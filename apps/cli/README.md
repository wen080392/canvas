# 🛡️ CloudGuardian CLI - Command-Line Security Scanner

## 📋 Overview

The CloudGuardian CLI provides command-line access to all security scanning features. Scan files, directories, and generate comprehensive reports directly from your terminal.

## ✨ Features

- ✅ **Single File & Directory Scanning** - Recursive scanning with pattern matching
- ✅ **Multiple Report Formats** - JSON, HTML, SARIF (GitHub Actions)
- ✅ **Concurrent Scanning** - Multi-threaded scanning for speed
- ✅ **Configuration Management** - Store API credentials locally
- ✅ **CI/CD Ready** - SARIF output for GitHub, GitLab, etc.
- ✅ **Multiple Scan Types** - Secrets, Terraform, compliance
- ✅ **Exit Code Support** - Non-zero exit on findings for CI/CD pipelines
- ✅ **Flexible Filtering** - Include/exclude patterns for fine-grained control

## 🚀 Installation

### From Source
```bash
cd apps/cli
pip install -e .
```

### From PyPI (When Published)
```bash
pip install cloudguardian-cli
```

### Verify Installation
```bash
cloudguardian-cli --help
```

## 🔧 Quick Start

### 1. Set Configuration
```bash
# Set API token
cloudguardian-cli config --token YOUR_API_TOKEN

# Set custom API URL
cloudguardian-cli config --api-url https://api.example.com --token YOUR_TOKEN
```

### 2. Check API Health
```bash
cloudguardian-cli health
# Output: ✅ CloudGuardian API is healthy
```

### 3. Scan a File
```bash
cloudguardian-cli scan ./main.tf
```

### 4. Scan a Directory
```bash
cloudguardian-cli scan ./infrastructure
```

### 5. Generate Report
```bash
# JSON report
cloudguardian-cli scan ./src --output report.json --format json

# HTML report
cloudguardian-cli scan ./src --output report.html --format html

# SARIF report (GitHub Actions)
cloudguardian-cli scan ./src --output results.sarif --format sarif
```

## 📖 Commands

### scan
Scan files or directories for security issues

**Usage**:
```bash
cloudguardian-cli scan <path> [options]
```

**Options**:
- `--output, -o` - Output file for report
- `--format, -f` - Report format: json, html, sarif (default: json)
- `--type, -t` - Scan type: secrets, terraform (default: secrets)
- `--patterns, -p` - File patterns to include (default: *.tf *.py *.js *.ts *.json *.env *.yml *.yaml)
- `--exclude, -e` - Patterns to exclude
- `--workers, -w` - Number of concurrent workers (default: 4)

**Examples**:
```bash
# Scan single file
cloudguardian-cli scan main.tf

# Scan directory with custom patterns
cloudguardian-cli scan ./src -p "*.py" "*.js"

# Scan with exclusions
cloudguardian-cli scan . -e "node_modules/*" ".git/*" "__pycache__/*"

# Scan with HTML report
cloudguardian-cli scan ./infrastructure -o report.html -f html

# Scan with 8 workers
cloudguardian-cli scan . -w 8
```

### config
Configure CloudGuardian CLI credentials and endpoints

**Usage**:
```bash
cloudguardian-cli config [options]
```

**Options**:
- `--token` - Set API token
- `--api-url` - Set API URL
- `--show` - Display current configuration

**Examples**:
```bash
# Set credentials
cloudguardian-cli config --token YOUR_TOKEN

# Set custom endpoint
cloudguardian-cli config --api-url https://api.example.com

# Show current config
cloudguardian-cli config --show

# Set both
cloudguardian-cli config --token YOUR_TOKEN --api-url https://api.example.com
```

### health
Check CloudGuardian API health and connectivity

**Usage**:
```bash
cloudguardian-cli health
```

**Output**:
```
✅ CloudGuardian API is healthy
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## 🌍 Environment Variables

### API Configuration
```bash
# API URL (default: http://localhost:8000)
export CLOUDGUARDIAN_API_URL=https://api.example.com

# API Token (required)
export CLOUDGUARDIAN_API_TOKEN=your-jwt-token-here
```

### Usage
```bash
# These will be read automatically
cloudguardian-cli scan .

