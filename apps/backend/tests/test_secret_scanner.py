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
        # Using a realistic-looking AWS key (not 'EXAMPLE' which is allowlisted)
        code = 'aws_access_key_id = "AKIAIOSFODNN7ABCDEFG"'
        
        findings = self.scanner.scan_content(code, "config.py")
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].secret_type, 'aws_access_key')
        self.assertEqual(findings[0].severity, 'CRITICAL')
        self.assertIn('AWS Access Key', findings[0].description)
    
    def test_aws_secret_key_detection(self):
        """Test detection of AWS Secret Key"""
        # Using a realistic-looking AWS secret key (not 'EXAMPLEKEY' which is allowlisted)
        code = 'aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYABCDEFGH"'
        
        findings = self.scanner.scan_content(code, "config.py")
        
        # Should find at least aws_secret_key (may also find high entropy)
        self.assertGreater(len(findings), 0)
        aws_findings = [f for f in findings if f.secret_type == 'aws_secret_key']
        self.assertEqual(len(aws_findings), 1)
        self.assertEqual(aws_findings[0].severity, 'CRITICAL')
    
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
        # High entropy string with mix of chars, numbers, and symbols
        code = 'database_password = "X9#kL2@mZ7!pQ4$nR1%wE8^tY6&uI3*oA5"'
        
        findings = self.scanner.scan_content(code, "config.py")
        
        # Should detect high entropy string or password pattern
        self.assertGreater(len(findings), 0)
        # Either entropy string or password assignment should be detected
        detected_types = [f.secret_type for f in findings]
        self.assertTrue('high_entropy_string' in detected_types or 'password_assignment' in detected_types)
    
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
        # GitHub PAT format: ghp_ followed by 36 alphanumeric chars
        code = 'GITHUB_TOKEN = "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890"'
        
        findings = self.scanner.scan_content(code, "test.py")
        
        # Should detect at least one finding (github_token or high_entropy)
        self.assertGreater(len(findings), 0)
        # First finding should be github_token pattern match
        github_findings = [f for f in findings if f.secret_type == 'github_token']
        self.assertGreater(len(github_findings), 0)
        self.assertEqual(github_findings[0].severity, 'CRITICAL')
    
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
