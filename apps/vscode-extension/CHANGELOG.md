# Changelog

All notable changes to CloudGuardian VS Code Extension are documented in this file.

## [1.0.0] - 2024-01-22

### ✨ Features

- **Secret Detection**: Real-time scanning for exposed credentials, API keys, and tokens
- **Inline Diagnostics**: Color-coded warnings and errors displayed directly in editor
- **Multiple Commands**:
  - Scan current file (`Ctrl+Shift+G`)
  - Scan entire workspace
  - Clear diagnostics
  - Open settings
- **Auto-Scan Options**:
  - Scan on file save (enabled by default)
  - Scan on file open (optional)
- **Status Bar Integration**: 
  - Visual indicator showing scan status and issue count
  - Color-coded by severity (green/yellow/red)
- **Workspace Scanning**: Scan up to 20 files in workspace at once
- **Configuration System**:
  - API URL configuration
  - API token management
  - Enable/disable extension
  - Customize scan behavior
- **Error Handling**:
  - Graceful handling of backend errors
  - User-friendly error messages
  - Connection failure detection

### 🎨 UI/UX Improvements

- Modern status bar with emoji indicators
- Severity-based color coding in diagnostics
- Inline issue descriptions
- Settings command for quick configuration access
- Clear diagnostic command to reset state

### 🔧 Technical

- TypeScript implementation with full type safety
- Axios for HTTP communication
- VS Code Diagnostic Collection API for rendering
- Configuration schema with proper defaults
- Command palette integration
- Event listeners for file operations

### 📚 Documentation

- Comprehensive README with examples
- Development guide for contributors
- Troubleshooting section
- Configuration documentation
- API integration guide

### 🧪 Testing

- Unit tests for extension functionality
- Integration test framework
- Test setup with VS Code mocks
- Command and configuration validation tests

### 🐛 Bug Fixes

- Fixed timeout issues with large files
- Improved error messages for backend failures
- Proper disposal of resources on deactivation

### 🚀 Performance

- 10-second timeout per file scan
- Debounced auto-scan operations
- Efficient diagnostic rendering
- Workspace scan limited to 20 files

## [0.1.0] - Initial Release

- Basic extension structure
- Manual scan command
- Save trigger integration
- Code action provider foundation

---

## Version Guidelines

- **Major.Minor.Patch** - Semantic versioning
- **Breaking Changes**: Major version bump
- **New Features**: Minor version bump
- **Bug Fixes**: Patch version bump

## Unreleased Features (Planned)

- [ ] AI-powered remediation suggestions
- [ ] Export reports (JSON, HTML, PDF)
- [ ] Integration with GitHub PR comments
- [ ] Custom rule definitions
- [ ] Performance metrics dashboard
- [ ] Multi-workspace support
- [ ] Advanced filtering and search
- [ ] Custom severity levels
- [ ] Plugin system for custom scanners
- [ ] WebSocket support for real-time updates

## Known Issues

None currently reported. Please open an issue if you encounter any problems.

## Getting Help

- **Documentation**: https://docs.cloudguardian.io/vscode-extension
- **Issue Tracker**: https://github.com/cloudguardian/cloudguardian/issues
- **Discussions**: https://github.com/cloudguardian/discussions

## Contributors

- CloudGuardian Team

## License

MIT License - See LICENSE.md for details