# Or override with command-line arguments
cloudguardian-cli --api-url https://custom.com --token custom-token scan .
```

## 📊 Report Formats

### JSON Report
```json
{
  "timestamp": "2024-01-22T10:30:00",
  "total_files": 10,
  "successful_scans": 10,
  "failed_scans": 0,
  "total_findings": 3,
  "severity_distribution": {
    "CRITICAL": 1,
    "HIGH": 1,
    "MEDIUM": 1,
    "LOW": 0
  },
  "results": [
    {
      "filename": "main.tf",
      "filepath": "/path/main.tf",
      "file_type": "terraform",
      "scan_type": "secrets",
      "severity": "CRITICAL",
      "findings": [
        {
          "type": "AWS_KEY",
          "severity": "CRITICAL",
          "description": "AWS Access Key detected"
        }
      ],
      "finding_count": 1,
      "status": "success"
    }
  ]
}
```

### HTML Report
- Professional styled report with statistics
- Severity-based color coding
- File-by-file results in table format
- Severity distribution visualization
- Timestamp and generated time

### SARIF Report
- GitHub Actions compatible format
- Auto-generates PR annotations
- Severity mapping to SARIF levels
- File locations and line numbers

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
name: CloudGuardian Security Scan

on: [pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install CloudGuardian CLI
        run: pip install cloudguardian-cli
      
      - name: Run scan
        env:
          CLOUDGUARDIAN_API_TOKEN: ${{ secrets.CLOUDGUARDIAN_TOKEN }}
          CLOUDGUARDIAN_API_URL: ${{ secrets.CLOUDGUARDIAN_URL }}
        run: |
          cloudguardian-cli scan . \
            --output results.sarif \
            --format sarif
      
      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

### GitLab CI

```yaml
security_scan:
  stage: security
  image: python:3.11
  script:
    - pip install cloudguardian-cli
    - cloudguardian-cli scan . --output report.json --format json
  artifacts:
    reports:
      sast: report.json
  only:
    - merge_requests
```

### Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('CloudGuardian Scan') {
            steps {
                sh '''
                    pip install cloudguardian-cli
                    cloudguardian-cli scan . \
                        --output report.html \
                        --format html
                '''
            }
        }
        
        stage('Publish Report') {
            steps {
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'report.html',
                    reportName: 'CloudGuardian Security Report'
                ])
            }
        }
    }
}
```

## 📝 Usage Examples

### Basic Scanning
```bash
# Scan current directory
cloudguardian-cli scan .

# Scan specific directory
cloudguardian-cli scan ./src

# Scan specific file
cloudguardian-cli scan main.tf
```

### Custom Patterns
```bash
# Scan only Python files
cloudguardian-cli scan . -p "*.py"

# Scan multiple file types
cloudguardian-cli scan . -p "*.tf" "*.py" "*.js"

# Exclude patterns
cloudguardian-cli scan . -e "node_modules/*" ".git/*" "venv/*"

# Combine include and exclude
cloudguardian-cli scan . -p "*.py" -e "*_test.py" "test_*"
```

### Reports and Output
```bash
# Save JSON report
cloudguardian-cli scan . -o report.json

# Generate HTML report
cloudguardian-cli scan . -o report.html -f html

# Create SARIF for GitHub
cloudguardian-cli scan . -o results.sarif -f sarif

# All formats at once
cloudguardian-cli scan . -o report && \
  cloudguardian-cli scan . -o report.html -f html && \
  cloudguardian-cli scan . -o results.sarif -f sarif
```

### Performance Tuning
```bash
# Increase workers for faster scanning
cloudguardian-cli scan . -w 8

# Reduce workers on limited systems
cloudguardian-cli scan . -w 2

# Scan with verbose output
cloudguardian-cli scan . -v
```

### Different Scan Types
```bash
# Scan for secrets (default)
cloudguardian-cli scan . -t secrets

# Scan for Terraform issues
cloudguardian-cli scan . -t terraform

# Scan specific types
cloudguardian-cli scan . -t secrets -p "*.env" "*.tf"
```

## 🔐 Security Best Practices

### Token Management
```bash
# ✅ Use environment variable
export CLOUDGUARDIAN_API_TOKEN=your-token
cloudguardian-cli scan .

# ✅ Use config file with restricted permissions
cloudguardian-cli config --token your-token
chmod 600 ~/.cloudguardian/config.json

# ❌ Don't pass token as command-line argument in shared shells
# cloudguardian-cli --token YOUR_TOKEN scan .  # Visible in history!
```

