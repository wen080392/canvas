"""
Drift Detection Service

Compares Terraform state (expected) vs AWS API (actual) to detect configuration drift.
"""

import json
import boto3
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import DriftAlert, Project, ResourceType, Severity, DriftStatus
from ..database import get_db

class DriftDetectionService:
    """Service to detect infrastructure drift between code and cloud"""
    
    def __init__(self, db: Session, aws_region: str = "us-east-1"):
        self.db = db
        self.aws_region = aws_region
        
        # Initialize AWS clients
        self.ec2_client = boto3.client('ec2', region_name=aws_region)
        self.s3_client = boto3.client('s3')
        self.rds_client = boto3.client('rds', region_name=aws_region)
        self.iam_client = boto3.client('iam')
    
    async def check_drift(self, project_id: int) -> List[DriftAlert]:
        """
        Main entry point: Check for drift in a project
        
        Args:
            project_id: ID of the project to check
            
        Returns:
            List of detected drift alerts
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # TODO: Load Terraform state file (from S3 or local path)
        tf_state = await self._load_terraform_state(project)
        
        drift_alerts = []
        
        # Check each resource type
        for resource in tf_state.get('resources', []):
            resource_type = resource.get('type')
            resource_name = resource.get('name')
            
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
    
    async def _load_terraform_state(self, project: Project) -> Dict[str, Any]:
        """
        Load terraform.tfstate file
        
        In production, this would:
        1. Check if state is in S3 backend
        2. Clone the git repo if needed
        3. Parse the state file
        
        For now, returns mock data
        """
        # TODO: Implement actual state loading
        return {
            "version": 4,
            "terraform_version": "1.5.0",
            "resources": []
        }
    
    async def _check_s3_drift(self, tf_resource: Dict, project_id: int) -> List[DriftAlert]:
        """Check S3 bucket configuration drift"""
        alerts = []
        
        bucket_name = tf_resource['instances'][0]['attributes']['bucket']
        expected_acl = tf_resource['instances'][0]['attributes'].get('acl', 'private')
        
        try:
            # Get actual bucket ACL from AWS
            acl_response = self.s3_client.get_bucket_acl(Bucket=bucket_name)
            
            # Check for public access
            is_public = any(
                grant['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
                for grant in acl_response.get('Grants', [])
            )
            
            actual_acl = 'public-read' if is_public else 'private'
            
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
                    detected_at=datetime.utcnow(),
                    status=DriftStatus.PENDING
                )
                
                self.db.add(alert)
                self.db.commit()
                alerts.append(alert)
        
        except Exception as e:
            print(f"Error checking S3 drift for {bucket_name}: {e}")
        
        return alerts
    
    async def _check_security_group_drift(self, tf_resource: Dict, project_id: int) -> List[DriftAlert]:
        """Check Security Group rules drift"""
        alerts = []
        
        sg_id = tf_resource['instances'][0]['attributes']['id']
        expected_rules = tf_resource['instances'][0]['attributes'].get('ingress', [])
        
        try:
            # Get actual security group from AWS
            response = self.ec2_client.describe_security_groups(GroupIds=[sg_id])
            sg = response['SecurityGroups'][0]
            actual_rules = sg['IpPermissions']
            
            # Compare rule counts
            if len(expected_rules) != len(actual_rules):
                alert = DriftAlert(
                    project_id=project_id,
                    resource_id=sg_id,
                    resource_type=ResourceType.SECURITY_GROUP,
                    aws_arn=f"arn:aws:ec2:{self.aws_region}::security-group/{sg_id}",
                    expected_state={'ingress_rules_count': len(expected_rules)},
                    actual_state={'ingress_rules_count': len(actual_rules)},
                    drift_details={
                        'expected_rules': expected_rules,
                        'actual_rules': self._serialize_sg_rules(actual_rules),
                        'message': f"Security group has {len(actual_rules)} rules, expected {len(expected_rules)}"
                    },
                    severity=Severity.CRITICAL,
                    detected_at=datetime.utcnow(),
                    status=DriftStatus.PENDING
                )
                
                self.db.add(alert)
                self.db.commit()
                alerts.append(alert)
        
        except Exception as e:
            print(f"Error checking SG drift for {sg_id}: {e}")
        
        return alerts
    
    async def _check_rds_drift(self, tf_resource: Dict, project_id: int) -> List[DriftAlert]:
        """Check RDS instance configuration drift"""
        alerts = []
        
        db_instance_id = tf_resource['instances'][0]['attributes']['identifier']
        expected_public = tf_resource['instances'][0]['attributes'].get('publicly_accessible', False)
        
        try:
            # Get actual RDS instance from AWS
            response = self.rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
            db_instance = response['DBInstances'][0]
            actual_public = db_instance['PubliclyAccessible']
            
            # Detect drift in public accessibility
            if expected_public != actual_public:
                alert = DriftAlert(
                    project_id=project_id,
                    resource_id=db_instance_id,
                    resource_type=ResourceType.RDS_DATABASE,
                    aws_arn=db_instance['DBInstanceArn'],
                    expected_state={'publicly_accessible': expected_public},
                    actual_state={'publicly_accessible': actual_public},
                    drift_details={
                        'field': 'publicly_accessible',
                        'expected': expected_public,
                        'actual': actual_public,
                        'message': f"RDS public access changed from {expected_public} to {actual_public}"
                    },
                    severity=Severity.CRITICAL if actual_public else Severity.MEDIUM,
                    detected_at=datetime.utcnow(),
                    status=DriftStatus.PENDING
                )
                
                self.db.add(alert)
                self.db.commit()
                alerts.append(alert)
        
        except Exception as e:
            print(f"Error checking RDS drift for {db_instance_id}: {e}")
        
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
