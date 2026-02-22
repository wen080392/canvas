"""
Example usage of Compliance Reporting
"""

from app.services.compliance_service import ComplianceMapper
from app.services.report_generator import ReportGenerator

def example_compliance_report():
    """Generate a sample compliance report"""
    
    # Sample findings (from security scans)
    findings = [
        {
            'rule_id': 'S3_NO_ENCRYPTION',
            'severity': 'CRITICAL',
            'resource': 'my-data-bucket'
        },
        {
            'rule_id': 'SECURITY_GROUP_OPEN',
            'severity': 'HIGH',
            'resource': 'web-sg'
        },
        {
            'rule_id': 'SECRET_LEAK',
            'severity': 'CRITICAL',
            'resource': 'config.py'
        }
    ]
    
    # Generate compliance summary
    mapper = ComplianceMapper()
    compliance_data = mapper.generate_compliance_summary(findings)
    
    print("=== Compliance Summary ===")
    print(f"   Overall Score: {compliance_data['overall_score']}%")
    print(f"   Total Findings: {compliance_data['total_findings']}")
    
    for framework, data in compliance_data['frameworks'].items():
        print(f"\n   {framework}: {data['score']}% - {data['status']}")
        print(f"      Failing: {len(data['failing_controls'])}")
        print(f"      Passing: {len(data['passing_controls'])}")
    
    # Generate PDF report
    generator = ReportGenerator()
    
    # Save as HTML (WeasyPrint not required)
    html_path = "compliance_report.html"
    generator.save_html(compliance_data, html_path)
    print(f"\n[SUCCESS] HTML Report saved: {html_path}")
    
    # Optionally generate PDF (requires WeasyPrint)
    # pdf_path = "compliance_report.pdf"
    # generator.generate_pdf(compliance_data, pdf_path)
    # print(f"✅ PDF Report saved: {pdf_path}")

if __name__ == "__main__":
    example_compliance_report()
