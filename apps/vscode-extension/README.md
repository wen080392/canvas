# 🛡️ CloudGuardian VS Code Extension

Advanced security scanning directly in VS Code for detecting secrets, vulnerabilities, and compliance issues.

## 🚀 Features

- **Real-time Secret Detection** - Scan files for exposed credentials, API keys, and tokens
- **Inline Diagnostics** - Color-coded warnings and errors inline with your code
- **One-Click Scanning** - Scan current file or entire workspace
- **Auto-Scan on Save** - Optional automatic scanning when files are modified
- **Status Bar Integration** - Quick status indicator with issue count
- **Workspace Scanning** - Scan up to 20 files in your workspace

## 📋 Requirements

- **VS Code** 1.80 or later
- **CloudGuardian Backend** running at `http://localhost:8000`
- **API Token** from CloudGuardian account

## 🔧 Installation

1. **Build from source**:
   ```bash
   cd apps/vscode-extension
   npm install
   npm run compile
   code --install-extension cloudguardian-*.vsix
   ```

2. **Or install from VS Code Marketplace**:
   - Open Extensions in VS Code (`Ctrl+Shift+X`)
   - Search for "CloudGuardian"
   - Click Install

## ⚙️ Configuration

### API Token Setup

1. Open VS Code Settings: `Ctrl+,` (or `Cmd+,` on Mac)
2. Search for `cloudguardian`
3. Set your **API Token** from CloudGuardian dashboard
4. Optionally customize **API URL** (default: `http://localhost:8000`)

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `cloudguardian.apiUrl` | `http://localhost:8000` | CloudGuardian backend API URL |
| `cloudguardian.apiToken` | `` | API authentication token (required) |
| `cloudguardian.enabled` | `true` | Enable/disable extension |
| `cloudguardian.scanOnSave` | `true` | Automatically scan on file save |
| `cloudguardian.scanOnOpen` | `false` | Automatically scan on file open |

**Add to `settings.json`**:
```json
{
  "cloudguardian.apiToken": "your-api-token-here",
  "cloudguardian.apiUrl": "http://localhost:8000",
  "cloudguardian.scanOnSave": true,
  "cloudguardian.enabled": true
}
```

## 🎯 Commands

### Keyboard Shortcuts

| Command | Shortcut | Description |
|---------|----------|-------------|
| CloudGuardian: Scan Current File | `Ctrl+Shift+G` | Scan active editor file |
| CloudGuardian: Scan Workspace | `Ctrl+Shift+Alt+G` | Scan entire workspace |
| CloudGuardian: Clear Diagnostics | - | Clear all findings |
| CloudGuardian: Settings | - | Open extension settings |

### Command Palette

Press `Ctrl+Shift+P` and search for:
- `CloudGuardian: Scan Current File`
- `CloudGuardian: Scan Workspace`
- `CloudGuardian: Clear Diagnostics`
- `CloudGuardian: Settings`

## 🔍 How It Works

### Supported File Types

The extension scans these file types:
- **Infrastructure**: `.tf` (Terraform), `.yaml`, `.yml`
- **Code**: `.py` (Python), `.js`, `.ts`
- **Configuration**: `.json`, `.env`

### Issue Severity Levels

| Severity | Icon | Color | Meaning |
|----------|------|-------|---------|
| **CRITICAL** | 🚨 | Red | Immediate security risk |
| **HIGH** | 🚨 | Red | High severity issue |
| **MEDIUM** | ⚠️ | Orange | Medium priority fix |
| **LOW** | ℹ️ | Blue | Low priority issue |

### Status Bar Indicator

The status bar shows quick visual feedback:
- ✅ **Clean** - No issues found
- ⚠️ **X issues** - Issues detected (clickable for settings)
- 🔍 **Scanning** - Scan in progress
- ❌ **Error** - Scan failed or backend offline

## 🔐 Security & Privacy

- **No Data Storage** - Scanned content is not stored
- **Encrypted Communication** - Uses HTTPS when available
- **Token Protection** - API token stored securely in VS Code
- **Offline Support** - Works with local CloudGuardian instances

## 🐛 Troubleshooting

### Backend Not Running

```
❌ CloudGuardian: Backend not running
```

**Solution**: Start the backend server:
```bash
cd apps/backend
python -m uvicorn app.main:app --reload --port 8000
```

### API Token Not Configured

```
⚠️ CloudGuardian: Configure API token
```

**Solution**: 
1. Open settings: `Ctrl+,`
2. Search for `cloudguardian.apiToken`
3. Paste your API token from CloudGuardian dashboard

### Timeout or Connection Error

**Solutions**:
- Verify backend is running at configured URL
- Check firewall/network connectivity
- Increase timeout in backend settings
- Check backend logs for errors

### Extension Not Scanning

**Check**:
1. Extension is enabled: `cloudguardian.enabled = true`
2. API token is configured
3. VS Code version is 1.80+
4. Run command from Command Palette: `CloudGuardian: Scan Current File`

## 📊 Performance

- **File Size Limit**: Up to 10MB per file
- **Workspace Limit**: Scans up to 20 files per workspace scan
- **Timeout**: 10 seconds per file
- **Auto-Scan**: Debounced to prevent excessive scanning

## 🚀 Advanced Usage

### Disable Auto-Scan for Large Files

Add to `settings.json`:
```json
{
  "cloudguardian.scanOnSave": false
}
```

Then manually scan with: `Ctrl+Shift+G`

### Use Custom Backend

```json
{
  "cloudguardian.apiUrl": "https://cloudguardian.company.com"
}
```

### Scan Specific File Type

Use Command Palette and select file before scanning.

## 📝 Example: Finding Secrets

1. Open any `.env` file or code file with credentials
2. Press `Ctrl+Shift+G` or wait for auto-save trigger
3. Issues appear as inline diagnostics
4. Hover to see details
5. Click status bar for settings

## 🤝 Contributing

Found a bug or have a feature request? 

- **Issue Tracker**: [GitHub Issues](https://github.com/cloudguardian/vs-code-extension/issues)
- **Discussion**: [GitHub Discussions](https://github.com/cloudguardian/discussions)

## 📄 License

MIT License - See LICENSE.md

## 🔗 Links

- **CloudGuardian**: https://cloudguardian.io
- **Documentation**: https://docs.cloudguardian.io
- **Repository**: https://github.com/cloudguardian/cloudguardian
- **Report Issue**: https://github.com/cloudguardian/cloudguardian/issues

---

**Status**: The extension is running and configured properly when you see ✅ or a count in the status bar.

**Need Help?** Open an issue or check documentation at https://docs.cloudguardian.io/vscode-extension
