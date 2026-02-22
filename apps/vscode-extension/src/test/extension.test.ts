import * as assert from 'assert';
import * as vscode from 'vscode';
import { deactivate } from '../extension';

suite('CloudGuardian Extension Tests', () => {
	let extension: vscode.Extension<any> | undefined;

	suiteSetup(async () => {
		extension = vscode.extensions.getExtension('cloudguardian.cloudguardian');
		if (!extension) {
			throw new Error('CloudGuardian extension not found');
		}
		await extension.activate();
	});

	suiteTeardown(() => {
		deactivate();
	});

	test('Extension should be present', () => {
		assert.ok(extension);
	});

	test('Should register commands', async () => {
		if (!extension) {
			throw new Error('CloudGuardian extension not found');
		}
		const commands = await vscode.commands.getCommands();
		assert.ok(commands.includes('cloudguardian.scan'));
		assert.ok(commands.includes('cloudguardian.scanWorkspace'));
		assert.ok(commands.includes('cloudguardian.clearDiagnostics'));
		assert.ok(commands.includes('cloudguardian.settings'));
	});

	test('Should have configuration schema', () => {
		const config = vscode.workspace.getConfiguration('cloudguardian');
		assert.ok(config);
		assert.ok(config.get('apiUrl') !== undefined);
		assert.ok(config.get('enabled') !== undefined);
	});

	test('Scan command should execute', async () => {
		// This test verifica se o comando registra corretamente
		await vscode.commands.executeCommand('cloudguardian.scan');
		assert.ok(true);
	});
});
