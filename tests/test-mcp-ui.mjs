import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import { makeFixture } from './fixture.mjs';
import { Client } from '../mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import { StdioClientTransport } from '../mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
import { chromium } from 'playwright';
const sandbox=await makeFixture(60000);
const {id,home}=sandbox;
const fixture=(used,withUsage=true)=>sandbox.write(used,withUsage);
const client=new Client({name:'browser-test',version:'1'});
await client.connect(new StdioClientTransport({command:process.execPath,args:[fileURLToPath(new URL('../mcp/server.mjs',import.meta.url))],env:{...process.env,CODEX_HOME:home}}));
const browser=await chromium.launch({headless:true,...(process.env.CHROME_EXECUTABLE_PATH ? {executablePath:process.env.CHROME_EXECUTABLE_PATH} : {})});
try{
 const page=await browser.newPage({viewport:{width:800,height:950}});
 await page.clock.install();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 let calls=0, fail=false;
 await page.exposeFunction('readTool',async params=>{calls++; if(fail)throw new Error('test failure');return client.callTool(params);});
 const html=await readFile(new URL('../mcp/inspector.html',import.meta.url),'utf8');
 const initial=await client.callTool({name:'open_context_status',arguments:{thread_id:id,timezone:'America/New_York'}});
 await page.setContent('<html><body style="margin:0"><iframe title="Context status" style="border:0;width:100%;height:930px"></iframe></body></html>');
 await page.evaluate(({html,initial})=>{
   window.bridgeMethods=[];
   window.addEventListener('message',async e=>{
     const m=e.data;if(m?.jsonrpc!=='2.0')return;
     window.bridgeMethods.push(m.method);
     const reply=result=>e.source.postMessage({jsonrpc:'2.0',id:m.id,result},'*');
     if(m.method==='ui/initialize')reply({hostContext:{theme:'light'}});
     if(m.method==='ui/notifications/initialized')e.source.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:initial},'*');
     if(m.method==='ui/notifications/size-changed' && m.params?.height)document.querySelector('iframe').style.height=m.params.height+'px';
     if(m.method==='tools/call'){
       try{reply(await window.readTool(m.params));}
       catch{e.source.postMessage({jsonrpc:'2.0',id:m.id,error:{message:'fixture error'}},'*');}
     }
   });
   document.querySelector('iframe').srcdoc=html;
 },{html,initial});
 const frame=page.frameLocator('iframe');
 await frame.getByRole('button',{name:'Refresh context status'}).waitFor();
 await frame.getByText(/Continue this session/).waitFor();
 const raw=page.frames()[1];
 await raw.evaluate(()=>window.originalRoot=document.getElementById('context-status-inspector'));
 await frame.getByText('Token accounting & provenance',{exact:true}).click();
 await fixture(85000);
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.locator('[data-field="session-guidance"]').filter({hasText:'Prepare a handoff'}).waitFor();
 assert.equal(await raw.evaluate(()=>window.originalRoot===document.getElementById('context-status-inspector')),true);
 assert.equal(await frame.locator('[data-section="accounting-details"]').getAttribute('open'),'');
 assert.equal(await frame.locator('tbody tr').count(),6);
 assert.equal(await frame.locator('[data-chart="capacity"] rect').count(),4);
 assert.equal(await page.locator('iframe').count(),1);
 fail=true;
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText(/Previous snapshot retained/).waitFor();
 await frame.locator('[data-field="session-guidance"]').filter({hasText:'Prepare a handoff'}).waitFor();
 fail=false;await fixture(93000);
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText(/Start a new session soon/).waitFor();
 await page.screenshot({path:home+'/inspector-light.png'});
 await fixture(0,false);
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText('The verified log contains no supported usage measurements.').waitFor();
 assert.equal(await frame.locator('[data-section="measurements"]').isVisible(),false);
 await fixture(40000);
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText(/Continue this session/).waitFor();
 await page.evaluate(()=>document.querySelector('iframe').contentWindow.postMessage({jsonrpc:'2.0',method:'ui/notifications/host-context-changed',params:{theme:'dark'}},'*'));
 await page.setViewportSize({width:320,height:1100});
 assert.equal(await raw.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true);
 await page.screenshot({path:home+'/inspector-dark-narrow.png'});
 const methods=await page.evaluate(()=>window.bridgeMethods);
 assert.equal(methods.filter(x=>x==='ui/initialize').length,1);
 assert.equal(methods.filter(x=>x==='tools/call').length,5);
 assert.equal(methods.some(x=>x==='ui/message'),false);
 assert.deepEqual(errors,[]);
 assert.equal(calls,5);
 const toggle=frame.getByRole('checkbox',{name:'Auto-refresh'});
 assert.equal(await toggle.isChecked(),true);
 await fixture(81000);
 await page.clock.runFor(15000);
 await frame.locator('[data-field="session-guidance"]').filter({hasText:'Prepare a handoff'}).waitFor();
 assert.equal(calls,6);
 assert.equal(await raw.evaluate(()=>window.originalRoot===document.getElementById('context-status-inspector')),true);
 await raw.evaluate(()=>{Object.defineProperty(document,'visibilityState',{configurable:true,value:'hidden'});document.dispatchEvent(new Event('visibilitychange'));});
 await page.clock.runFor(60000);assert.equal(calls,6);
 await frame.getByText('Paused while hidden').waitFor();
 await raw.evaluate(()=>{Object.defineProperty(document,'visibilityState',{configurable:true,value:'visible'});document.dispatchEvent(new Event('visibilitychange'));});
 await fixture(92000);
 await page.clock.runFor(15000);await frame.getByText(/Start a new session soon/).waitFor();
 assert.equal(calls,7);
 await toggle.uncheck();await page.clock.runFor(60000);assert.equal(calls,7);
 await toggle.check();fail=true;
 for(let n=0;n<3;n++){
   await page.clock.runFor(15000);
   await frame.getByText(n===2 ? /Auto-refresh stopped/ : /Retrying in 15 seconds/).waitFor();
 }
 assert.equal(await toggle.isChecked(),false);
 assert.equal(calls,10);await page.clock.runFor(60000);assert.equal(calls,10);
 fail=false;await toggle.check();await fixture(50000);
 await page.clock.runFor(15000);await frame.getByText(/Continue this session/).waitFor();
 assert.equal(calls,11);
 await page.screenshot({path:home+'/auto-refresh-narrow.png'});
 assert.deepEqual(errors,[]);
 assert.equal((await page.evaluate(()=>window.bridgeMethods)).some(x=>x==='ui/message'),false);
 await toggle.uncheck();
 await sandbox.append({type:'turn_context',payload:{model:'Second model',effort:'medium',turn_id:'two'}});
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText('Waiting for usage from Second model. Latest measurements belong to Test model.').waitFor();
 assert.equal(await frame.locator('[data-chart="capacity"]').isVisible(),false);
 await frame.getByText('Latest request model: Test model · Before the model change').waitFor();
 await frame.getByText('Telemetry checks & model changes',{exact:true}).click();
 await frame.getByText(/Test model → Second model/).waitFor();
 assert.match(await frame.locator('[data-section="diagnostics"]').innerText(),/Not observed/);
 if(process.env.TEST_SCREENSHOT) {
   await frame.getByText('Token accounting & provenance',{exact:true}).click();
   await page.setViewportSize({width:800,height:1000});
   await page.screenshot({path:process.env.TEST_SCREENSHOT,fullPage:true});
 }
 await sandbox.append({type:'event_msg',payload:{type:'token_count',info:{model_context_window:200000,last_token_usage:{input_tokens:20000,cached_input_tokens:15000,output_tokens:1000,total_tokens:21000}}}});
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText('Latest request model: Second model',{exact:true}).waitFor();
 assert.equal(await frame.locator('[data-field="model-notice"]').isVisible(),false);
 assert.equal(await frame.locator('[data-chart="capacity"]').isVisible(),true);
 assert.equal(await frame.locator('[data-section="model-switches"] li').count(),1);
 await sandbox.append({type:'event_msg',payload:{type:'token_count',info:{last_token_usage:{future_counter:999}}}});
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText('A newer usage record has no readable counters. Refresh after valid telemetry is recorded.').waitFor();
 assert.equal(await frame.locator('[data-chart="capacity"]').isVisible(),false);
 await frame.getByText(/Timing unavailable/).waitFor();
 assert.match(await frame.locator('[data-section="diagnostics"]').innerText(),/1 unreadable measurements/);
 assert.equal(await raw.evaluate(()=>window.originalRoot===document.getElementById('context-status-inspector')),true);
 await sandbox.append({type:'token_usage_record',payload:{thread_id:id,turn_id:'two',usage:{total_tokens:30000}}});
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText(/Continue this session/).waitFor();
 assert.equal(await frame.locator('[data-chart="capacity"]').isVisible(),true);
 await fixture(0,false);
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText('The verified log contains no supported usage measurements.').waitFor();
 assert.equal(await frame.locator('[data-section="diagnostics"]').isVisible(),true);
 assert.equal(await frame.locator('[data-section="model-switches"] li').count(),0);
 assert.deepEqual(errors,[]);
 const advice=frame.locator('[data-field="session-guidance"]');
 const reason=frame.locator('[data-field="session-reason"]');
 const intent=frame.getByLabel('Next step');
 // Advice and handoff remain usable even with no measurements.
 assert.equal(await advice.innerText(),'Timing unavailable');
 await intent.selectOption('unrelated');
 assert.equal(await advice.innerText(),'Start a new session for the new task');
 await frame.getByText('Handoff checklist & prompt',{exact:true}).click();
 const prompt=frame.getByLabel('Prompt to paste into the current chat');
 const promptText=await prompt.inputValue();
 assert.match(promptText,/first concrete next action/);
 assert.doesNotMatch(promptText,new RegExp(id));
 // Explicit copy is the only write; no message or model call is sent.
 const beforeCopy=calls;
 await raw.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.copiedPrompt=text;}}}));
 await frame.getByRole('button',{name:'Copy handoff prompt'}).click();
 await frame.getByText('Copied. Paste it into the current chat when ready.').waitFor();
 assert.equal(await raw.evaluate(()=>window.copiedPrompt),promptText);
 await raw.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new Error('denied');}}}));
 await frame.getByRole('button',{name:'Copy handoff prompt'}).click();
 await frame.getByText(/Clipboard unavailable/).waitFor();
 assert.equal(await prompt.evaluate(e=>document.activeElement===e && e.selectionStart===0 && e.selectionEnd===e.value.length),true);
 assert.equal(calls,beforeCopy);
 await fixture(60000);
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await frame.getByText('60.0% used · 40,000 remaining',{exact:true}).waitFor();
 assert.equal(await intent.inputValue(),'unrelated');
 assert.equal(await advice.innerText(),'Start a new session for the new task');
 assert.equal(await frame.locator('[data-section="handoff-details"]').getAttribute('open'),'');
 assert.equal(await prompt.inputValue(),promptText);
 await toggle.check();
 await fixture(70000);await page.clock.runFor(15000);
 await frame.getByText('70.0% used · 30,000 remaining',{exact:true}).waitFor();
 assert.equal(await intent.inputValue(),'unrelated');
 assert.equal(await frame.locator('[data-section="handoff-details"]').getAttribute('open'),'');
 assert.equal(await prompt.inputValue(),promptText);
 await toggle.uncheck();
 await intent.selectOption('large');
 assert.equal(await advice.innerText(),'Plan the next step before continuing');
 await intent.selectOption('continue');
 for(const [used,title] of [[79999,'Continue this session'],[80000,'Prepare a handoff'],[89999,'Prepare a handoff'],[90000,'Start a new session soon'],[110000,'Start a new session soon']]){
   await fixture(used);
   await frame.getByRole('button',{name:'Refresh context status'}).click();
   // Wait for the completed request, including when the title stays the same.
   await frame.locator('[data-action="refresh"]:enabled').waitFor();
   await frame.locator('[data-field="capacity-value"]').filter({hasText:(used/1000).toFixed(1)+'%'}).waitFor();
   assert.equal(await advice.innerText(),title);
 }
 await fixture(85000);
 await frame.getByRole('button',{name:'Refresh context status'}).click();
 await advice.filter({hasText:'Prepare a handoff'}).waitFor();
 await intent.selectOption('large');
 assert.match(await reason.innerText(),/large step with limited estimated headroom/);
 // All waiting states suppress capacity advice; never use the old estimate.
 for(const [state,expected] of [['awaiting_model_usage','model changed'],['awaiting_post_compaction_usage','Compaction was recorded'],['awaiting_readable_usage','unreadable']]){
   const result=await client.callTool({name:'read_context_status',arguments:{thread_id:id}});
   result.structuredContent.usage_state=state;
   result.structuredContent.capacity_estimate=null;
   await page.evaluate(result=>document.querySelector('iframe').contentWindow.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:result},'*'),result);
   await reason.filter({hasText:expected}).waitFor();
   assert.equal(await advice.innerText(),'Timing unavailable');
   assert.equal(await intent.inputValue(),'large');
 }
 const compacted=await client.callTool({name:'read_context_status',arguments:{thread_id:id}});
 compacted.structuredContent.compactions_observed=4;
 await page.evaluate(result=>document.querySelector('iframe').contentWindow.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:result},'*'),compacted);
 await reason.filter({hasText:'count alone does not require a new chat'}).waitFor();
 assert.equal(await advice.innerText(),'Prepare a handoff');
 await frame.getByText('Token accounting & provenance',{exact:true}).click();
 await frame.getByText('Telemetry checks & model changes',{exact:true}).click();
 await intent.focus();
 for(const width of [800,320]){
   await page.setViewportSize({width,height:1100});
   for(const theme of ['light','dark']){
     await page.evaluate(theme=>document.querySelector('iframe').contentWindow.postMessage({jsonrpc:'2.0',method:'ui/notifications/host-context-changed',params:{theme}},'*'),theme);
     assert.equal(await raw.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
     if(process.env.ADVICE_SCREENSHOTS)await page.screenshot({path:process.env.ADVICE_SCREENSHOTS+`/advice-${theme}-${width}.png`,fullPage:true});
   }
 }
 assert.equal((await page.evaluate(()=>window.bridgeMethods)).some(x=>x==='ui/message'),false);
 assert.deepEqual(errors,[]);
 // The shared inline fallback also offers advice without needing MCP or clipboard access.
 const fallback=await browser.newPage();
 fallback.on('pageerror',e=>errors.push(e.message));
 const template=await readFile(new URL('../assets/inspector.html',import.meta.url),'utf8');
 await fallback.setContent(template.replace('@@CONTEXT_STATUS_DATA@@',JSON.stringify({status:'unavailable',reason:'No local log'})));
 assert.equal(await fallback.locator('[data-field="session-guidance"]').innerText(),'Timing unavailable');
 await fallback.getByLabel('Next step').selectOption('unrelated');
 assert.equal(await fallback.locator('[data-field="session-guidance"]').innerText(),'Start a new session for the new task');
 await fallback.getByText('Handoff checklist & prompt',{exact:true}).focus();
 await fallback.keyboard.press('Enter');
 assert.equal(await fallback.locator('[data-section="handoff-details"]').getAttribute('open'),'');
 await fallback.getByRole('button',{name:'Copy handoff prompt'}).focus();
 await fallback.keyboard.press('Enter');
 await fallback.getByText(/Clipboard unavailable/).waitFor();
 assert.equal(await fallback.getByLabel('Prompt to paste into the current chat').inputValue(),promptText);
 assert.deepEqual(errors,[]);
 await fallback.evaluate(()=>{window.openai={widgetState:{privateContent:{kind:'context-status-v1',detailsOpen:true}},setWidgetState:async state=>{window.savedState=state;}};});
 await fallback.setContent(template.replace('@@CONTEXT_STATUS_DATA@@',JSON.stringify(compacted.structuredContent)));
 assert.equal(await fallback.locator('[data-section="accounting-details"]').isVisible(),true);
 assert.equal(await fallback.locator('[data-section="accounting-details"]').getAttribute('open'),'');
 assert.equal(await fallback.locator('[data-section="handoff-details"]').getAttribute('open'),null);
 await fallback.close();
 console.log('PASS: task intent, threshold boundaries, unavailable guidance, compaction caveat, handoff copy/fallback, state retained, 320px');
 console.log('PASS: model change waiting state, cache attribution, history, recovery, diagnostics without usage');
 console.log('PASS: unreadable usage suppresses capacity advice, diagnostic evidence survives, valid telemetry recovers in place');
 console.log('PASS: auto-refresh enabled by default, timer refresh, same DOM, hidden pause/resume, off stops, 3-error stop, reenable recovery');
 console.log('PASS: real stdio refresh, same DOM, preserved details, no new chat messages, 80/90% guidance, retry, unavailable recovery, light/dark, 320px');
}finally{await browser.close();await client.close();await sandbox.cleanup();}
