    const refresh = root.querySelector('[data-action="refresh"]');
    const status = root.querySelector('#context-refresh-status');
    const auto = root.querySelector('[data-action="auto-refresh"]');
    const autoStatus = root.querySelector('#context-auto-status');
    const interval = 15000;
    let autoTimer = null, failures = 0, disposed = false;
    let sequence = 0, ready = false, busy = false;
    const pending = new Map();
    const notify = (method, params) => window.parent.postMessage({jsonrpc:'2.0',method,params}, '*');
    function request(method, params) {
      const id = ++sequence;
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {pending.delete(id); reject(new Error('Request timed out'));},20000);
        pending.set(id,{resolve,reject,timer});
        window.parent.postMessage({jsonrpc:'2.0',id,method,params},'*');
      });
    }
    function message(text) { status.hidden=false; status.textContent=text; }
    function availability() {
      refresh.disabled=!ready || busy || !data.thread_id;
      auto.disabled=!ready || !data.thread_id;
    }
    function schedule() {
      clearTimeout(autoTimer);autoTimer=null;
      if (disposed || !auto.checked) return;
      if (document.visibilityState === 'hidden') {
        autoStatus.textContent='Paused while hidden';return;
      }
      autoStatus.textContent='Every 15 seconds while visible';
      if (ready && data.thread_id && !busy) autoTimer=setTimeout(()=>refreshData(true),interval);
    }
    function theme(context) {
      if (!context) return;
      if (['light','dark'].includes(context.theme)) document.documentElement.style.colorScheme=context.theme;
      for (const [key,value] of Object.entries(context.styles?.variables || {})) {
        if (key.startsWith('--') && typeof value === 'string') document.documentElement.style.setProperty(key,value);
      }
    }
    function accept(result, automatic=false) {
      if (result?.isError || !result?.structuredContent) throw new Error('No telemetry returned');
      render(result.structuredContent);
      status.setAttribute('aria-live',automatic ? 'off' : 'polite');
      message(`Checked ${stamp(data.observed_at)}. ${data.status === 'ok' ? 'Recorded telemetry; unreported work is excluded.' : 'Telemetry unavailable.'}`);
      availability();
      schedule();
    }
    window.addEventListener('message', event => {
      if (event.source !== window.parent || event.data?.jsonrpc !== '2.0') return;
      const msg=event.data;
      if (pending.has(msg.id)) {
        const item=pending.get(msg.id); pending.delete(msg.id);clearTimeout(item.timer);
        msg.error ? item.reject(new Error(msg.error.message || 'Host error')) : item.resolve(msg.result);
      } else if (msg.method === 'ui/notifications/tool-result') {
        try {accept(msg.params);} catch {message('Unable to load the inspector. Retry Refresh when available.');}
      } else if (msg.method === 'ui/notifications/host-context-changed') theme(msg.params);
    });
    async function refreshData(automatic=false) {
      if (disposed || busy || !ready || !data.thread_id) return;
      if (automatic && (!auto.checked || document.visibilityState === 'hidden')) {schedule();return;}
      clearTimeout(autoTimer);autoTimer=null;
      busy=true;availability();refresh.textContent='Refreshing…';
      status.setAttribute('aria-live',automatic ? 'off' : 'polite');
      if (!automatic) message('Reading local telemetry…');
      try {
        accept(await request('tools/call',{name:'read_context_status',arguments:{thread_id:data.thread_id,timezone:data.display_timezone || 'UTC'}}),automatic);
        failures=0;
      } catch {
        failures++;
        if (auto.checked && failures>=3) {
          auto.checked=false;autoStatus.textContent='Stopped after 3 failed checks. Turn on to retry.';
          status.setAttribute('aria-live','polite');
          message('Auto-refresh stopped. Previous snapshot retained. You can retry Refresh.');
        } else message('Refresh failed. Previous snapshot retained.' + (auto.checked ? ' Retrying in 15 seconds.' : ' Try again.'));
      }
      finally {busy=false;refresh.textContent='Refresh';availability();schedule();}
    }
    refresh.addEventListener('click',()=>refreshData());
    auto.addEventListener('change',()=>{
      failures=0;
      autoStatus.textContent=auto.checked ? 'Every 15 seconds while visible' : 'Off · every 15 seconds when enabled';
      schedule();
    });
    document.addEventListener('visibilitychange',schedule);
    window.addEventListener('pagehide',()=>{disposed=true;clearTimeout(autoTimer);});
    window.addEventListener('pageshow',()=>{disposed=false;schedule();});
    message('Connecting to the local context-status app…');
    request('ui/initialize',{appInfo:{name:'Context status',version:'1.0.0'},appCapabilities:{},protocolVersion:'2026-01-26'})
      .then(result=>{theme(result?.hostContext);ready=true;notify('ui/notifications/initialized',{});availability();schedule();})
      .catch(()=>message('The MCP Apps connection is unavailable. Reopen the inspector in Codex.'));
    let lastHeight=0;
    new ResizeObserver(()=>{
      const height=Math.ceil(document.body.getBoundingClientRect().height);
      if(ready && height!==lastHeight){lastHeight=height;notify('ui/notifications/size-changed',{height});}
    }).observe(document.body);
