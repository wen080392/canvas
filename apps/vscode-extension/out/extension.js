"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.getSeverity = getSeverity;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
const API_URL = 'http://localhost:8000/api/v1/scan';
function activate(context) {
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
    vscode.workspace.onDidSaveTextDocument((document) => {
        if (document.languageId === 'terraform') {
            scanDocument(document, diagnosticCollection);
        }
    }, null, context.subscriptions);
    // Code Action Provider
    context.subscriptions.push(vscode.languages.registerCodeActionsProvider('terraform', new CloudGuardianCodeActionProvider(), {
        providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
    }));
}
function scanDocument(document, collection) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const response = yield axios_1.default.post(API_URL, {
                content: document.getText()
            });
            const diagnostics = [];
            for (const issue of response.data) {
                // If line number is missing, default to top of file
                const line = issue.line_number ? issue.line_number - 1 : 0;
                // Use actual line length instead of fixed 100
                const lineText = document.lineAt(line).text;
                const range = new vscode.Range(line, 0, line, lineText.length);
                const diagnostic = new vscode.Diagnostic(range, `${issue.rule_id}: ${issue.message}`, getSeverity(issue.severity));
                diagnostic.source = 'CloudGuardian';
                // Store fix suggestion directly as code (string)
                diagnostic.code = issue.fix_suggestion || undefined;
                diagnostics.push(diagnostic);
            }
            collection.set(document.uri, diagnostics);
        }
        catch (error) {
            console.error('Error scanning document:', error);
            vscode.window.showErrorMessage('CloudGuardian: Failed to scan document. Is the backend running?');
        }
    });
}
function getSeverity(severity) {
    switch (severity) {
        case 'CRITICAL': return vscode.DiagnosticSeverity.Error;
        case 'HIGH': return vscode.DiagnosticSeverity.Error;
        case 'MEDIUM': return vscode.DiagnosticSeverity.Warning;
        case 'LOW': return vscode.DiagnosticSeverity.Information;
        default: return vscode.DiagnosticSeverity.Information;
    }
}
class CloudGuardianCodeActionProvider {
    provideCodeActions(document, range, context, token) {
        return context.diagnostics
            .filter((diagnostic) => diagnostic.source === 'CloudGuardian' && diagnostic.code)
            .map((diagnostic) => this.createFix(document, diagnostic));
    }
    createFix(document, diagnostic) {
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
function deactivate() { }
//# sourceMappingURL=extension.js.map