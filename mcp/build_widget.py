"""Build the MCP App using the same chart markup and accounting as the fallback."""
from pathlib import Path

here = Path(__file__).resolve().parent
source = (here.parent / 'assets/inspector.html').read_text()
source = source.replace('  <script type="application/json" id="context-status-data">@@CONTEXT_STATUS_DATA@@</script>\n', '')
source = source.replace("const data = JSON.parse(root.querySelector('#context-status-data').textContent);", 'let data = {};')
begin = source.index("    el('model').textContent")
refresh_begin = source.index("    const refresh =", begin)
refresh_end = source.index("    if (data.status !== 'ok')", refresh_begin)
source = source[:refresh_begin] + source[refresh_end:]
end = source.index("    const details=root.querySelector('details');")
source = source[:end] + '    }\n' + (here / 'bridge.js').read_text() + '\n  })();\n  </script>\n</div>'
reset = '''
    function render(next) {
      if (!next || typeof next !== 'object' || !next.thread_id) return;
      if (data.thread_id && next.thread_id !== data.thread_id) throw new Error('Chat binding changed');
      data = next;
      for (const name of ['capacity-legend','accounting','provenance']) section(name).replaceChildren();
      for (const chart of root.querySelectorAll('[data-chart]')) {chart.replaceChildren();chart.removeAttribute('hidden');}
      section('capacity-scale').hidden=false;
      section('measurements').hidden=true;
      el('unavailable').hidden=true;
      el('cache-cached').textContent=''; el('cache-fresh').textContent='';
'''
source = source[:begin] + reset + source[begin:]
source = source.replace('aria-describedby="context-refresh-status">Refresh', 'aria-describedby="context-refresh-status" disabled>Refresh')
source = source.replace('    <div id="context-refresh-status"', '''    <div class="cs-auto-row">
      <label class="cs-auto-label"><input type="checkbox" data-action="auto-refresh" aria-describedby="context-auto-status" checked disabled> Auto-refresh</label>
      <span id="context-auto-status" class="text-small text-muted">Every 15 seconds while visible</span>
    </div>
    <div id="context-refresh-status"''')
base = (here / 'theme.css').read_text()
(here / 'inspector.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+base+'</style></head><body>'+source+'</body></html>')
