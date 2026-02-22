import * as vscode from 'vscode';
import axios from 'axios';

interface SecurityIssue {
	type: string;
	severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
	line_number?: number;
	matched_string: string;
	description: string;
}

interface ScanResponse {
	secrets: SecurityIssue[];
	total_findings: number;
	success?: boolean;
}

class CloudGuardianScanner {
	private diagnosticCollection: vscode.DiagnosticCollection;
	private statusBar: vscode.StatusBarItem;
	private apiUrl: string = 'http://localhost:8000';
	private apiToken: string = '';
	// private context: vscode.ExtensionContext;

	constructor() {
		this.diagnosticCollection = vscode.languages.createDiagnosticCollection('cloudguardian');
		this.statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
		this.loadConfig();
	}

	private loadConfig() {
		const config = vscode.workspace.getConfiguration('cloudguardian');
		this.apiUrl = config.get<string>('apiUrl') || 'http://localhost:8000';
		this.apiToken = config.get<string>('apiToken') || '';
	}

	async scanDocument(document: vscode.TextDocument) {
		const config = vscode.workspace.getConfiguration('cloudguardian');
		
		// Skip if extension is disabled
		if (!config.get<boolean>('enabled', true)) {
			return;
		}

		// Skip if no token configured
		if (!this.apiToken) {
			this.statusBar.text = '⚠️ CloudGuardian: Configure API token';
			this.statusBar.tooltip = 'Click to open settings';
			this.statusBar.command = 'cloudguardian.settings';
			this.statusBar.show();
			return;
		}

		try {
			this.statusBar.text = '🔍 CloudGuardian: Scanning...';
			this.statusBar.tooltip = 'Scanning file for secrets and vulnerabilities';
			this.statusBar.show();

			const response = await axios.post<ScanResponse>(`${this.apiUrl}/secrets/scan`, {
				content: document.getText(),
				filename: document.fileName
			}, {
				headers: {
					'Authorization': `Bearer ${this.apiToken}`,
					'Content-Type': 'application/json'
				},
				timeout: 10000
			});

			this.displayDiagnostics(document, response.data);
			this.updateStatusBar(response.data.total_findings);

		} catch (error: any) {
			const message = error.response?.data?.detail || error.message || 'Unknown error';
			console.error('CloudGuardian scan error:', error);
			
			if (error.code === 'ECONNREFUSED') {
				this.statusBar.text = '❌ CloudGuardian: Backend not running';
				this.statusBar.tooltip = 'Start backend at http://localhost:8000';
			} else {
				this.statusBar.text = '❌ CloudGuardian: Error';
				this.statusBar.tooltip = message;
			}
			this.statusBar.show();
		}
	}

	private displayDiagnostics(document: vscode.TextDocument, data: ScanResponse) {
		const diagnostics: vscode.Diagnostic[] = [];

		(data.secrets || []).forEach((issue: SecurityIssue) => {
			const line = Math.max(0, (issue.line_number || 1) - 1);
			const lineLength = document.lineAt(line).text.length;
			const range = new vscode.Range(line, 0, line, lineLength);

			const severity = this.mapSeverity(issue.severity);
			const message = `🔐 ${issue.type}: ${issue.description}`;

			const diagnostic = new vscode.Diagnostic(range, message, severity);
			diagnostic.code = issue.type;
			diagnostic.source = 'CloudGuardian';

			diagnostics.push(diagnostic);
		});

		this.diagnosticCollection.set(document.uri, diagnostics);
	}

	private mapSeverity(severity: string): vscode.DiagnosticSeverity {
		switch (severity) {
			case 'CRITICAL':
			case 'HIGH':
				return vscode.DiagnosticSeverity.Error;
			case 'MEDIUM':
				return vscode.DiagnosticSeverity.Warning;
			case 'LOW':
				return vscode.DiagnosticSeverity.Information;
			default:
				return vscode.DiagnosticSeverity.Information;
		}
	}

