#!/usr/bin/env python3
"""
CloudGuardian CLI - Command-line interface for security scanning
Scans files, directories, and generates comprehensive security reports
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from requests.auth import HTTPBearerAuth
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Result from a single file scan"""
    filename: str
    filepath: str
    file_type: str
    scan_type: str  # 'secrets' or 'terraform' or 'compliance'
    severity: str   # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    findings: List[Dict[str, Any]]
    finding_count: int
    scan_duration: float
    status: str     # 'success', 'error', 'skipped'
    error_message: Optional[str] = None


class CloudGuardianConfig:
    """Configuration management for CLI"""

    def __init__(self, api_url: str = None, api_token: str = None, 
                 config_file: str = None):
        """Initialize configuration from arguments, env, or config file"""
        self.api_url = api_url or os.getenv('CLOUDGUARDIAN_API_URL', 'http://localhost:8000')
        self.api_token = api_token or os.getenv('CLOUDGUARDIAN_API_TOKEN', '')
        self.config_file = config_file or os.path.expanduser('~/.cloudguardian/config.json')
        
        # Load from config file if exists
        if os.path.exists(self.config_file):
            self._load_config_file()

    def _load_config_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.api_url = config.get('api_url', self.api_url)
                self.api_token = config.get('api_token', self.api_token)
                logger.debug(f"Loaded config from {self.config_file}")
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}")

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.api_token:
            logger.error("❌ API token not configured")
            logger.error("   Set CLOUDGUARDIAN_API_TOKEN environment variable or use --token")
            return False
        
        if not self.api_url:
            logger.error("❌ API URL not configured")
            return False
        
        return True

    def save(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config = {
                'api_url': self.api_url,
                'api_token': self.api_token
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")


class CloudGuardianScanner:
    """Scanner client for CloudGuardian API"""

    def __init__(self, config: CloudGuardianConfig):
        """Initialize scanner with configuration"""
        self.config = config
        self.session = requests.Session()
        self.session.auth = HTTPBearerAuth(config.api_token)
        self.headers = {'Content-Type': 'application/json'}

    def scan_file(self, filepath: str, scan_type: str = 'secrets') -> ScanResult:
        """Scan a single file"""
        import time
        start_time = time.time()
        
        try:
            # Read file
            if not os.path.exists(filepath):
                return ScanResult(
                    filename=os.path.basename(filepath),
                    filepath=filepath,
                    file_type=self._get_file_type(filepath),
                    scan_type=scan_type,
                    severity='UNKNOWN',
                    findings=[],
                    finding_count=0,
                    scan_duration=0,
                    status='error',
                    error_message=f"File not found: {filepath}"
                )

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Skip empty files
            if not content.strip():
                return ScanResult(
                    filename=os.path.basename(filepath),
                    filepath=filepath,
                    file_type=self._get_file_type(filepath),
                    scan_type=scan_type,
                    severity='LOW',
                    findings=[],
                    finding_count=0,
                    scan_duration=time.time() - start_time,
                    status='skipped',
                    error_message='File is empty'
                )

            # Call API
            endpoint = f"{self.config.api_url}/{scan_type}/scan"
            response = self.session.post(
                endpoint,
                json={'content': content, 'filename': filepath},
                headers=self.headers,
                timeout=30
            )

            if response.status_code != 200:
                return ScanResult(
                    filename=os.path.basename(filepath),
                    filepath=filepath,
                    file_type=self._get_file_type(filepath),
                    scan_type=scan_type,
                    severity='UNKNOWN',
                    findings=[],
                    finding_count=0,
                    scan_duration=time.time() - start_time,
                    status='error',
                    error_message=f"API error: {response.status_code} - {response.text}"
                )

            data = response.json()
            findings = data.get('secrets', data.get('findings', []))
            severity = self._max_severity(findings)

            return ScanResult(
                filename=os.path.basename(filepath),
                filepath=filepath,
                file_type=self._get_file_type(filepath),
                scan_type=scan_type,
                severity=severity,
                findings=findings,
                finding_count=len(findings),
                scan_duration=time.time() - start_time,
                status='success'
            )

        except Exception as e:
            logger.error(f"Error scanning {filepath}: {e}")
            return ScanResult(
                filename=os.path.basename(filepath),
                filepath=filepath,
                file_type=self._get_file_type(filepath),
                scan_type=scan_type,
                severity='UNKNOWN',
                findings=[],
                finding_count=0,
                scan_duration=time.time() - start_time,
                status='error',
                error_message=str(e)
            )

    def scan_directory(self, directory: str, patterns: List[str] = None,
                      exclude_patterns: List[str] = None,
                      max_workers: int = 4,
                      scan_type: str = 'secrets') -> List[ScanResult]:
        """Scan all files in a directory"""
        if patterns is None:
            patterns = ['*.tf', '*.py', '*.js', '*.ts', '*.json', '*.env', '*.yml', '*.yaml']
        if exclude_patterns is None:
            exclude_patterns = ['node_modules/*', '.git/*', '__pycache__/*', '.venv/*', 'venv/*']

        files_to_scan = self._find_files(directory, patterns, exclude_patterns)
        logger.info(f"Found {len(files_to_scan)} files to scan in {directory}")

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.scan_file, f, scan_type): f for f in files_to_scan}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    self._log_scan_result(result)
                except Exception as e:
                    logger.error(f"Error in thread: {e}")

        return results

    def _find_files(self, directory: str, patterns: List[str],
                   exclude_patterns: List[str]) -> List[str]:
        """Find files matching patterns in directory"""
        from fnmatch import fnmatch
        
        files = []
        for root, dirs, filenames in os.walk(directory):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(
                fnmatch(os.path.join(root, d), exc) for exc in exclude_patterns
            )]

            for filename in filenames:
                filepath = os.path.join(root, filename)
                
                # Check if matches include patterns
                if any(fnmatch(filename, pat) for pat in patterns):
                    # Check if not excluded
                    if not any(fnmatch(filepath, exc) for exc in exclude_patterns):
                        files.append(filepath)

        return files

    @staticmethod
    def _get_file_type(filepath: str) -> str:
        """Get file type from extension"""
        ext = os.path.splitext(filepath)[1].lower()
        type_map = {
            '.tf': 'terraform',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.json': 'json',
            '.env': 'env',
            '.yml': 'yaml',
            '.yaml': 'yaml'
        }
        return type_map.get(ext, 'unknown')

    @staticmethod
    def _max_severity(findings: List[Dict]) -> str:
        """Get maximum severity from findings"""
        if not findings:
            return 'LOW'
        
        severities = [f.get('severity', 'LOW') for f in findings]
        priority = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        return min(severities, key=lambda x: priority.get(x, 99))

    @staticmethod
    def _log_scan_result(result: ScanResult):
        """Log scan result with appropriate color"""
        status_icon = {
            'success': '✓',
            'error': '✗',
            'skipped': '⊘'
        }
        icon = status_icon.get(result.status, '?')
        
        if result.status == 'error':
            logger.error(f"{icon} {result.filename}: {result.error_message}")
        elif result.status == 'skipped':
            logger.warning(f"{icon} {result.filename}: {result.error_message}")
        elif result.finding_count > 0:
            logger.warning(f"{icon} {result.filename}: {result.finding_count} findings ({result.severity})")
        else:
            logger.info(f"{icon} {result.filename}: clean")


