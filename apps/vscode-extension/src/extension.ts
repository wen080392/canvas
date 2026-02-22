import * as vscode from 'vscode';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/scan';

interface SecurityIssue {
	rule_id: string;
	severity: string;
	message: string;
	line_number?: number;
	fix_suggestion?: string;
}

export function activate(context: vscode.ExtensionContext) {
	console.log('CloudGuardian extension is now active!');

	const diagnosticCollection = vscode.languages.createDiagnosticCollection('cloudguardian');
	context.subscriptions.push(diagnosticCollection);

	// Command to manually trigger scan
	let disposable = vscode.commands.registerCommand('cloudguardian.scan', () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			scanDocument(editor.document, diagnosticCollection);
		}
	});
	context.subscriptions.push(disposable);

	// Scan on save
	vscode.workspace.onDidSaveTextDocument((document: vscode.TextDocument) => {
		if (document.languageId === 'terraform') {
			scanDocument(document, diagnosticCollection);
		}
	}, null, context.subscriptions);

	// Code Action Provider
	context.subscriptions.push(
		vscode.languages.registerCodeActionsProvider('terraform', new CloudGuardianCodeActionProvider(), {
			providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
		})
	);
}

async function scanDocument(document: vscode.TextDocument, collection: vscode.DiagnosticCollection) {
	try {
		const response = await axios.post<SecurityIssue[]>(API_URL, {
			content: document.getText()
		});

		const diagnostics: vscode.Diagnostic[] = [];

		for (const issue of response.data) {
			// If line number is missing, default to top of file
			const line = issue.line_number ? issue.line_number - 1 : 0;
			// Use actual line length instead of fixed 100
			const lineText = document.lineAt(line).text;
			const range = new vscode.Range(line, 0, line, lineText.length);

			const diagnostic = new vscode.Diagnostic(
				range,
				`${issue.rule_id}: ${issue.message}`,
				getSeverity(issue.severity)
			);

			diagnostic.source = 'CloudGuardian';
			// Store fix suggestion directly as code (string)
			diagnostic.code = issue.fix_suggestion || undefined;

			diagnostics.push(diagnostic);
		}

		collection.set(document.uri, diagnostics);

	} catch (error) {
		console.error('Error scanning document:', error);
		vscode.window.showErrorMessage('CloudGuardian: Failed to scan document. Is the backend running?');
	}
}

export function getSeverity(severity: string): vscode.DiagnosticSeverity {
	switch (severity) {
		case 'CRITICAL': return vscode.DiagnosticSeverity.Error;
		case 'HIGH': return vscode.DiagnosticSeverity.Error;
		case 'MEDIUM': return vscode.DiagnosticSeverity.Warning;
		case 'LOW': return vscode.DiagnosticSeverity.Information;
		default: return vscode.DiagnosticSeverity.Information;
	}
}

class CloudGuardianCodeActionProvider implements vscode.CodeActionProvider {
	provideCodeActions(document: vscode.TextDocument, range: vscode.Range | vscode.Selection, context: vscode.CodeActionContext, token: vscode.CancellationToken): vscode.ProviderResult<(vscode.Command | vscode.CodeAction)[]> {
		return context.diagnostics
			.filter((diagnostic: vscode.Diagnostic) => diagnostic.source === 'CloudGuardian' && diagnostic.code)
			.map((diagnostic: vscode.Diagnostic) => this.createFix(document, diagnostic));
	}

	private createFix(document: vscode.TextDocument, diagnostic: vscode.Diagnostic): vscode.CodeAction {
		// Extract fix suggestion from diagnostic code
		const fixContent = typeof diagnostic.code === 'string' ? diagnostic.code : String(diagnostic.code);
		const fix = new vscode.CodeAction(`Fix: Apply ${fixContent}`, vscode.CodeActionKind.QuickFix);
		fix.edit = new vscode.WorkspaceEdit();

		// This is a simplified fix application. In reality, we'd need to parse the HCL and insert it correctly.
		// For this MVP, we'll just append it or replace the line if we knew the exact range.

		fix.edit.insert(document.uri, diagnostic.range.end, `\n  # Fix: ${fixContent}`);

		fix.diagnostics = [diagnostic];
		return fix;
	}
}

export function deactivate() { }
