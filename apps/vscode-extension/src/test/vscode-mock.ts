// Mock vscode module
export enum DiagnosticSeverity {
    Error = 0,
    Warning = 1,
    Information = 2,
    Hint = 3
}

export const window = {
    showErrorMessage: (message: string) => console.error(message)
};

export const Range = class {
    constructor(public startLine: number, public startChar: number, public endLine: number, public endChar: number) { }
};

export const Diagnostic = class {
    constructor(public range: any, public message: string, public severity: DiagnosticSeverity) { }
};

export const Uri = {
    parse: (value: string) => value
};