class ReportGenerator:
    """Generate reports from scan results"""

    @staticmethod
    def generate_json_report(results: List[ScanResult], output_file: str = None) -> str:
        """Generate JSON report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(results),
            'successful_scans': len([r for r in results if r.status == 'success']),
            'failed_scans': len([r for r in results if r.status == 'error']),
            'total_findings': sum(r.finding_count for r in results),
            'severity_distribution': ReportGenerator._get_severity_distribution(results),
            'results': [asdict(r) for r in results]
        }

        json_str = json.dumps(report, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_str)
            logger.info(f"✅ JSON report saved to {output_file}")

        return json_str

    @staticmethod
    def generate_html_report(results: List[ScanResult], output_file: str = None) -> str:
        """Generate HTML report"""
        severity_colors = {
            'CRITICAL': '#dc2626',
            'HIGH': '#ea580c',
            'MEDIUM': '#eab308',
            'LOW': '#3b82f6',
            'UNKNOWN': '#6b7280'
        }

        total_findings = sum(r.finding_count for r in results)
        severity_dist = ReportGenerator._get_severity_distribution(results)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudGuardian Scan Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .timestamp {{ opacity: 0.9; font-size: 0.9em; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #6b7280; font-size: 0.9em; margin-top: 5px; }}
        .severity-bar {{ display: flex; gap: 10px; margin-top: 15px; }}
        .severity-item {{ flex: 1; text-align: center; padding: 10px; border-radius: 4px; color: white; font-weight: bold; }}
        .results-section {{ background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .section-title {{ background: #f3f4f6; padding: 15px 20px; border-bottom: 1px solid #e5e7eb; font-weight: bold; }}
        .result-item {{ padding: 15px 20px; border-bottom: 1px solid #e5e7eb; display: flex; align-items: center; justify-content: space-between; }}
        .result-item:last-child {{ border-bottom: none; }}
        .result-status {{ padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }}
        .status-success {{ background: #dcfce7; color: #166534; }}
        .status-error {{ background: #fee2e2; color: #991b1b; }}
        .status-skipped {{ background: #fef3c7; color: #92400e; }}
        .severity-badge {{ padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.85em; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ text-align: left; padding: 12px; }}
        th {{ background: #f3f4f6; border-bottom: 2px solid #e5e7eb; }}
        tr:nth-child(even) {{ background: #f9fafb; }}
        footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ CloudGuardian Security Report</h1>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(results)}</div>
                <div class="stat-label">Files Scanned</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_findings}</div>
                <div class="stat-label">Total Findings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len([r for r in results if r.status == 'success'])}</div>
                <div class="stat-label">Successful Scans</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len([r for r in results if r.status == 'error'])}</div>
                <div class="stat-label">Failed Scans</div>
            </div>
        </div>

        <div class="severity-bar">
            {"".join(f'<div class="severity-item" style="background: {severity_colors.get(s, severity_colors[\"UNKNOWN\"])}; flex: {severity_dist.get(s, 0)};"><strong>{s}</strong><br/>{severity_dist.get(s, 0)}</div>' for s in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])}
        </div>

        <div class="results-section" style="margin-top: 30px;">
            <div class="section-title">📋 Scan Results</div>
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Type</th>
                        <th>Findings</th>
                        <th>Severity</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(f'''
                    <tr>
                        <td>{r.filename}</td>
                        <td>{r.file_type}</td>
                        <td>{r.finding_count}</td>
                        <td><span class="severity-badge" style="background: {severity_colors.get(r.severity, severity_colors['UNKNOWN'])}">{r.severity}</span></td>
                        <td><span class="result-status status-{r.status}">{r.status.upper()}</span></td>
                    </tr>
                    ''' for r in results)}
                </tbody>
            </table>
        </div>

        <footer>
            <p>CloudGuardian Security Scanner | Report Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>"""

        if output_file:
            with open(output_file, 'w') as f:
                f.write(html)
            logger.info(f"✅ HTML report saved to {output_file}")

        return html

    @staticmethod
    def generate_sarif_report(results: List[ScanResult], output_file: str = None) -> str:
        """Generate SARIF report for GitHub integration"""
        sarif = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "CloudGuardian",
                        "version": "1.0.0",
                        "informationUri": "https://cloudguardian.io"
                    }
                },
                "results": []
            }]
        }

        severity_map = {
            'CRITICAL': 'error',
            'HIGH': 'error',
            'MEDIUM': 'warning',
            'LOW': 'note'
        }

        for result in results:
            if result.status != 'success' or not result.findings:
                continue

            for finding in result.findings:
                sarif["runs"][0]["results"].append({
                    "ruleId": finding.get('type', 'UNKNOWN'),
                    "message": {
                        "text": finding.get('description', 'Security finding detected')
                    },
                    "severity": severity_map.get(finding.get('severity', 'LOW'), 'note'),
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": result.filepath
                            },
                            "region": {
                                "startLine": finding.get('line_number', 1)
                            }
                        }
                    }]
                })

        sarif_json = json.dumps(sarif, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(sarif_json)
            logger.info(f"✅ SARIF report saved to {output_file}")

        return sarif_json

    @staticmethod
    def _get_severity_distribution(results: List[ScanResult]) -> Dict[str, int]:
        """Get distribution of severities"""
        dist = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for result in results:
            if result.severity in dist:
                dist[result.severity] += 1
        return dist

    @staticmethod
    def print_summary(results: List[ScanResult]):
        """Print summary to console"""
        print("\n" + "="*60)
        print("CloudGuardian Scan Summary")
        print("="*60)
        print(f"Total files: {len(results)}")
        print(f"Successful: {len([r for r in results if r.status == 'success'])}")
        print(f"Failed: {len([r for r in results if r.status == 'error'])}")
        print(f"Total findings: {sum(r.finding_count for r in results)}")
        
        dist = ReportGenerator._get_severity_distribution(results)
        print("\nSeverity Distribution:")
        for severity, count in dist.items():
            if count > 0:
                print(f"  {severity}: {count}")
        print("="*60 + "\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='CloudGuardian CLI - Security scanning from the command line',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single file
  cloudguardian-cli scan file.tf
  
  # Scan a directory
  cloudguardian-cli scan ./infrastructure
  
  # Generate HTML report
  cloudguardian-cli scan ./src --output report.html --format html
  
  # Scan with custom API endpoint
  cloudguardian-cli scan . --api-url https://api.example.com --token YOUR_TOKEN
  
  # Configure credentials
  cloudguardian-cli config --token YOUR_TOKEN --api-url http://localhost:8000
        """
    )

    # Global arguments
    parser.add_argument('--api-url', help='CloudGuardian API URL', default=os.getenv('CLOUDGUARDIAN_API_URL'))
    parser.add_argument('--token', help='API token for authentication', default=os.getenv('CLOUDGUARDIAN_API_TOKEN'))
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan files for security issues')
    scan_parser.add_argument('path', help='File or directory path to scan')
    scan_parser.add_argument('--output', '-o', help='Output file for report')
    scan_parser.add_argument('--format', '-f', choices=['json', 'html', 'sarif'], default='json',
                           help='Report format')
    scan_parser.add_argument('--type', '-t', choices=['secrets', 'terraform'], default='secrets',
                           help='Scan type')
    scan_parser.add_argument('--patterns', '-p', nargs='+', help='File patterns to scan')
    scan_parser.add_argument('--exclude', '-e', nargs='+', help='Patterns to exclude')
    scan_parser.add_argument('--workers', '-w', type=int, default=4, help='Number of concurrent workers')

    # Config command
    config_parser = subparsers.add_parser('config', help='Configure CloudGuardian CLI')
    config_parser.add_argument('--token', help='Set API token')
    config_parser.add_argument('--api-url', help='Set API URL')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')

    # Health check command
    health_parser = subparsers.add_parser('health', help='Check API health')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle no command
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Initialize config
    config = CloudGuardianConfig(api_url=args.api_url, api_token=args.token)

    # Handle commands
    if args.command == 'config':
        if args.show:
            print(f"API URL: {config.api_url}")
            print(f"API Token: {'***' if config.api_token else 'Not set'}")
        else:
            if args.token:
                config.api_token = args.token
            if hasattr(args, 'api_url') and args.api_url:
                config.api_url = args.api_url
            config.save()

    elif args.command == 'health':
        if not config.validate():
            sys.exit(1)
        
        try:
            response = requests.get(f"{config.api_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ CloudGuardian API is healthy")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"⚠️  API returned status {response.status_code}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to connect to API: {e}")
            sys.exit(1)

    elif args.command == 'scan':
        if not config.validate():
            sys.exit(1)

        scanner = CloudGuardianScanner(config)
        path = os.path.expanduser(args.path)

        if not os.path.exists(path):
            logger.error(f"❌ Path not found: {path}")
            sys.exit(1)

        # Perform scan
        if os.path.isfile(path):
            results = [scanner.scan_file(path, args.type)]
        else:
            patterns = args.patterns if args.patterns else None
            exclude = args.exclude if args.exclude else None
            results = scanner.scan_directory(path, patterns, exclude, args.workers, args.type)

        # Generate report
        ReportGenerator.print_summary(results)

        if args.output:
            if args.format == 'json':
                ReportGenerator.generate_json_report(results, args.output)
            elif args.format == 'html':
                ReportGenerator.generate_html_report(results, args.output)
            elif args.format == 'sarif':
                ReportGenerator.generate_sarif_report(results, args.output)

        # Exit with error if findings found
        total_findings = sum(r.finding_count for r in results)
        if total_findings > 0:
            sys.exit(1)


if __name__ == '__main__':
    main()
