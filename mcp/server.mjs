import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { readFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

const exec = promisify(execFile);
const server = new McpServer({ name: 'context-status', version: '1.0.0' });
const uri = 'ui://context-status/inspector-v1.html';
const reader = fileURLToPath(new URL('../scripts/mcp_snapshot.py', import.meta.url));
const inputSchema = {
  thread_id: z.string().uuid().describe('Exact current Codex thread ID; never choose another chat.'),
  timezone: z.string().max(100).default('UTC').describe('Client IANA timezone'),
};
async function snapshot({ thread_id, timezone }) {
  try {
    const { stdout } = await exec(process.env.CONTEXT_STATUS_PYTHON || 'python3',
      [reader, '--thread-id', thread_id, '--timezone', timezone],
      { timeout: 15000, maxBuffer: 1024 * 1024 });
    const structuredContent = JSON.parse(stdout);
    return { structuredContent, content: [{ type: 'text', text:
      structuredContent.status === 'ok' ? 'Context inspector updated from local recorded telemetry. Capacity is estimated.' : structuredContent.reason }] };
  } catch {
    return { isError: true, content: [{ type: 'text', text: 'Could not read local telemetry. Check the local server and retry.' }] };
  }
}
server.registerResource('context-inspector', uri, { mimeType: 'text/html;profile=mcp-app' }, async () => ({
  contents: [{ uri, mimeType: 'text/html;profile=mcp-app',
    text: await readFile(new URL('./inspector.html', import.meta.url), 'utf8'),
    _meta: { ui: { prefersBorder: false, csp: { connectDomains: [], resourceDomains: [] } } } }],
}));
const annotations = { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true };
server.registerTool('open_context_status', {
  title: 'Context status', description: 'Open the context-status inspector for the exact current local Codex chat. Refresh updates this same view in place.',
  inputSchema, annotations,
  _meta: { ui: { resourceUri: uri }, 'openai/outputTemplate': uri },
}, snapshot);
server.registerTool('read_context_status', {
  title: 'Refresh context status', description: 'Reread recorded usage for the chat already bound to the context inspector. Returns data only.',
  inputSchema, annotations,
  _meta: { ui: { visibility: ['app'] }, 'openai/widgetAccessible': true },
}, snapshot);
await server.connect(new StdioServerTransport());
