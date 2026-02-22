import moduleAlias from 'module-alias';
import * as path from 'path';

moduleAlias.addAlias('vscode', path.join(process.cwd(), 'src', 'test', 'vscode-mock.ts'));
