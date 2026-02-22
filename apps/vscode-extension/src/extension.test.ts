import * as vscode from 'vscode';
import { expect } from 'chai';
import { getSeverity } from './extension';

describe('Extension Tests', () => {
    it('should return Error severity for CRITICAL', () => {
        const severity = getSeverity('CRITICAL');
        expect(severity).to.equal(vscode.DiagnosticSeverity.Error);
    });

    it('should return Error severity for HIGH', () => {
        const severity = getSeverity('HIGH');
        expect(severity).to.equal(vscode.DiagnosticSeverity.Error);
    });

    it('should return Warning severity for MEDIUM', () => {
        const severity = getSeverity('MEDIUM');
        expect(severity).to.equal(vscode.DiagnosticSeverity.Warning);
    });

    it('should return Information severity for LOW', () => {
        const severity = getSeverity('LOW');
        expect(severity).to.equal(vscode.DiagnosticSeverity.Information);
    });

    it('should return Information severity for unknown values', () => {
        const severity = getSeverity('UNKNOWN');
        expect(severity).to.equal(vscode.DiagnosticSeverity.Information);
    });
});
