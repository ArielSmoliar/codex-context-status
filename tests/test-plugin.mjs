// Real Codex lifecycle, isolated from the user's configuration and session data.
import assert from 'node:assert/strict';
import {execFileSync, spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {cp, mkdir, readFile, writeFile, access} from 'node:fs/promises';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {Client} from '../mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {StdioClientTransport} from '../mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
import {makeFixture} from './fixture.mjs';

const root = fileURLToPath(new URL('..', import.meta.url));
const fixture = await makeFixture();
const home = fixture.home;
const repo = join(home, 'marketplace-source');
const pluginId = 'context-status@codex-context-status';
// Git uses a local transport for a synthetic HTTPS URL: exercises Codex's Git
// marketplace snapshots and upgrades without GitHub, credentials, or network.
const env = {PATH: process.env.PATH, HOME: process.env.HOME, CODEX_HOME: home,
  PYTHONDONTWRITEBYTECODE: '1', GIT_CONFIG_NOSYSTEM: '1',
  GIT_CONFIG_GLOBAL: join(home, 'gitconfig'), GIT_TERMINAL_PROMPT: '0'};
if (process.env.CONTEXT_STATUS_PYTHON) env.CONTEXT_STATUS_PYTHON = process.env.CONTEXT_STATUS_PYTHON;
const run = (command, args, cwd=home) => execFileSync(command, args,
  {cwd, env, encoding: 'utf8', timeout: 45000, stdio: ['ignore', 'pipe', 'pipe']});
const codex = (...args) => JSON.parse(run('codex', ['plugin', ...args, '--json']));
const git = (...args) => run('git', args, repo);

async function inspectHost(expected) {
  const child = spawn('codex', ['app-server', '--stdio'], {cwd: home, env, stdio: ['pipe','pipe','pipe']});
  const exited = new Promise(resolve => child.once('exit', resolve));
  const pending = new Map();
  let seq = 0;
  child.stderr.resume();
  const lines = createInterface({input: child.stdout});
  lines.on('line', line => {
    const message = JSON.parse(line);
    const callback = pending.get(message.id);
    if (callback) {pending.delete(message.id); callback(message);}
  });
  function call(method, params) {
    const id = ++seq;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {pending.delete(id); reject(new Error(`Timed out: ${method}`));}, 30000);
      pending.set(id, response => {clearTimeout(timer); response.error ? reject(new Error(JSON.stringify(response.error))) : resolve(response.result);});
      child.stdin.write(JSON.stringify({id, method, params})+'\n');
    });
  }
  try {
    await call('initialize', {clientInfo: {name: 'context-status-plugin-test', version: '1.0'}, capabilities: {experimentalApi: true}});
    const result = await call('mcpServerStatus/list', {});
    const server = result.data.find(item => item.pluginId === pluginId);
    if (!expected) {assert.equal(server, undefined); return;}
    assert.ok(server, 'Codex must discover the installed plugin MCP server');
    assert.equal(server.toolsError, null);
    assert.ok(server.tools.open_context_status);
    assert.ok(server.tools.read_context_status);
    assert.ok(server.resources.some(item => item.uri === 'ui://context-status/inspector-v1.html'));
    const skills = await call('skills/list', {cwds: [home], forceReload: true});
    assert.ok(JSON.stringify(skills).includes('context-status:context-status'), 'Codex discovers the namespaced skill');
  } finally {
    lines.close();
    child.kill();
    await exited;
  }
}

async function checkRuntime(installedPath, marker='') {
  // A fresh install cannot resolve dependencies from the developer checkout.
  await assert.rejects(access(join(installedPath, 'node_modules')));
  const manifest = JSON.parse(await readFile(join(installedPath, 'mcp.json'), 'utf8'));
  const server = manifest.mcpServers['context-status'];
  assert.equal(server.type, 'stdio');
  assert.equal(server.command, 'node');
  const args = server.args.map(arg => arg.replaceAll('${PLUGIN_ROOT}', installedPath));
  // Fail if bundled runtime tries network access (stdio and filesystem still work).
  const guard = join(home, 'deny-network.cjs');
  await writeFile(guard, `const deny=()=>{throw new Error('Unexpected network access');};
require('node:net').Socket.prototype.connect=deny;
require('node:http').request=deny; require('node:https').request=deny;
globalThis.fetch=deny;\n`);
  const client = new Client({name: 'plugin-install-test', version: '1.0'});
  const transport = new StdioClientTransport({command: process.execPath,
    args: ['--require', guard, ...args], cwd: home, env});
  try {
    await client.connect(transport);
    const response = await client.callTool({name: 'open_context_status', arguments: {thread_id: fixture.id, timezone: 'UTC'}});
    assert.equal(response.structuredContent.status, 'ok');
    assert.equal(response.structuredContent.capacity_estimate.used_tokens, 60000);
    assert.ok(!JSON.stringify(response).includes('PRIVATE_CONVERSATION_SENTINEL'));
    assert.ok(!JSON.stringify(response).includes(home));
    const fallback = JSON.parse(run(env.CONTEXT_STATUS_PYTHON || 'python3',
      [join(installedPath, 'skills/context-status/scripts/context_status.py'),
        '--thread-id', fixture.id, '--visualization', join(home, 'fallback.html')]));
    assert.equal(fallback.capacity_estimate.used_tokens, 60000);
    assert.ok((await readFile(join(home, 'fallback.html'), 'utf8')).includes('Context capacity'));
    const resource = await client.readResource({uri: 'ui://context-status/inspector-v1.html'});
    assert.ok(resource.contents[0].text.includes('Auto-refresh'));
    assert.deepEqual(resource.contents[0]._meta.ui.csp, {connectDomains: [], resourceDomains: []});
    if (marker) assert.ok(resource.contents[0].text.includes(marker));
    await fixture.write(61000);
    const refreshed = await client.callTool({name: 'read_context_status', arguments: {thread_id: fixture.id, timezone: 'UTC'}});
    assert.equal(refreshed.structuredContent.capacity_estimate.used_tokens, 61000);
    const missing = await client.callTool({name: 'read_context_status', arguments: {thread_id: '00000000-0000-4000-8000-000000000999', timezone: 'UTC'}});
    assert.equal(missing.structuredContent.status, 'unavailable');
    assert.equal(missing.structuredContent.capacity_estimate, null);
    await fixture.write(60000);
  } finally {await client.close();}
}