	private updateStatusBar(findings: number) {
		if (findings === 0) {
			this.statusBar.text = '✅ CloudGuardian: Clean';
			this.statusBar.color = new vscode.ThemeColor('terminal.ansiGreen');
		} else if (findings <= 3) {
			this.statusBar.text = `⚠️  CloudGuardian: ${findings} issue${findings !== 1 ? 's' : ''}`;
			this.statusBar.color = new vscode.ThemeColor('terminal.ansiYellow');
		} else {
			this.statusBar.text = `🚨 CloudGuardian: ${findings} issues`;
			this.statusBar.color = new vscode.ThemeColor('terminal.ansiRed');
		}
		this.statusBar.show();
	}

	async scanWorkspace() {
		const pattern = '**/*.{tf,py,js,ts,json,yml,yaml,env}';
		const files = await vscode.workspace.findFiles(pattern);

		if (files.length === 0) {
			vscode.window.showInformationMessage('CloudGuardian: No files to scan');
			return;
		}

		const limit = Math.min(files.length, 20);
		let scannedCount = 0;

		for (let i = 0; i < limit; i++) {
			const file = files[i];
			try {
				const doc = await vscode.workspace.openTextDocument(file);
				await this.scanDocument(doc);
				scannedCount++;
			} catch (error) {
				console.error(`Failed to scan ${file.fsPath}:`, error);
			}
		}

		vscode.window.showInformationMessage(
			`✅ CloudGuardian: Scanned ${scannedCount} of ${files.length} files`
		);
	}

	clear() {
		this.diagnosticCollection.clear();
		this.statusBar.text = '⚪ CloudGuardian: Ready';
		this.statusBar.show();
	}

	dispose() {
		this.diagnosticCollection.dispose();
		this.statusBar.dispose();
	}
}

let scanner: CloudGuardianScanner;

export function activate(context: vscode.ExtensionContext) {
	console.log('🛡️ CloudGuardian extension activated!');

	scanner = new CloudGuardianScanner(context);
	context.subscriptions.push(scanner);

	// Command: Scan current file
	context.subscriptions.push(
		vscode.commands.registerCommand('cloudguardian.scan', async () => {
			const editor = vscode.window.activeTextEditor;
			if (editor) {
				await scanner.scanDocument(editor.document);
			} else {
				vscode.window.showWarningMessage('CloudGuardian: No file open');
			}
		})
	);

	// Command: Scan workspace
	context.subscriptions.push(
		vscode.commands.registerCommand('cloudguardian.scanWorkspace', async () => {
			vscode.window.showInformationMessage('🔍 CloudGuardian: Scanning workspace...');
			await scanner.scanWorkspace();
		})
	);

	// Command: Clear diagnostics
	context.subscriptions.push(
		vscode.commands.registerCommand('cloudguardian.clearDiagnostics', () => {
			scanner.clear();
			vscode.window.showInformationMessage('✅ CloudGuardian: Diagnostics cleared');
		})
	);

	// Command: Open settings
	context.subscriptions.push(
		vscode.commands.registerCommand('cloudguardian.settings', () => {
			vscode.commands.executeCommand('workbench.action.openSettings', 'cloudguardian');
		})
	);

	// Scan on save
	context.subscriptions.push(
		vscode.workspace.onDidSaveTextDocument(async (document: vscode.TextDocument) => {
			const config = vscode.workspace.getConfiguration('cloudguardian');
			if (config.get<boolean>('scanOnSave', true)) {
				await scanner.scanDocument(document);
			}
		})
	);

	// Scan on open
	context.subscriptions.push(
		vscode.workspace.onDidOpenTextDocument(async (document: vscode.TextDocument) => {
			const config = vscode.workspace.getConfiguration('cloudguardian');
			if (config.get<boolean>('scanOnOpen', false)) {
				await scanner.scanDocument(document);
			}
		})
	);

	// Config change listener
	context.subscriptions.push(
		vscode.workspace.onDidChangeConfiguration((event) => {
			if (event.affectsConfiguration('cloudguardian')) {
				console.log('🔄 CloudGuardian: Configuration updated');
				scanner['loadConfig']();
			}
		})
	);
}

export function deactivate() {
	console.log('🛡️ CloudGuardian extension deactivated');
	if (scanner) {
		scanner.dispose();
	}
}
