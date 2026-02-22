"""
Unit Tests for Secret Scanner

Tests pattern matching and entropy-based detection.
"""

import unittest
from app.services.secret_scanner import SecretScannerService, SecretFinding

class TestSecretScanner(unittest.TestCase):
    """Test cases for SecretScannerService"""
    
    def setUp(self):
        """Initialize scanner for each test"""
        self.scanner = SecretScannerService()
    
    def test_aws_access_key_detection(self):
        """Test detection of AWS Access Key ID"""
        code = 'aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"'
        
        findings = self.scanner.scan_content(code, "test.py")
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].secret_type, 'aws_access_key')
        self.assertEqual(findings[0].severity, 'CRITICAL')
        self.assertIn('AWS Access Key', findings[0].description)
    
    def test_aws_secret_key_detection(self):
        """Test detection of AWS Secret Key"""
        code = 'aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
        
        findings = self.scanner.scan_content(code, "test.py")
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].secret_type, 'aws_secret_key')
        self.assertEqual(findings[0].severity, 'CRITICAL')
    
    def test_rsa_private_key_detection(self):
        """Test detection of RSA private key"""
        code = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----
        '''
        
        findings = self.scanner.scan_content(code, "key.pem")
        
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0].severity, 'CRITICAL')
    
    def test_high_entropy_detection(self):
        """Test entropy-based detection of random strings"""
        code = 'database_password = "7f8a9d0s8f9a0s8d9f0a8sd90f"'
        
        findings = self.scanner.scan_content(code, "config.py")
        
        # Should detect high entropy string
        entropy_findings = [f for f in findings if f.secret_type == 'high_entropy_string']
        self.assertGreater(len(entropy_findings), 0)
        self.assertGreater(entropy_findings[0].entropy, self.scanner.ENTROPY_THRESHOLD)
    
    def test_uuid_not_detected(self):
        """Test that UUIDs are NOT flagged (allowlist)"""
        code = 'request_id = "550e8400-e29b-41d4-a716-446655440000"'
        
        findings = self.scanner.scan_content(code, "test.py")
        
        # UUID should be allowlisted
        self.assertEqual(len(findings), 0)
    
    def test_git_sha_not_detected(self):
        """Test that Git SHAs are NOT flagged (allowlist)"""
        code = 'commit_hash = "356a192b7913b04c54574d18c28d46e6395428ab"'
        
        findings = self.scanner.scan_content(code, "test.py")
        
        # Git SHA should be allowlisted
        self.assertEqual(len(findings), 0)
    
    def test_example_values_not_detected(self):
        """Test that obvious examples are NOT flagged"""
        code = 'api_key = "example_key_changeme"'
        
        findings = self.scanner.scan_content(code, "example.py")
        
        # Should be allowlisted
        self.assertEqual(len(findings), 0)
    
    def test_normal_code_not_detected(self):
        """Test that normal code doesn't trigger false positives"""
        code = '''
import os
from typing import List

def my_function(param: str) -> bool:
    return param == "value"
        '''
        
        findings = self.scanner.scan_content(code, "main.py")
        
        # Should have no findings
        self.assertEqual(len(findings), 0)
    
    def test_shannon_entropy_calculation(self):
        """Test Shannon entropy calculation accuracy"""
        # Low entropy (repetitive)
        low_entropy_string = "aaaaaaaaaa"
        low_entropy = self.scanner.calculate_shannon_entropy(low_entropy_string)
        self.assertLess(low_entropy, 1.0)
        
        # High entropy (random)
        high_entropy_string = "Xy7#b9@Lz1"
        high_entropy = self.scanner.calculate_shannon_entropy(high_entropy_string)
        self.assertGreater(high_entropy, 3.0)
    
    def test_obfuscation(self):
        """Test secret obfuscation in snippets"""
        line = 'password = "MySecretPassword123"'
        match_span = (11, 32)  # Position of the password
        
        obfuscated = self.scanner._obfuscate_secret(line, match_span)
        
        # Should contain asterisks
        self.assertIn('*', obfuscated)
        # Should NOT contain full secret
        self.assertNotIn('MySecretPassword123', obfuscated)
    
    def test_github_token_detection(self):
        """Test detection of GitHub Personal Access Token"""
        code = 'GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvw"'
        
        findings = self.scanner.scan_content(code, "test.py")
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].secret_type, 'github_token')
        self.assertEqual(findings[0].severity, 'CRITICAL')
    
    def test_slack_webhook_detection(self):
        """Test detection of Slack webhook URL"""
        code = 'webhook = "[REDACTED_SLACK]
        
        findings = self.scanner.scan_content(code, "test.py")
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].secret_type, 'slack_webhook')
        self.assertEqual(findings[0].severity, 'HIGH')
    
    def test_report_generation(self):
        """Test report generation"""
        code = '''
aws_key = "AKIAIOSFODNN7EXAMPLE"
password = "Xy7#b9@Lz1"
        '''
        
        findings = self.scanner.scan_content(code, "test.py")
        report = self.scanner.generate_report(findings)
        
        self.assertIn('total_findings', report)
        self.assertIn('by_severity', report)
        self.assertGreater(report['total_findings'], 0)

if __name__ == '__main__':
    unittest.main()
