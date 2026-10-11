import {execFileSync} from 'node:child_process';
import {symlink, readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {Client} from '../mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {StdioClientTransport} from '../mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
import {makeFixture} from './fixture.mjs';

const sandbox = await makeFixture();
const source = fileURLToPath(new URL('..', import.meta.url));
const target = join(sandbox.home, 'skills/context-status');
const client = new Client({name: 'installed-context-status-test', version: '1.0'});
try {
  const output = execFileSync(process.env.CONTEXT_STATUS_PYTHON || 'python3',
    [join(source, 'scripts/install.py'), '--codex-home', sandbox.home, '--apply'], {encoding: 'utf8'});
  assert.ok(output.includes('Files ready.'));
  // Reuse already installed test dependencies; the installer never downloads them.
  await symlink(join(source, 'mcp/node_modules'), join(target, 'mcp/node_modules'), 'dir');
  const transport = new StdioClientTransport({command: process.execPath,
    args: [join(target, 'mcp/server.mjs')], env: {...process.env, CODEX_HOME: sandbox.home}});
  await client.connect(transport);
  const response = await client.callTool({name: 'open_context_status',
    arguments: {thread_id: sandbox.id, timezone: 'UTC'}});
  assert.equal(response.structuredContent.status, 'ok');
  assert.equal(response.structuredContent.capacity_estimate.used_tokens, 60000);
  const resource = await client.readResource({uri: 'ui://context-status/inspector-v1.html'});
  assert.ok(resource.contents[0].text.includes('Auto-refresh'));
  await assert.rejects(readFile(join(sandbox.home, 'config.toml')), {code: 'ENOENT'});
  console.log('PASS: managed installed package serves real MCP telemetry and UI without changing configuration');
} finally {
  await client.close();
  await sandbox.cleanup();
}
