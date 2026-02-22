"""
PDF Report Generator

Generates professional compliance reports using Jinja2 templates.
"""

from jinja2 import Template
from datetime import datetime
from typing import Dict, Any
import os

class ReportGenerator:
    """
    Service to generate professional PDF reports.
    
    Uses HTML templates + CSS for beautiful formatting.
    """
    
    REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @page { size: A4; margin: 0; }
        body { font-family: 'Inter', sans-serif; }
        .print-container { max-width: 210mm; margin: 0 auto; }
    </style>
</head>
<body class="bg-gray-100 p-8">
    <div class="print-container bg-white shadow-2xl rounded-lg overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-white">
            <div class="flex justify-between items-center">
                <div>
                    <div class="flex items-center mb-2">
                        <svg class="w-8 h-8 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6z"/>
                        </svg>
                        <h1 class="text-3xl font-bold">CloudGuardian</h1>
                    </div>
                    <h2 class="text-xl font-semibold opacity-90">Compliance Audit Report</h2>
                </div>
                <div class="text-right">
                    <p class="text-sm opacity-90">Report ID: {{ report_date }}</p>
                    <p class="text-sm opacity-90">Generated: {{ report_date }}</p>
                </div>
            </div>
        </div>

        <!-- Overall Score Banner -->
        <div class="bg-gradient-to-br from-indigo-50 to-purple-50 p-8 border-b border-gray-200">
            <div class="text-center">
                <p class="text-gray-600 text-sm font-medium uppercase tracking-wide">Overall Security Posture</p>
                <p class="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 my-4">
                    {{ overall_score }}%
                </p>
                <p class="text-gray-600">Across {{ framework_count }} Compliance Frameworks</p>
            </div>
        </div>

        <!-- Summary Stats -->
        <div class="grid grid-cols-3 gap-6 p-8 border-b border-gray-200">
            <div class="text-center p-6 bg-blue-50 rounded-lg">
                <p class="text-3xl font-bold text-blue-600">{{ total_findings }}</p>
                <p class="text-gray-600 text-sm mt-1">Total Findings</p>
            </div>
            <div class="text-center p-6 bg-green-50 rounded-lg">
                <p class="text-3xl font-bold text-green-600">{{ frameworks_passing }}</p>
                <p class="text-gray-600 text-sm mt-1">Frameworks Passing</p>
            </div>
            <div class="text-center p-6 bg-red-50 rounded-lg">
                <p class="text-3xl font-bold text-red-600">{{ frameworks_failing }}</p>
                <p class="text-gray-600 text-sm mt-1">Frameworks Failing</p>
            </div>
        </div>

        <!-- Frameworks Detail -->
        <div class="p-8">
            {% for name, framework in frameworks.items() %}
            <div class="mb-8 {% if not loop.last %}border-b border-gray-200 pb-8{% endif %}">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h3 class="text-2xl font-bold text-gray-800">{{ name }}</h3>
                        <p class="text-gray-600 mt-1">{{ framework.passed_controls }} of {{ framework.total_controls }} controls passing</p>
                    </div>
                    <div class="flex items-center">
                        <span class="text-4xl font-bold mr-4 {% if framework.status == 'PASS' %}text-green-600{% else %}text-red-600{% endif %}">
                            {{ framework.score }}%
                        </span>
                        <span class="px-4 py-2 rounded-full text-sm font-bold {% if framework.status == 'PASS' %}bg-green-100 text-green-700{% else %}bg-red-100 text-red-700{% endif %}">
                            {{ framework.status }}
                        </span>
                    </div>
                </div>

                {% if framework.failing_controls %}
                <div class="mb-6">
                    <h4 class="text-lg font-semibold text-red-700 mb-3 flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"/>
                        </svg>
                        Failing Controls
                    </h4>
                    <div class="overflow-hidden rounded-lg border border-red-200">
                        <table class="w-full">
                            <thead class="bg-red-50">
                                <tr>
                                    <th class="text-left py-3 px-4 text-red-700 font-semibold text-sm">Control ID</th>
                                    <th class="text-left py-3 px-4 text-red-700 font-semibold text-sm">Title</th>
                                    <th class="text-left py-3 px-4 text-red-700 font-semibold text-sm">Description</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white">
                                {% for control in framework.failing_controls %}
                                <tr class="border-t border-red-100">
                                    <td class="py-3 px-4"><code class="bg-red-50 px-2 py-1 rounded text-sm">{{ control.id }}</code></td>
                                    <td class="py-3 px-4 font-medium">{{ control.title }}</td>
                                    <td class="py-3 px-4 text-gray-600 text-sm">{{ control.description }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endif %}

                {% if framework.passing_controls %}
                <div>
                    <h4 class="text-lg font-semibold text-green-700 mb-3 flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/>
                        </svg>
                        Passing Controls
                    </h4>
                    <div class="grid grid-cols-2 gap-3">
                        {% for control in framework.passing_controls %}
                        <div class="flex items-center p-3 bg-green-50 rounded-lg border border-green-200">
                            <svg class="w-5 h-5 text-green-600 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                            </svg>
                            <div>
                                <code class="text-xs text-green-700 font-medium">{{ control.id }}</code>
                                <p class="text-sm text-gray-700">{{ control.title }}</p>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 p-8 border-t border-gray-200">
            <div class="flex items-center justify-between text-sm text-gray-600">
                <div>
                    <p class="font-semibold text-gray-800">CloudGuardian Security Platform</p>
                    <p class="mt-1">Automated security scanning and compliance reporting</p>
                </div>
                <div class="text-right">
                    <p>For support: security@cloudguardian.io</p>
                    <p class="mt-1">© 2024 CloudGuardian. All rights reserved.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    def __init__(self):
        """Initialize report generator"""
        self.template = Template(self.REPORT_TEMPLATE)
    
    def generate_html(self, compliance_data: Dict[str, Any]) -> str:
        """
        Generate HTML report.
        
        Args:
            compliance_data: Compliance summary from ComplianceMapper
        
        Returns:
            Rendered HTML string
        """
        frameworks = compliance_data['frameworks']
        
        context = {
            'report_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
            'overall_score': compliance_data['overall_score'],
            'framework_count': len(frameworks),
            'total_findings': compliance_data['total_findings'],
            'frameworks_passing': sum(1 for f in frameworks.values() if f['status'] == 'PASS'),
            'frameworks_failing': sum(1 for f in frameworks.values() if f['status'] == 'FAIL'),
            'frameworks': frameworks
        }
        
        return self.template.render(**context)
    
    def generate_pdf(
        self,
        compliance_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Generate PDF report.
        
        Args:
            compliance_data: Compliance summary
            output_path: Path to save PDF
        
        Returns:
            Path to generated PDF
        
        Note:
            Requires WeasyPrint: pip install weasyprint
            Alternative: pdfkit (requires wkhtmltopdf binary)
        """
        html_content = self.generate_html(compliance_data)
        
        try:
            from weasyprint import HTML
            
            HTML(string=html_content).write_pdf(output_path)
            return output_path
            
        except ImportError:
            # Fallback: save as HTML if WeasyPrint not installed
            html_output = output_path.replace('.pdf', '.html')
            
            with open(html_output, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"⚠️  WeasyPrint not installed. Saved as HTML: {html_output}")
            print("   Install with: pip install weasyprint")
            
            return html_output
    
    def save_html(
        self,
        compliance_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Save report as HTML (alternative to PDF).
        
        Args:
            compliance_data: Compliance summary
            output_path: Path to save HTML
        
        Returns:
            Path to saved file
        """
        html_content = self.generate_html(compliance_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
