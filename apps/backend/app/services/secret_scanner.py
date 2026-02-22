"""
Secret Scanner Service

Detects leaked credentials using pattern matching and Shannon entropy analysis.
"""

import re
import math
from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SecretFinding:
    """Represents a detected secret"""
    file_path: str
    line_number: int
    severity: str  # CRITICAL, HIGH, MEDIUM
    secret_type: str
    description: str
    snippet: str  # Partially obfuscated
    entropy: float = 0.0

class SecretScannerService:
    """
    Service to detect leaked credentials in code.
    
    Uses hybrid approach:
    1. Pattern matching (regex) for known formats
    2. Shannon entropy analysis for high-complexity strings
    """
    
    # Known secret patterns
    PATTERNS = {
        'aws_access_key': {
            'pattern': r'AKIA[0-9A-Z]{16}',
            'description': 'AWS Access Key ID',
            'severity': 'CRITICAL'
        },
        'aws_secret_key': {
            'pattern': r'aws_secret_access_key\s*=\s*["\']([A-Za-z0-9/+=]{40})["\']',
            'description': 'AWS Secret Access Key',
            'severity': 'CRITICAL'
        },
        'rsa_private_key': {
            'pattern': r'-----BEGIN RSA PRIVATE KEY-----',
            'description': 'RSA Private Key',
            'severity': 'CRITICAL'
        },
        'ssh_private_key': {
            'pattern': r'-----BEGIN OPENSSH PRIVATE KEY-----',
            'description': 'SSH Private Key',
            'severity': 'CRITICAL'
        },
        'github_token': {
            'pattern': r'ghp_[A-Za-z0-9]{36}',
            'description': 'GitHub Personal Access Token',
            'severity': 'CRITICAL'
        },
        'slack_webhook': {
            'pattern': r'[REDACTED_SLACK]
            'description': 'Slack Webhook URL',
            'severity': 'HIGH'
        },
        'generic_api_key': {
            'pattern': r'(api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*["\']([A-Za-z0-9_\-]{20,})["\']',
            'description': 'Generic API Key',
            'severity': 'HIGH'
        },
        'password_assignment': {
            'pattern': r'(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']',
            'description': 'Hardcoded Password',
            'severity': 'HIGH'
        }
    }
    
    # Entropy threshold for detection
    ENTROPY_THRESHOLD = 4.5
    
    # Allowlist patterns (known safe high-entropy strings)
    ALLOWLIST_PATTERNS = [
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',  # UUID
        r'^[0-9a-f]{40}$',  # Git SHA
        r'^[0-9a-f]{64}$',  # SHA256
        r'example|sample|test|dummy|placeholder|changeme',  # Obvious examples
    ]
    
    # Binary and exclude extensions
    BINARY_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz'}
    EXCLUDE_DIRS = {'.git', 'node_modules', '.venv', '__pycache__', 'dist', 'build'}
    
    def __init__(self):
        """Initialize scanner"""
        self.findings: List[SecretFinding] = []
    
    def calculate_shannon_entropy(self, data: str) -> float:
        """
        Calculate Shannon entropy of a string.
        
        Higher entropy = more randomness = likely a secret
        
        Args:
            data: String to analyze
        
        Returns:
            Entropy value (0 = no randomness, ~5+ = high randomness)
        """
        if not data:
            return 0.0
        
        # Count character frequency
        entropy = 0.0
        for char in set(data):
            prob = data.count(char) / len(data)
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        return entropy
    
    def is_allowlisted(self, text: str) -> bool:
        """
        Check if string matches allowlist patterns.
        
        Args:
            text: String to check
        
        Returns:
            True if string is safe (UUID, example, etc)
        """
        text_lower = text.lower()
        
        for pattern in self.ALLOWLIST_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def scan_content(
        self,
        content: str,
        file_path: str = "unknown"
    ) -> List[SecretFinding]:
        """
        Scan content for secrets.
        
        Args:
            content: File content to scan
            file_path: Path to file (for reporting)
        
        Returns:
            List of SecretFinding objects
        """
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Pattern-based detection
            for secret_type, pattern_info in self.PATTERNS.items():
                matches = re.finditer(pattern_info['pattern'], line, re.IGNORECASE)
                
                for match in matches:
                    # Check if it's allowlisted
                    matched_text = match.group(0)
                    if self.is_allowlisted(matched_text):
                        continue
                    
                    # Obfuscate snippet
                    snippet = self._obfuscate_secret(line, match.span())
                    
                    finding = SecretFinding(
                        file_path=file_path,
                        line_number=line_num,
                        severity=pattern_info['severity'],
                        secret_type=secret_type,
                        description=pattern_info['description'],
                        snippet=snippet
                    )
                    findings.append(finding)
            
            # Entropy-based detection for high-complexity strings
            # Look for strings in quotes with high entropy
            string_pattern = r'["\']([A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:,.<>?/\\|`~]{12,})["\']'
            string_matches = re.finditer(string_pattern, line)
            
            for match in string_matches:
                candidate = match.group(1)
                
                # Skip if allowlisted
                if self.is_allowlisted(candidate):
                    continue
                
                # Calculate entropy
                entropy = self.calculate_shannon_entropy(candidate)
                
                if entropy >= self.ENTROPY_THRESHOLD:
                    snippet = self._obfuscate_secret(line, match.span())
                    
                    finding = SecretFinding(
                        file_path=file_path,
                        line_number=line_num,
                        severity='MEDIUM',
                        secret_type='high_entropy_string',
                        description=f'High entropy string detected (entropy: {entropy:.2f})',
                        snippet=snippet,
                        entropy=entropy
                    )
                    findings.append(finding)
        
        return findings
    
    def scan_file(self, file_path: str) -> List[SecretFinding]:
        """
        Scan a single file.
        
        Args:
            file_path: Path to file
        
        Returns:
            List of findings
        """
        path = Path(file_path)
        
        # Skip binary files
        if path.suffix in self.BINARY_EXTENSIONS:
            return []
        
        # Skip excluded directories
        if any(excluded in path.parts for excluded in self.EXCLUDE_DIRS):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return self.scan_content(content, file_path)
            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return []
    
    def scan_directory(self, directory: str) -> List[SecretFinding]:
        """
        Recursively scan a directory.
        
        Args:
            directory: Directory path
        
        Returns:
            List of all findings
        """
        all_findings = []
        dir_path = Path(directory)
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                findings = self.scan_file(str(file_path))
                all_findings.extend(findings)
        
        return all_findings
    
    def _obfuscate_secret(self, line: str, match_span: tuple) -> str:
        """
        Obfuscate the secret in the snippet for safe logging.
        
        Args:
            line: Full line of code
            match_span: Tuple of (start, end) positions
        
        Returns:
            Line with secret partially obfuscated
        """
        start, end = match_span
        secret = line[start:end]
        
        # Show first 4 and last 4 characters, obfuscate middle
        if len(secret) > 8:
            obfuscated = secret[:4] + '*' * (len(secret) - 8) + secret[-4:]
        else:
            obfuscated = '*' * len(secret)
        
        return line[:start] + obfuscated + line[end:]
    
    def generate_report(self, findings: List[SecretFinding]) -> Dict[str, Any]:
        """
        Generate summary report.
        
        Args:
            findings: List of findings
        
        Returns:
            Report dictionary
        """
        severity_counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0
        }
        
        for finding in findings:
            severity_counts[finding.severity] += 1
        
        return {
            'total_findings': len(findings),
            'by_severity': severity_counts,
            'findings': [
                {
                    'file': f.file_path,
                    'line': f.line_number,
                    'severity': f.severity,
                    'type': f.secret_type,
                    'description': f.description,
                    'snippet': f.snippet
                }
                for f in findings
            ]
        }
