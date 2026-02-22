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
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = __importStar(require("vscode"));
const chai_1 = require("chai");
const extension_1 = require("./extension");
describe('Extension Tests', () => {
    it('should return Error severity for CRITICAL', () => {
        const severity = (0, extension_1.getSeverity)('CRITICAL');
        (0, chai_1.expect)(severity).to.equal(vscode.DiagnosticSeverity.Error);
    });
    it('should return Error severity for HIGH', () => {
        const severity = (0, extension_1.getSeverity)('HIGH');
        (0, chai_1.expect)(severity).to.equal(vscode.DiagnosticSeverity.Error);
    });
    it('should return Warning severity for MEDIUM', () => {
        const severity = (0, extension_1.getSeverity)('MEDIUM');
        (0, chai_1.expect)(severity).to.equal(vscode.DiagnosticSeverity.Warning);
    });
    it('should return Information severity for LOW', () => {
        const severity = (0, extension_1.getSeverity)('LOW');
        (0, chai_1.expect)(severity).to.equal(vscode.DiagnosticSeverity.Information);
    });
    it('should return Information severity for unknown values', () => {
        const severity = (0, extension_1.getSeverity)('UNKNOWN');
        (0, chai_1.expect)(severity).to.equal(vscode.DiagnosticSeverity.Information);
    });
});
//# sourceMappingURL=extension.test.js.map