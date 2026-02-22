from typing import List, Dict, Any
from .graph_service import InfrastructureGraphService
from .compliance_service import ComplianceMapper, ComplianceScanner

class ComplianceReportService:
    """
    Service to generate real compliance reports by scanning infrastructure.
    """
    
    def __init__(self):
        self.graph_service = InfrastructureGraphService()
        self.mapper = ComplianceMapper()
        self.scanner = ComplianceScanner()

    async def get_compliance_overview(self, terraform_content: str = None) -> List[Dict[str, Any]]:
        """
        Get high-level compliance status by scanning real/mock infrastructure.
        """
        if not terraform_content:
            # Default fallback for demo if no content provided
            terraform_content = """
            resource "aws_s3_bucket" "data_bucket" {
              bucket = "my-data-bucket"
              acl    = "public-read" # BAD: Public Access
            }
            
            resource "aws_db_instance" "default" {
              allocated_storage    = 10
              storage_encrypted    = false # BAD: No Encryption
              engine               = "mysql"
              instance_class       = "db.t3.micro"
            }
            """
            
        # 1. Parse Terraform to get resources
        graph_data = await self.graph_service.parse_terraform(terraform_content)
        resources = graph_data.get('nodes', [])
        
        # 2. Scan resources for technical findings
        findings = self.scanner.scan(resources)
        
        # 3. Map findings to compliance frameworks (SOC2, etc.)
        report = self.mapper.generate_compliance_summary(findings)
        
        # 4. Transform to frontend format
        overview = []
        frameworks_data = report.get('frameworks', {})
        
        framework_meta = {
            "SOC2": {"name": "SOC 2 Type II", "desc": "Security, Availability & Confidentiality"},
            "ISO27001": {"name": "ISO/IEC 27001:2013", "desc": "Information Security Management"},
            "GDPR": {"name": "GDPR", "desc": "General Data Protection Regulation"},
            "HIPAA": {"name": "HIPAA", "desc": "Health Insurance Portability and Accountability Act"},
             "PCI_DSS": {"name": "PCI DSS", "desc": "Payment Card Industry Data Security Standard"}
        }
        
        for key, data in frameworks_data.items():
            meta = framework_meta.get(key, {"name": key, "desc": "Security Framework"})
            
            # Decide status based on score
            score = data['score']
            status = "COMPLIANT" if score >= 90 else "AT_RISK" if score >= 70 else "NON_COMPLIANT"
            
            overview.append({
                "id": key,
                "name": meta["name"],
                "description": meta["desc"],
                "score": score,
                "status": status,
                "controls_count": data['total_controls'],
                "passing_count": data['passed_controls'],
                "failing_controls": data['failing_controls']
            })
            
        return overview

    async def get_framework_details(self, framework_id: str, terraform_content: str = None) -> Dict[str, Any]:
        """
        Get detailed controls for a specific framework.
        """
        overview = await self.get_compliance_overview(terraform_content)
        for fw in overview:
            if fw['id'] == framework_id:
                return fw
        return {}
