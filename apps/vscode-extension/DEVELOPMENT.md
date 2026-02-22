# 🛠️ CloudGuardian VS Code Extension - Development Guide

## 🏗️ Architecture

```
src/
├── extension.ts          # Main entry point with CloudGuardianScanner class
├── test/
│   ├── extension.test.ts # Integration tests
│   ├── setup.ts          # Test configuration
│   └── vscode-mock.ts    # VS Code API mocks
```

## 🚀 Quick Start Development

### 1. Install Dependencies
```bash
cd apps/vscode-extension
npm install
```

### 2. Compile TypeScript
```bash
npm run compile
```

### 3. Watch for Changes
```bash
npm run watch
```

### 4. Run Tests
```bash
npm test
```

### 5. Run Extension in Debug Mode
- Press `F5` in VS Code (automatically opens debug session)
- Or go to Run → Run Without Debugging

## 📦 Project Structure

### Main Extension File: `src/extension.ts`

**CloudGuardianScanner Class**:
- Manages all scanning operations
- Handles API communication
- Renders diagnostics inline
- Updates status bar

**Key Methods**:
| Method | Purpose |
|--------|---------|
| `loadConfig()` | Reads VS Code settings |
| `scanDocument()` | Scans single file |
| `displayDiagnostics()` | Renders issues inline |
| `mapSeverity()` | Maps API severity to VS Code severity |
| `updateStatusBar()` | Updates status indicator |
| `scanWorkspace()` | Scans multiple files |
| `clear()` | Clears all diagnostics |

### Configuration: `package.json`

**Commands**:
- `cloudguardian.scan` - Scan current file
- `cloudguardian.scanWorkspace` - Scan workspace
- `cloudguardian.clearDiagnostics` - Clear findings
- `cloudguardian.settings` - Open settings

**Keybindings**:
- `Ctrl+Shift+G` (Windows/Linux)
- `Cmd+Shift+G` (macOS)

