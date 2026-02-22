"""
Terraform Validator Service

Validates and formats Terraform code using terraform CLI.
"""

import subprocess
import tempfile
import os
from typing import Tuple, Optional
from pathlib import Path

class TerraformValidator:
    """
    Service to validate and format Terraform code.
    
    Requires terraform CLI to be installed and available in PATH.
    """
    
    def __init__(self, terraform_bin: str = "terraform"):
        """
        Initialize validator.
        
        Args:
            terraform_bin: Path to terraform binary (default: 'terraform')
        """
        self.terraform_bin = terraform_bin
    
    def format_code(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Format Terraform code using `terraform fmt`.
        
        Args:
            file_path: Path to .tf file to format
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            result = subprocess.run(
                [self.terraform_bin, "fmt", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Terraform fmt timeout after 10s"
        except FileNotFoundError:
            return False, f"Terraform binary not found: {self.terraform_bin}"
        except Exception as e:
            return False, str(e)
    
    def validate_code(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Terraform syntax using `terraform validate`.
        
        Note: This requires running 'terraform init' first in the directory.
        For simpler validation, we use basic syntax check.
        
        Args:
            file_path: Path to .tf file
        
        Returns:
            Tuple of (is_valid: bool, error_output: Optional[str])
        """
        try:
            # Get directory containing the file
            file_dir = os.path.dirname(file_path)
            
            # First check if .terraform directory exists (init was run)
            terraform_dir = os.path.join(file_dir, ".terraform")
            
            # For validation, we need terraform init
            # In production, you'd have a pre-initialized workspace
            if not os.path.exists(terraform_dir):
                # Run init in background (quick validation mode)
                init_result = subprocess.run(
                    [self.terraform_bin, "init", "-backend=false"],
                    cwd=file_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if init_result.returncode != 0:
                    return False, f"Init failed: {init_result.stderr}"
            
            # Now run validate
            result = subprocess.run(
                [self.terraform_bin, "validate"],
                cwd=file_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
        except Exception as e:
            return False, str(e)
    
    def create_temp_file(self, content: str, suffix: str = ".tf") -> str:
        """
        Create temporary file with Terraform content.
        
        Args:
            content: Terraform code
            suffix: File suffix (default: .tf)
        
        Returns:
            Path to temporary file
        """
        # Create temp file that won't be auto-deleted
        fd, path = tempfile.mkstemp(suffix=suffix, text=True)
        
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
            return path
        except Exception as e:
            os.close(fd)
            raise e
    
    def validate_and_format(
        self,
        content: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Convenience method: Format and validate in one call.
        
        Args:
            content: Terraform code as string
        
        Returns:
            Tuple of (success, formatted_content, error_message)
        """
        temp_file = None
        try:
            # Create temp file
            temp_file = self.create_temp_file(content)
            
            # Format
            fmt_success, fmt_error = self.format_code(temp_file)
            if not fmt_success:
                return False, None, f"Format error: {fmt_error}"
            
            # Validate
            val_success, val_error = self.validate_code(temp_file)
            if not val_success:
                return False, None, f"Validation error: {val_error}"
            
            # Read formatted content
            with open(temp_file, 'r') as f:
                formatted_content = f.read()
            
            return True, formatted_content, None
            
        finally:
            # Cleanup
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
                
                # Also remove .terraform directory if created
                temp_dir = os.path.dirname(temp_file)
                terraform_dir = os.path.join(temp_dir, ".terraform")
                if os.path.exists(terraform_dir):
                    import shutil
                    shutil.rmtree(terraform_dir, ignore_errors=True)
