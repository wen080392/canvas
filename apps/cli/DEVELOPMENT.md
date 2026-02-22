# CloudGuardian CLI - Development Guide

## 🏗️ Architecture

The CLI is organized into several key classes:

```
cloudguardian_cli.py
├── CloudGuardianConfig      # Configuration management
├── CloudGuardianScanner     # Scanner client + file discovery
├── ScanResult (dataclass)   # Result container
└── ReportGenerator          # Report generation (JSON, HTML, SARIF)
```

## 🚀 Quick Start Development

### Setup
```bash
cd apps/cli
pip install -e .
```

### Run Tests
```bash
python -m pytest test_cli.py -v
```

### Run CLI
```bash
python cloudguardian_cli.py scan .
python cloudguardian_cli.py --help
```

## 📝 Code Structure

### CloudGuardianConfig
Manages API credentials and configuration:
- Loads from environment variables
- Loads from config file `~/.cloudguardian/config.json`
- Command-line override support
- Validation methods

### CloudGuardianScanner
Scans files via CloudGuardian API:
- Single file scanning
- Recursive directory scanning
- Concurrent scanning with ThreadPoolExecutor
- File pattern matching
- API communication with Bearer tokens

### ScanResult
Dataclass containing scan results:
- File metadata
- Findings list
- Scan status
- Duration tracking
- Error messages

### ReportGenerator
Generates multiple report formats:
- JSON: Structured data for processing
- HTML: Visual report for review
- SARIF: GitHub Actions compatible

## 🔧 Adding New Features

### Add New Report Format

```python
@staticmethod
def generate_custom_report(results: List[ScanResult], output_file: str = None) -> str:
    """Generate custom report format"""
    custom_format = "..."
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(custom_format)
        logger.info(f"✅ Report saved to {output_file}")
    
    return custom_format
```

Then add to argument parser:
```python
scan_parser.add_argument(
    '--format', '-f',
    choices=['json', 'html', 'sarif', 'custom'],  # Add here
    default='json'
)
```

And add to scan command handler:
```python
elif args.format == 'custom':
    ReportGenerator.generate_custom_report(results, args.output)
```

## 🧪 Testing

### Running Tests
```bash
python -m pytest test_cli.py -v
python -m pytest test_cli.py::TestCloudGuardianConfig -v
```

### With Coverage
```bash
python -m pytest test_cli.py --cov=cloudguardian_cli --cov-report=html
```

### Individual Test
```bash
python -m pytest test_cli.py::TestReportGenerator::test_json_report_generation -v
```

## 📦 Packaging

### Install Locally
```bash
pip install -e .
```

### Build Distribution
```bash
python setup.py sdist bdist_wheel
```

### Install from Wheel
```bash
pip install dist/cloudguardian_cli-1.0.0-py3-none-any.whl
```

## 🔌 API Integration

### Backend Endpoints Used

**POST /secrets/scan**
```
Request:
{
  "content": "file content",
  "filename": "name.tf"
}

Response:
{
  "secrets": [...],
  "total_findings": 0
}
```

**GET /health**
```
Response:
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## 🐛 Debugging

### Enable Verbose Logging
```bash
python cloudguardian_cli.py -v scan .
```

### Mock API Responses
```python
with patch('requests.Session.post') as mock_post:
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {...}
    # Run test
```

## 📊 Performance

### Concurrent Scanning
- Default: 4 workers
- Max recommended: 8-16 (depends on system)
- Set via: `-w` or `--workers` argument

### File Discovery
- Uses `os.walk()` for efficient traversal
- Pattern matching with `fnmatch`
- Excludes common directories (node_modules, .git, etc.)

### API Timeouts
- Request timeout: 30 seconds
- Suitable for files up to 10MB

## 🔐 Security

### Token Management
- Never log API tokens
- Store in secure config file
- Use environment variables for CI/CD
- Support Bearer authentication

### Input Validation
- Validate file paths exist
- Check file is readable
- Validate API responses
- Sanitize error messages

## 📚 Code Style

### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`

### Documentation
- All functions have docstrings
- Document parameters and return types
- Include usage examples

### Logging
```python
logger.info('Normal info')       # ℹ️  General information
logger.warning('Warning')        # ⚠️  Warnings
logger.error('Error occurred')   # ❌ Errors
logger.debug('Debug info')       # 🔍 Debug only
```

## 🚀 Release Process

### Update Version
1. Edit `__init__.py`: `__version__ = "1.1.0"`
2. Edit `setup.py`: `version="1.1.0"`

### Build Package
```bash
python setup.py sdist bdist_wheel
```

### Test Installation
```bash
pip install dist/cloudguardian_cli-*.whl
cloudguardian-cli --version
```

## ✅ Checklist for New PR

- [ ] Code follows PEP 8
- [ ] All functions documented
- [ ] Tests added/updated
- [ ] Tests pass locally
- [ ] No hardcoded values
- [ ] Error handling comprehensive
- [ ] Logging added
- [ ] README updated
- [ ] No breaking changes

---

**Last Updated**: 2024-01-22
**Maintainer**: CloudGuardian Team
