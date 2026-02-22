"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Uri = exports.Diagnostic = exports.Range = exports.window = exports.DiagnosticSeverity = void 0;
// Mock vscode module
var DiagnosticSeverity;
(function (DiagnosticSeverity) {
    DiagnosticSeverity[DiagnosticSeverity["Error"] = 0] = "Error";
    DiagnosticSeverity[DiagnosticSeverity["Warning"] = 1] = "Warning";
    DiagnosticSeverity[DiagnosticSeverity["Information"] = 2] = "Information";
    DiagnosticSeverity[DiagnosticSeverity["Hint"] = 3] = "Hint";
})(DiagnosticSeverity || (exports.DiagnosticSeverity = DiagnosticSeverity = {}));
exports.window = {
    showErrorMessage: (message) => console.error(message)
};
const Range = class {
    constructor(startLine, startChar, endLine, endChar) {
        this.startLine = startLine;
        this.startChar = startChar;
        this.endLine = endLine;
        this.endChar = endChar;
    }
};
exports.Range = Range;
const Diagnostic = class {
    constructor(range, message, severity) {
        this.range = range;
        this.message = message;
        this.severity = severity;
    }
};
exports.Diagnostic = Diagnostic;
exports.Uri = {
    parse: (value) => value
};
//# sourceMappingURL=vscode-mock.js.map