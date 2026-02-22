"""
Compliance Mapping Service

Maps technical vulnerabilities to compliance framework controls.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ComplianceControl:
    """Represents a compliance control"""
    control_id: str
    framework: str
    title: str
    description: str
    status: str  # PASS, FAIL

class ComplianceMapper:
    """
    Service to map vulnerabilities to compliance frameworks.
    
    Translates technical findings into compliance language for auditors.
    """
    
    # Mapping of vulnerability types to compliance controls
    VULNERABILITY_TO_CONTROLS = {
        # S3 Security
        'S3_NO_ENCRYPTION': [
            'SOC2_CC6.1',  # Logical and Physical Access Controls
            'ISO27001_A.10.1.1',  # Cryptographic Controls
            'HIPAA_164.312',  # Technical Safeguards
            'PCI_DSS_3.4'  # Encryption of Cardholder Data
        ],
        'S3_PUBLIC_ACCESS': [
            'SOC2_CC6.1',
            'ISO27001_A.9.1.2',  # Access to Networks and Services
            'HIPAA_164.308',  # Administrative Safeguards
            'PCI_DSS_1.2'  # Firewall Configuration
        ],
        
        # Network Security
        'SECURITY_GROUP_OPEN': [
            'SOC2_CC6.6',  # Network Security
            'ISO27001_A.13.1.1',  # Network Controls
            'HIPAA_164.312',  # Technical Safeguards
            'PCI_DSS_1.3'  # Firewall Rules
        ],
        
        # Database Security
        'RDS_NO_ENCRYPTION': [
            'SOC2_CC6.1',
            'ISO27001_A.10.1.1',
            'HIPAA_164.312',
            'PCI_DSS_3.4'
        ],
        'RDS_PUBLIC_ACCESS': [
            'SOC2_CC6.1',
            'ISO27001_A.9.1.2',
            'HIPAA_164.308'
        ],
        
        # Secrets & Credentials
        'SECRET_LEAK': [
            'SOC2_CC6.1',
            'ISO27001_A.9.4.3',  # Password Management
            'HIPAA_164.308',
            'PCI_DSS_8.2'  # User Authentication
        ],
        
        # Monitoring & Logging
        'NO_CLOUDTRAIL': [
            'SOC2_CC7.2',  # System Monitoring
            'ISO27001_A.12.4.1',  # Event Logging
            'HIPAA_164.312',
            'PCI_DSS_10.1'  # Audit Trails
        ]
    }
    
    # Control definitions
    CONTROLS = {
        # SOC2
        'SOC2_CC6.1': {
            'framework': 'SOC2',
            'title': 'Logical and Physical Access Controls',
            'description': 'Entity implements controls to protect against unauthorized access'
        },
        'SOC2_CC6.6': {
            'framework': 'SOC2',
            'title': 'Network Security',
            'description': 'Entity implements network security measures'
        },
        'SOC2_CC7.2': {
            'framework': 'SOC2',
            'title': 'System Monitoring',
            'description': 'Entity monitors system components'
        },
        
        # ISO27001
        'ISO27001_A.10.1.1': {
            'framework': 'ISO27001',
            'title': 'Cryptographic Controls',
            'description': 'Policy on the use of cryptographic controls'
        },
        'ISO27001_A.9.1.2': {
            'framework': 'ISO27001',
            'title': 'Access to Networks and Services',
            'description': 'Users are only provided access to networks and services'
        },
        'ISO27001_A.13.1.1': {
            'framework': 'ISO27001',
            'title': 'Network Controls',
            'description': 'Networks are managed and controlled'
        },
        'ISO27001_A.9.4.3': {
            'framework': 'ISO27001',
            'title': 'Password Management System',
            'description': 'Secure password management system'
        },
        'ISO27001_A.12.4.1': {
            'framework': 'ISO27001',
            'title': 'Event Logging',
            'description': 'Event logs recording activities are produced and retained'
        },
        
        # HIPAA
        'HIPAA_164.312': {
            'framework': 'HIPAA',
            'title': 'Technical Safeguards',
            'description': 'Implement technical policies and procedures'
        },
        'HIPAA_164.308': {
            'framework': 'HIPAA',
            'title': 'Administrative Safeguards',
            'description': 'Implement administrative safeguards'
        },
        
        # PCI DSS
        'PCI_DSS_3.4': {
            'framework': 'PCI_DSS',
            'title': 'Encryption of Cardholder Data',
            'description': 'Render PAN unreadable anywhere it is stored'
        },
        'PCI_DSS_1.2': {
            'framework': 'PCI_DSS',
            'title': 'Firewall Configuration',
            'description': 'Build firewall configuration that restricts connections'
        },
        'PCI_DSS_1.3': {
            'framework': 'PCI_DSS',
            'title': 'Firewall Rules',
            'description': 'Prohibit direct public access'
        },
        'PCI_DSS_8.2': {
            'framework': 'PCI_DSS',
            'title': 'User Authentication',
            'description': 'Assign unique ID to each user'
        },
        'PCI_DSS_10.1': {
            'framework': 'PCI_DSS',
            'title': 'Audit Trails',
            'description': 'Implement audit trails to link all access'
        }
    }
    
    def __init__(self):
        """Initialize mapper"""
        pass
    
    def map_vulnerability_to_controls(
        self,
        vulnerability_type: str
    ) -> List[str]:
        """
        Get compliance controls for a vulnerability type.
        
        Args:
            vulnerability_type: Type of vulnerability
        
        Returns:
            List of control IDs
        """
        return self.VULNERABILITY_TO_CONTROLS.get(vulnerability_type, [])
    
    def generate_compliance_summary(
        self,
        findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate compliance summary from vulnerability findings.
        
        Args:
            findings: List of vulnerability findings
        
        Returns:
            Compliance summary by framework
        """
        # Track which controls failed
        failing_controls = set()
        all_controls = set()
        
        for finding in findings:
            vuln_type = finding.get('rule_id') or finding.get('type')
            controls = self.map_vulnerability_to_controls(vuln_type)
            
            for control_id in controls:
                all_controls.add(control_id)
                if finding.get('severity') in ['CRITICAL', 'HIGH']:
                    failing_controls.add(control_id)
        
        # Group by framework
        frameworks = {}
        
        for framework in ['SOC2', 'ISO27001', 'HIPAA', 'PCI_DSS']:
            framework_controls = {
                ctrl_id: ctrl_info 
                for ctrl_id, ctrl_info in self.CONTROLS.items()
                if ctrl_info['framework'] == framework
            }
            
            failing = [
                ctrl_id for ctrl_id in framework_controls
                if ctrl_id in failing_controls
            ]
            
            passing = [
                ctrl_id for ctrl_id in framework_controls
                if ctrl_id in all_controls and ctrl_id not in failing_controls
            ]
            
            total = len(framework_controls)
            passed = total - len(failing)
            score = int((passed / total) * 100) if total > 0 else 100
            
            status = 'PASS' if score >= 80 else 'FAIL'
            
            frameworks[framework] = {
                'status': status,
                'score': score,
                'failing_controls': [
                    {
                        'id': ctrl_id,
                        'title': self.CONTROLS[ctrl_id]['title'],
                        'description': self.CONTROLS[ctrl_id]['description']
                    }
                    for ctrl_id in failing
                ],
                'passing_controls': [
                    {
                        'id': ctrl_id,
                        'title': self.CONTROLS[ctrl_id]['title']
                    }
                    for ctrl_id in passing
                ],
                'total_controls': total,
                'passed_controls': passed
            }
        
        return {
            'generated_at': datetime.utcnow().isoformat(),
            'overall_score': sum(f['score'] for f in frameworks.values()) // len(frameworks),
            'frameworks': frameworks,
            'total_findings': len(findings)
        }