**Configuration Schema**:
- `apiUrl` - Backend URL (default: http://localhost:8000)
- `apiToken` - JWT authentication token
- `enabled` - Enable/disable extension
- `scanOnSave` - Auto-scan on file save
- `scanOnOpen` - Auto-scan on file open

## 🔌 API Integration

### Backend Endpoint

**POST `/secrets/scan`**

Request:
```json
{
  "content": "file content here",
  "filename": "main.tf"
}
```

Response:
```json
{
  "secrets": [
    {
      "type": "AWS_KEY",
      "severity": "CRITICAL",
      "line_number": 5,
      "matched_string": "AKIA...",
      "description": "AWS Access Key detected"
    }
  ],
  "total_findings": 1
}
```

### Headers

```
Authorization: Bearer {api_token}
Content-Type: application/json
```

## 🎨 Diagnostics Rendering

The extension renders issues as VS Code diagnostics:

```typescript
// Severity Mapping
CRITICAL/HIGH → DiagnosticSeverity.Error (red underline)
MEDIUM       → DiagnosticSeverity.Warning (yellow)
LOW          → DiagnosticSeverity.Information (blue)
```

**Example Issue**:
```
Line 5: 🔐 AWS_KEY: AWS Access Key detected
```

## 📊 Status Bar Integration

```
✅ CloudGuardian: Clean         // No issues
⚠️  CloudGuardian: 2 issues      // Some issues
🚨 CloudGuardian: 5 issues      // Many issues
🔍 CloudGuardian: Scanning...   // In progress
❌ CloudGuardian: Error         // Error state
```

Click status bar to open settings.

## 🧪 Testing

### Run All Tests
```bash
npm test
```

### Test Structure

**File**: `src/test/extension.test.ts`

```typescript
// Tests verify:
- Extension loads correctly
- Commands register properly
- Configuration is accessible
- Commands execute without error
```

### Unit Test Example
```typescript
test('Should register commands', async () => {
    const commands = await vscode.commands.getCommands();
    assert.ok(commands.includes('cloudguardian.scan'));
});
```

## 🔧 Configuration Management

### Reading Configuration
```typescript
const config = vscode.workspace.getConfiguration('cloudguardian');
const apiUrl = config.get<string>('apiUrl') || 'http://localhost:8000';
const apiToken = config.get<string>('apiToken') || '';
```

### Listen for Config Changes
```typescript
vscode.workspace.onDidChangeConfiguration((event) => {
    if (event.affectsConfiguration('cloudguardian')) {
        scanner.loadConfig();
    }
});
```

## 🐛 Debugging

### Enable Debug Logging
In `src/extension.ts`, add:
```typescript
console.log('Debug message:', variable);
```

### View Debug Output
In VS Code: View → Debug Console (or `Ctrl+Shift+Y`)

### Debug Mode
- Press `F5` to start debugging
- Set breakpoints by clicking line numbers
- Inspect variables in Debug Sidebar

## 📝 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/my-feature
```

### 2. Make Changes
- Edit `src/extension.ts` or configuration
- Compile: `npm run compile`
- Test locally with `F5`

### 3. Add Tests
- Create test in `src/test/extension.test.ts`
- Run: `npm test`

### 4. Build VSIX
```bash
npm run package
```

### 5. Commit & Push
```bash
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

## 🎯 Common Tasks

### Add New Configuration Setting

**In `package.json`**:
```json
"cloudguardian.mySetting": {
  "type": "string",
  "default": "value",
  "description": "My setting description"
}
```

**In `extension.ts`**:
```typescript
const value = config.get<string>('mySetting');
```

### Add New Command

**In `package.json`**:
```json
{
  "command": "cloudguardian.myCommand",
  "title": "CloudGuardian: My Command"
}
```

**In `extension.ts`**:
```typescript
context.subscriptions.push(
  vscode.commands.registerCommand('cloudguardian.myCommand', () => {
    // Command logic
  })
);
```

### Add Event Listener

```typescript
context.subscriptions.push(
  vscode.workspace.onDidSaveTextDocument(async (doc) => {
    // Handle file save
  })
);
```

## 📦 Build & Distribution

### Build VSIX Package
```bash
npm run package
```

Creates: `cloudguardian-vscode-1.0.0.vsix`

### Install Locally
```bash
code --install-extension cloudguardian-vscode-1.0.0.vsix
```

### Publish to Marketplace
```bash
npm run publish
```

(Requires VS Code publisher account)

## 🔐 Security Considerations

1. **Never log API tokens**
   ```typescript
   // ❌ WRONG
   console.log('Token:', apiToken);
   
   // ✅ CORRECT
   console.log('Scanning with authentication');
   ```

2. **Validate backend responses**
   ```typescript
   if (!response.data.secrets || !Array.isArray(response.data.secrets)) {
       throw new Error('Invalid response format');
   }
   ```

3. **Handle errors gracefully**
   ```typescript
   catch (error: any) {
       console.error('Scan error:', error);
       vscode.window.showErrorMessage('Scan failed');
   }
   ```

## 🚨 Error Handling

### Backend Connection Error
```typescript
catch (error: any) {
    if (error.code === 'ECONNREFUSED') {
        // Backend not running
        this.statusBar.text = '❌ Backend not running';
    }
}
```

### Timeout
```typescript
const response = await axios.post(..., {
    timeout: 10000  // 10 seconds
});
```

### Invalid Response
```typescript
if (!response.data || !response.data.secrets) {
    throw new Error('Invalid API response');
}
```

## 📚 VS Code Extension API Reference

### Important APIs Used

| API | Purpose |
|-----|---------|
| `vscode.languages.createDiagnosticCollection()` | Create diagnostic collection |
| `vscode.window.createStatusBarItem()` | Create status bar item |
| `vscode.commands.registerCommand()` | Register command |
| `vscode.workspace.onDidSaveTextDocument()` | Listen to save events |
| `vscode.window.showErrorMessage()` | Show error to user |
| `vscode.workspace.getConfiguration()` | Read settings |

## 🔗 Resources

- [VS Code API Documentation](https://code.visualstudio.com/api)
- [VS Code Extension Examples](https://github.com/microsoft/vscode-extension-samples)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Axios Documentation](https://axios-http.com/docs/intro)

## 📋 Checklist for New Features

- [ ] Code compiles without errors: `npm run compile`
- [ ] Tests pass: `npm test`
- [ ] No console errors in debug mode
- [ ] API token is not logged
- [ ] Error handling is comprehensive
- [ ] User feedback is provided (messages, status bar)
- [ ] Configuration is documented
- [ ] Keybindings are registered
- [ ] Commands are in Command Palette
- [ ] VSIX package builds: `npm run package`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Make changes and test locally
4. Commit with clear messages
5. Push to your fork
6. Open Pull Request with description

## 📞 Support

- **Issues**: https://github.com/cloudguardian/cloudguardian/issues
- **Discussions**: https://github.com/cloudguardian/discussions
- **Documentation**: https://docs.cloudguardian.io/vscode-extension