### API URL Configuration
```bash
# ✅ Use environment variable for production
export CLOUDGUARDIAN_API_URL=https://api.company.com

# ✅ Use config file
cloudguardian-cli config --api-url https://api.company.com

# ✅ For local development
export CLOUDGUARDIAN_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### "API token not configured"
```bash
# Solution 1: Set environment variable
export CLOUDGUARDIAN_API_TOKEN=your-token

# Solution 2: Configure CLI
cloudguardian-cli config --token your-token

# Solution 3: Check config file
cloudguardian-cli config --show
```

### "Failed to connect to API"
```bash
# Check API is running
cloudguardian-cli health

# Verify API URL
cloudguardian-cli config --show

# Try explicit URL
cloudguardian-cli --api-url http://localhost:8000 health

# Check firewall/network
curl http://localhost:8000/health
```

### "Permission denied"
```bash
# Make script executable
chmod +x cloudguardian-cli

# Or run with Python
python -m cloudguardian_cli scan .
```

### "No files found"
```bash
# Check patterns match your files
ls -la main.tf

# Verbose mode shows what's being scanned
cloudguardian-cli scan . -v

# Try explicit patterns
cloudguardian-cli scan . -p "*.tf" "*.py"
```

### "Timeout"
```bash
# Reduce file size or use exclusions
cloudguardian-cli scan . -e "large_files/*"

# Reduce workers
cloudguardian-cli scan . -w 2

# Increase API timeout (backend setting)
```

## 📊 Exit Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 0 | Success, no findings | Normal completion |
| 1 | Findings detected | CI/CD pipeline failure trigger |
| 2 | Configuration error | Fix configuration and retry |
| 3 | API error | Check backend connectivity |

**Example - CI/CD Failure on Findings**:
```bash
cloudguardian-cli scan . || exit 1
```

## 🔧 Advanced Configuration

### Config File Location
```
~/.cloudguardian/config.json
```

### Config File Format
```json
{
  "api_url": "https://api.example.com",
  "api_token": "eyJhbGc..."
}
```

### Override Config File
```bash
# Use specific config file
cloudguardian-cli --config /etc/cloudguardian/config.json scan .

# Command-line overrides config file
cloudguardian-cli --api-url https://other.com scan .
```

## 📚 Examples and Recipes

### Scan Infrastructure as Code
```bash
cloudguardian-cli scan ./terraform -p "*.tf" -o infra-report.html -f html
```

### Scan Source Code
```bash
cloudguardian-cli scan ./src -p "*.py" "*.js" -e "test_*" "*_test.py" -o code-report.json
```

### Scan Entire Project
```bash
cloudguardian-cli scan . \
  -p "*.tf" "*.py" "*.js" "*.env" \
  -e "node_modules/*" ".git/*" "__pycache__/*" "venv/*" \
  -o full-report.html -f html
```

### Generate All Report Types
```bash
#!/bin/bash
cloudguardian-cli scan . -o report.json -f json
cloudguardian-cli scan . -o report.html -f html
cloudguardian-cli scan . -o results.sarif -f sarif
echo "All reports generated!"
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
cloudguardian-cli scan . -t secrets --workers 8
if [ $? -ne 0 ]; then
    echo "Security scan failed. Commit blocked."
    exit 1
fi
```

## 🎯 Performance Tips

1. **Use Multiple Workers** - Increase `-w` for faster scanning
2. **Filter Files** - Use `-p` and `-e` to scan only necessary files
3. **Cache Results** - Store reports for comparison
4. **Parallel Scans** - Run multiple CLI instances for different directories
5. **Local API** - Use local CloudGuardian instance for speed

## 📞 Support

- **GitHub Issues**: https://github.com/cloudguardian/cloudguardian/issues
- **Documentation**: https://docs.cloudguardian.io/cli
- **Community**: https://github.com/cloudguardian/discussions

## 📝 Version

```bash
cloudguardian-cli --version
# CloudGuardian CLI v1.0.0
```

## 📄 License

MIT License - See LICENSE.md for details

---

**Pro Tip**: Combine with other CLI tools for powerful automation:
```bash
# Scan and immediately generate HTML report if findings detected
cloudguardian-cli scan . || cloudguardian-cli scan . -o report.html -f html && open report.html
```
