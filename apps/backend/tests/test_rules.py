import pytest
from app.rules.aws.s3 import S3PublicAccessRule
from app.rules.base import Severity

def test_s3_public_access_rule_detects_public_acl():
    rule = S3PublicAccessRule()
    resource = {
        'type': 'aws_s3_bucket',
        'values': {
            'bucket': 'my-public-bucket',
            'acl': 'public-read'
        }
    }
    
    issue = rule.check(resource)
    
    assert issue is not None
    assert issue.severity == Severity.HIGH
    assert issue.message == "S3 bucket has public access enabled via ACL"
    assert issue.fix_suggestion == 'acl = "private"'

def test_s3_public_access_rule_passes_private_acl():
    rule = S3PublicAccessRule()
    resource = {
        'type': 'aws_s3_bucket',
        'values': {
            'bucket': 'my-private-bucket',
            'acl': 'private'
        }
    }
    
    issue = rule.check(resource)
    
    assert issue is None