try {
  console.log(run('codex', ['--version']).trim());
  await mkdir(join(repo, '.agents/plugins'), {recursive: true});
  await cp(join(root, '.agents/plugins/marketplace.json'), join(repo, '.agents/plugins/marketplace.json'));
  await cp(join(root, 'plugins'), join(repo, 'plugins'), {recursive: true});
  await writeFile(env.GIT_CONFIG_GLOBAL, `[url "file://${repo}"]\n insteadOf = https://context-status-test.invalid/repo.git\n[protocol "file"]\n allow = always\n`);
  git('init', '-b', 'main');
  git('config', 'user.email', 'test@example.invalid');
  git('config', 'user.name', 'Synthetic test');
  git('add', '.'); git('commit', '-m', 'Plugin v1');
  const firstCommit = git('rev-parse', 'HEAD').trim();
  const plugin = join(repo, 'plugins/context-status');
  const manifest = JSON.parse(await readFile(join(plugin, 'plugin.json'), 'utf8'));
  const originalVersion = manifest.version;
  // Files from an existing standalone installation must survive every operation.
  await mkdir(join(home, 'skills/context-status'), {recursive: true});
  const sentinel = join(home, 'skills/context-status/local-note.txt');
  await writeFile(sentinel, 'keep my standalone files');
  await writeFile(join(home, 'config.toml'), 'model = "preserve-test-setting"\n[mcp_servers.unrelated]\ncommand = "unused-test-command"\nenabled = false\n');
  await fixture.append({type: 'response_item', payload: {type: 'message', content: 'PRIVATE_CONVERSATION_SENTINEL'}});

  const market = codex('marketplace', 'add', 'https://context-status-test.invalid/repo.git', '--ref', 'main');
  assert.notEqual(market.installedRoot, repo, 'Git marketplace must use a snapshot');
  const installed = codex('add', pluginId);
  assert.equal(installed.version, originalVersion);
  const log = join(home, 'sessions', `test-${fixture.id}.jsonl`);
  const before = await readFile(log, 'utf8');
  await inspectHost(true);
  assert.equal(await readFile(log, 'utf8'), before);
  await checkRuntime(installed.installedPath);
  console.log('PASS: Git marketplace install, real host discovery, offline bundled MCP, refresh and exact chat binding');

  // Publish a new version to the local Git source, then use actual Codex commands.
  const parts = originalVersion.split('.').map(Number);
  assert.ok(parts.length === 3 && parts.every(Number.isInteger));
  parts[2] += 1;
  manifest.version = parts.join('.');
  await writeFile(join(plugin, 'plugin.json'), JSON.stringify(manifest, null, 2)+'\n');
  const html = join(plugin, 'skills/context-status/mcp/inspector.html');
  await writeFile(html, (await readFile(html, 'utf8'))+'\n<!-- synthetic-upgrade-marker -->\n');
  git('add', '.'); git('commit', '-m', 'Plugin v2');
  codex('marketplace', 'upgrade', 'codex-context-status');
  const upgraded = codex('add', pluginId);
  assert.equal(upgraded.version, manifest.version);
  await inspectHost(true);
  await checkRuntime(upgraded.installedPath, 'synthetic-upgrade-marker');
  console.log('PASS: Git snapshot upgrade installs and serves the changed version');

  codex('marketplace', 'remove', 'codex-context-status');
  codex('marketplace', 'add', 'https://context-status-test.invalid/repo.git', '--ref', firstCommit);
  codex('marketplace', 'upgrade', 'codex-context-status');
  const rolledBack = codex('add', pluginId);
  assert.equal(rolledBack.version, originalVersion);
  assert.ok(!(await readFile(join(rolledBack.installedPath, 'skills/context-status/mcp/inspector.html'), 'utf8')).includes('synthetic-upgrade-marker'));
  console.log('PASS: pinned commit remains pinned and supports rollback');

  const preservedLog = await readFile(log, 'utf8');
  codex('remove', pluginId);
  codex('marketplace', 'remove', 'codex-context-status');
  await assert.rejects(access(installed.installedPath));
  await assert.rejects(access(upgraded.installedPath));
  await inspectHost(false);
  assert.equal(await readFile(log, 'utf8'), preservedLog);
  assert.equal(await readFile(sentinel, 'utf8'), 'keep my standalone files');
  const config = await readFile(join(home, 'config.toml'), 'utf8');
  assert.ok(config.includes('preserve-test-setting') && config.includes('mcp_servers.unrelated'));
  assert.ok(!config.includes('context-status@codex-context-status'));
  console.log('PASS: removal cleans both cached versions and discovery, preserves logs, standalone files and unrelated configuration');
} finally {await fixture.cleanup();}
