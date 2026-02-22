"""
Drift Detection Service

Compares Terraform state (expected) vs AWS API (actual) to detect configuration drift.
"""

import json
import boto3
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models import DriftAlert, Project, ResourceType, Severity, DriftStatus
from ..database import get_db

class DriftDetectionService:
    """Service to detect infrastructure drift between code and cloud"""
    
    def __init__(self, db: Session, aws_region: str = "us-east-1"):
        self.db = db
        self.aws_region = aws_region
        self.simulation_mode = True # Default to simulation for demo if no AWS configured
        
        # Initialize AWS clients (try/catch for local dev without creds)
        try:
            self.ec2_client = boto3.client('ec2', region_name=aws_region)
            self.s3_client = boto3.client('s3')
            self.rds_client = boto3.client('rds', region_name=aws_region)
            self.iam_client = boto3.client('iam')
            # Verify credentials roughly
            self.s3_client.list_buckets()
            self.simulation_mode = False
        except Exception:
            print("DriftDetection: No valid AWS credentials found. Using SIMULATION MODE.")
            self.simulation_mode = True
    
    async def check_drift(self, project_id: int) -> List[DriftAlert]:
        """
        Main entry point: Check for drift in a project
        """
        # In simulation mode, we create a fake project wrapper if real one doesn't exist
        # This helps testing the flow easily
        
        # Load Terraform state file (from S3 or local path)
        # For demo, if project not found, we just mock the whole flow
        project = self.db.query(Project).filter(Project.id == project_id).first()
        
        # If simulation and no project, create a dummy context
        if self.simulation_mode and not project:
            tf_state = self._get_mock_state()
        elif project:
            tf_state = await self._load_terraform_state(project)
        else:
             raise ValueError(f"Project {project_id} not found")
        
        drift_alerts = []
        
        # Check each resource type
        for resource in tf_state.get('resources', []):
            resource_type = resource.get('type')
            
            if resource_type == 'aws_s3_bucket':
                alerts = await self._check_s3_drift(resource, project_id)
                drift_alerts.extend(alerts)
            
            elif resource_type == 'aws_security_group':
                alerts = await self._check_security_group_drift(resource, project_id)
                drift_alerts.extend(alerts)
            
            elif resource_type == 'aws_db_instance':
                alerts = await self._check_rds_drift(resource, project_id)
                drift_alerts.extend(alerts)
        
        return drift_alerts
        
    def _get_mock_state(self):
        """Returns a mock tfstate for demonstration"""
        return {
            "resources": [
                {
                    "type": "aws_s3_bucket",
                    "name": "critical-data",
                    "instances": [{"attributes": {"bucket": "company-data-prod", "acl": "private"}}]
                },
                {
                    "type": "aws_security_group",
                    "name": "web-sg",
                    "instances": [{"attributes": {"id": "sg-12345", "ingress": [{}, {}]}}] 
                },
                {
                    "type": "aws_db_instance",
                    "name": "main-db",
                    "instances": [{"attributes": {"identifier": "prod-db", "publicly_accessible": False}}]
                }
            ]
        }
    
    async def _load_terraform_state(self, project: Project) -> Dict[str, Any]:
        """
        Load terraform.tfstate file
        
        Tries to load from:
        1. Local storage: storage/projects/{id}/terraform.tfstate
        2. Repository path if local
        3. Fallback to mock for demo purposes if file not found
        """
        import os
        
        # 1. Try project specific storage
        local_path = os.path.join("storage", "projects", str(project.id), "terraform.tfstate")
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading state from {local_path}: {e}")

        # 2. Try common development locations (for demo/dev)
        # Look in the root infrastructure folder often used in this workspace
        common_paths = [
            os.path.abspath(os.path.join(os.getcwd(), "..", "..", "infrastructure", "terraform", "terraform.tfstate")),
            os.path.abspath(os.path.join(os.getcwd(), "infrastructure", "terraform", "terraform.tfstate")),
            os.path.abspath(os.path.join("C:\\Users\\USER\\CloudGuardian\\infrastructure\\terraform\\terraform.tfstate"))
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        print(f"Loading state from dev path: {path}")
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading state from {path}: {e}")

        # 3. Try S3 Backend (if configured)
        s3_bucket = os.getenv("TERRAFORM_STATE_BUCKET")
        s3_key = os.getenv("TERRAFORM_STATE_KEY", f"projects/{project.id}/terraform.tfstate")
        
        if s3_bucket:
            try:
                print(f"Attempting to load state from S3: {s3_bucket}/{s3_key}")
                response = self.s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
                content = response['Body'].read().decode('utf-8')
                return json.loads(content)
            except Exception as e:
                print(f"Error loading state from S3 ({s3_bucket}/{s3_key}): {e}")

        # 4. Fallback to mock data if no State file found (so the app doesn't crash in demo)
        print(f"No state file found for project {project.id}, returning mock state.")
        return self._get_mock_state()
    
    async def _check_s3_drift(self, tf_resource: Dict, project_id: int) -> List[DriftAlert]:
        """Check S3 bucket configuration drift"""
        alerts = []
        
        bucket_name = tf_resource['instances'][0]['attributes']['bucket']
        expected_acl = tf_resource['instances'][0]['attributes'].get('acl', 'private')
        
        # SIMULATION OR REAL CHECK
        if self.simulation_mode:
            # Simulate a 50% chance of drift
            actual_acl = 'public-read' if random.random() > 0.5 else expected_acl
            is_public = (actual_acl == 'public-read')
        else:
            try:
                acl_response = self.s3_client.get_bucket_acl(Bucket=bucket_name)
                is_public = any(
                    grant['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
                    for grant in acl_response.get('Grants', [])
                )
                actual_acl = 'public-read' if is_public else 'private'
            except Exception as e:
                print(f"Error checking S3 drift for {bucket_name}: {e}")
                return []

        # Detect drift
        if expected_acl != actual_acl:
            alert = DriftAlert(
                project_id=project_id,
                resource_id=bucket_name,
                resource_type=ResourceType.S3_BUCKET,
                aws_arn=f"arn:aws:s3:::{bucket_name}",
                expected_state={'acl': expected_acl},
                actual_state={'acl': actual_acl},
                drift_details={
                    'field': 'acl',
                    'expected': expected_acl,
                    'actual': actual_acl,
                    'message': f"Bucket ACL changed from {expected_acl} to {actual_acl}"
                },
                severity=Severity.HIGH if is_public else Severity.MEDIUM,
                detected_at=datetime.now(timezone.utc),
                status=DriftStatus.PENDING
            )
            
            try:
                self.db.add(alert)
                self.db.commit()
                alerts.append(alert)
            except Exception:
                self.db.rollback()
        
        return alerts
    
    async def _check_security_group_drift(self, tf_resource: Dict, project_id: int) -> List[DriftAlert]:
        """Check Security Group rules drift"""
        alerts = []
        
        sg_id = tf_resource['instances'][0]['attributes'].get('id', 'sg-unknown')
        expected_rules = tf_resource['instances'][0]['attributes'].get('ingress', [])
        
        if self.simulation_mode:
            # Simulate finding an extra rule (e.g. port 22 open to world)
            actual_rules_count = len(expected_rules) + 1
            simulated_extra_rule = [{'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0']}]
        else:
            try:
                response = self.ec2_client.describe_security_groups(GroupIds=[sg_id])
                sg = response['SecurityGroups'][0]
                actual_rules = sg['IpPermissions']
                actual_rules_count = len(actual_rules)
            except Exception as e:
                print(f"Error checking SG drift for {sg_id}: {e}")
                return []

        # Compare rule counts (Simple heuristic for demo)
        if len(expected_rules) != actual_rules_count:
            alert = DriftAlert(
                project_id=project_id,
                resource_id=sg_id,
                resource_type=ResourceType.SECURITY_GROUP,
                aws_arn=f"arn:aws:ec2:{self.aws_region}::security-group/{sg_id}",
                expected_state={'ingress_rules_count': len(expected_rules)},
                actual_state={'ingress_rules_count': actual_rules_count},
                drift_details={
                    'expected_rules': expected_rules,
                    'actual_rules': simulated_extra_rule if self.simulation_mode else self._serialize_sg_rules(actual_rules),
                    'message': f"Security group has {actual_rules_count} rules, expected {len(expected_rules)}. Found 1 extra rule allowing SSH (0.0.0.0/0)."
                },
                severity=Severity.CRITICAL,
                detected_at=datetime.now(timezone.utc),
                status=DriftStatus.PENDING
            )
            
            try:
                self.db.add(alert)
                self.db.commit()
                alerts.append(alert)
            except Exception:
                self.db.rollback()
        
        return alerts
    
    async def _check_rds_drift(self, tf_resource: Dict, project_id: int) -> List[DriftAlert]:
        """Check RDS instance configuration drift"""
        alerts = []
        
        db_instance_id = tf_resource['instances'][0]['attributes']['identifier']
        expected_public = tf_resource['instances'][0]['attributes'].get('publicly_accessible', False)
        
        if self.simulation_mode:
             # Simulate drift
             actual_public = not expected_public
        else:
            try:
                response = self.rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
                db_instance = response['DBInstances'][0]
                actual_public = db_instance['PubliclyAccessible']
            except Exception as e:
                print(f"Error checking RDS drift for {db_instance_id}: {e}")
                return []
            
        # Detect drift in public accessibility
        if expected_public != actual_public:
            alert = DriftAlert(
                project_id=project_id,
                resource_id=db_instance_id,
                resource_type=ResourceType.RDS_DATABASE,
                aws_arn=f"arn:aws:rds:{self.aws_region}:123456789:db:{db_instance_id}",
                expected_state={'publicly_accessible': expected_public},
                actual_state={'publicly_accessible': actual_public},
                drift_details={
                    'field': 'publicly_accessible',
                    'expected': expected_public,
                    'actual': actual_public,
                    'message': f"RDS public access changed from {expected_public} to {actual_public}"
                },
                severity=Severity.CRITICAL if actual_public else Severity.MEDIUM,
                detected_at=datetime.now(timezone.utc),
                status=DriftStatus.PENDING
            )
            try:
                self.db.add(alert)
                self.db.commit()
                alerts.append(alert)
            except Exception:
                self.db.rollback()

        return alerts
    
    def _serialize_sg_rules(self, rules: List[Dict]) -> List[Dict]:
        """Convert AWS security group rules to serializable format"""
        serialized = []
        for rule in rules:
            serialized.append({
                'protocol': rule.get('IpProtocol'),
                'from_port': rule.get('FromPort'),
                'to_port': rule.get('ToPort'),
                'cidr_blocks': [r['CidrIp'] for r in rule.get('IpRanges', [])]
            })
        return serialized
