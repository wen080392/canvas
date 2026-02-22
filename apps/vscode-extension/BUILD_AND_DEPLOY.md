# 🚀 VS Code Extension - Build & Deployment Guide

## ⚡ Quick Build

### Development Build
```bash
cd apps/vscode-extension
npm install
npm run compile
```

### Production Build (VSIX)
```bash
npm run package
```

**Output**: `cloudguardian-vscode-1.0.0.vsix`

## 📦 VSIX Package Structure

```
cloudguardian-vscode-1.0.0.vsix
├── extension/
│   ├── package.json
│   ├── README.md
│   ├── CHANGELOG.md
│   └── out/
│       ├── extension.js (compiled)
│       └── extension.js.map
├── [Content_Types].xml
└── extension.vsixmanifest
```

## 🖥️ Installation Methods

### Method 1: VS Code UI
1. Open VS Code
2. Extensions (`Ctrl+Shift+X`)
3. Click **Install from VSIX...**
4. Select `cloudguardian-vscode-1.0.0.vsix`

### Method 2: Command Line
```bash
code --install-extension cloudguardian-vscode-1.0.0.vsix
```

### Method 3: VS Code Marketplace
*(After publishing)*
1. Search "CloudGuardian" in Extensions
2. Click Install

## 🌐 Publishing to Marketplace

### Prerequisites
- VS Code publisher account
- Personal Access Token (PAT)
- `vsce` CLI installed

### Setup Publisher
```bash
npm install -g @vscode/vsce
vsce create-publisher cloudguardian
```

### Generate PAT
1. Azure DevOps: https://dev.azure.com/
2. Organization Settings → Personal Access Tokens
3. New Token → Organization: "All accessible organizations" → Scopes: "Marketplace (manage)"

### Publish
```bash
vsce login cloudguardian
npm run publish
```

## 🔄 Update Process

### For Minor/Patch Updates
1. Update version in `package.json`
2. Update `CHANGELOG.md`
3. Compile: `npm run compile`
4. Package: `npm run package`
5. Test locally with `F5`
6. Commit changes: `git commit -m "chore: bump version to 1.0.1"`
7. Tag: `git tag v1.0.1`
8. Push: `git push origin main && git push origin v1.0.1`

### For Major Updates
1. Update version (e.g., 1.0.0 → 2.0.0)
2. Update `CHANGELOG.md` with breaking changes
3. Update `README.md` if needed
4. Run full test suite: `npm test`
5. Manual testing in debug mode
6. Package and publish

## ✅ Pre-Release Checklist

- [ ] All tests pass: `npm test`
- [ ] Compiles without warnings: `npm run compile`
- [ ] No `console.log()` for debugging left
- [ ] No API tokens or secrets in code
- [ ] Error handling is comprehensive
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version number is incremented
- [ ] Package builds successfully: `npm run package`
- [ ] Manual testing completed
- [ ] Git history is clean
- [ ] No merge conflicts

## 🧪 Test Before Publishing

### 1. Build VSIX
```bash
npm run package
```

### 2. Install Locally
```bash
code --install-extension cloudguardian-vscode-1.0.0.vsix
```

### 3. Test Functionality
- [ ] Extension loads without errors
- [ ] Scan command works: `Ctrl+Shift+G`
- [ ] Workspace scan finds files
- [ ] Status bar shows correctly
- [ ] Error messages are helpful
- [ ] Settings are readable
- [ ] Configuration changes apply

### 4. Uninstall for Clean Test
```bash
code --uninstall-extension cloudguardian.cloudguardian-vscode
```

## 📝 Versioning Strategy

### Semantic Versioning: MAJOR.MINOR.PATCH

| Type | Change | Example |
|------|--------|---------|
| MAJOR | Breaking changes, major features | 1.0.0 → 2.0.0 |
| MINOR | New features, backward compatible | 1.0.0 → 1.1.0 |
| PATCH | Bug fixes, improvements | 1.0.0 → 1.0.1 |

### Version Update Locations
- `package.json` - "version" field
- `CHANGELOG.md` - Add section for version
- Git tag - `git tag v1.0.1`

## 🔗 Distribution Channels

### 1. **VS Code Marketplace** (Primary)
- Automatic updates
- Discovery by users
- One-click installation
- Usage statistics

### 2. **GitHub Releases**
- Manual installation
- VSIX file download
- For manual deployments

### 3. **Direct VSIX Distribution**
- Email/download links
- Company internal distribution
- Custom installations

## 📊 Monitoring After Release

### Marketplace Insights
- Visit: https://marketplace.visualstudio.com/manage/publishers/cloudguardian
- Track: Downloads, ratings, reviews
- Monitor: Issue reports and feedback

### Issue Tracking
- GitHub Issues: https://github.com/cloudguardian/cloudguardian/issues
- Triage high-priority bugs
- Release hotfixes as needed

## 🆘 Rollback Procedure

If critical bugs are found:

### 1. Identify Issue
- Check GitHub issues
- Verify in test environment

### 2. Create Fix Branch
```bash
git checkout -b fix/critical-issue
# Make fixes
npm test
npm run compile
```

### 3. Release Patch
```bash
# Update version: 1.0.1 → 1.0.2
# Update CHANGELOG.md
npm run package
vsce publish
```

### 4. Notify Users
- GitHub announcement
- Release notes
- In-app notification (if possible)

## 🔐 Security Checklist

- [ ] No hardcoded credentials
- [ ] No API keys in source code
- [ ] No user data collection without consent
- [ ] No external phone-home calls
- [ ] HTTPS for all API communication
- [ ] Proper error handling (no stack traces)
- [ ] Input validation on all API calls
- [ ] Dependency versions are pinned

## 📚 Release Notes Template

```markdown
# CloudGuardian VS Code Extension v1.0.1

## What's New

### Features
- New command: "Scan Workspace"
- Improved status bar with icons

### Bug Fixes
- Fixed timeout on large files
- Improved error messages

### Improvements
- Better performance on workspace scans
- Enhanced documentation

## Installation

Search for "CloudGuardian" in VS Code Extensions.

## Getting Help

- 📖 [Documentation](https://docs.cloudguardian.io)
- 🐛 [Report Issues](https://github.com/cloudguardian/cloudguardian/issues)
- 💬 [Discussions](https://github.com/cloudguardian/discussions)
```

## 🎯 Release Cadence

**Recommended Schedule**:
- **Security patches**: Within 24 hours
- **Bug fixes**: Weekly or as needed
- **Minor features**: Monthly
- **Major releases**: Quarterly

## 📞 Support Resources

- **Documentation**: https://docs.cloudguardian.io/vscode-extension
- **Issue Tracker**: https://github.com/cloudguardian/cloudguardian/issues
- **Discussions**: https://github.com/cloudguardian/discussions
- **Email Support**: support@cloudguardian.io

---

**Last Updated**: 2024-01-22
**Maintained By**: CloudGuardian Team
