import hcl2
from typing import List, Dict, Any
from app.rules.base import SecurityIssue, SecurityRule
from app.rules.aws.s3 import S3PublicAccessRule

class SecurityScanner:
    def __init__(self):
        self.rules: List[SecurityRule] = [
            S3PublicAccessRule()
        ]

    def scan(self, hcl_content: str) -> List[SecurityIssue]:
        issues = []
        try:
            # Parse HCL content
            # hcl2.loads returns a dict with keys as resource types
            parsed = hcl2.loads(hcl_content)
            
            # Iterate over resources
            # Structure is usually: {'resource': [{'aws_s3_bucket': {'my_bucket': {...}}}]}
            resources_block = parsed.get('resource', [])
            
            for resource_entry in resources_block:
                for resource_type, resource_instances in resource_entry.items():
                    for instance_name, instance_config in resource_instances.items():
                        # Normalize resource for rule check
                        # We pass a simplified dict: {'type': 'aws_s3_bucket', 'name': 'my_bucket', 'values': {...}}
                        resource_context = {
                            'type': resource_type,
                            'name': instance_name,
                            'values': instance_config
                        }
                        
                        for rule in self.rules:
                            issue = rule.check(resource_context)
                            if issue:
                                issues.append(issue)
                                
        except Exception as e:
            print(f"Error parsing HCL: {e}")
            # In a real app, we might want to return a parsing error issue
            
        return issues
