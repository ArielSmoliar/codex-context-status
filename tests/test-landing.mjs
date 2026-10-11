import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile, mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {chromium} from 'playwright';

const root=resolve('site');
const types={'/':'text/html','/index.html':'text/html','/style.css':'text/css','/script.js':'text/javascript','/icon.svg':'image/svg+xml'};
const server=createServer(async(req,res)=>{
  if(!Object.hasOwn(types,req.url)){res.writeHead(404).end();return;}
  try{res.setHeader('Content-Type',types[req.url]);res.end(await readFile(resolve(root,req.url==='/'?'index.html':req.url.slice(1))));}
  catch{res.writeHead(500).end();}
});
await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
let browser;
try{
  browser=await chromium.launch({headless:true,...(process.env.CHROME_EXECUTABLE_PATH?{executablePath:process.env.CHROME_EXECUTABLE_PATH}:{})});
  const context=await browser.newContext({reducedMotion:'reduce'});
  const page=await context.newPage();
  const errors=[];const external=[];
  page.on('pageerror',e=>errors.push(e.message));
  const origin=`http://127.0.0.1:${server.address().port}`;
  await page.route('**/*',route=>{
    if(new URL(route.request().url()).origin!==origin){external.push(route.request().url());return route.abort();}
    return route.continue();
  });
  await page.goto(origin);
  for(const width of [360,768,1440]){
    await page.setViewportSize({width,height:1000});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`overflow at ${width}`);
  }
  await page.getByRole('button',{name:'Near capacity',exact:true}).click();
  assert.equal(await page.getByRole('meter').getAttribute('aria-valuenow'),'84');
  await page.getByRole('button',{name:'Model changed',exact:true}).click();
  assert.equal(await page.getByRole('meter').count(),0);
  assert.equal(await page.getByText('Limit unknown',{exact:true}).isVisible(),true);
  assert.equal(await page.getByText('Awaiting usage',{exact:true}).isVisible(),true);
  await page.getByRole('button',{name:'Room to work',exact:true}).press('Enter');
  assert.equal(await page.getByRole('meter').getAttribute('aria-valuenow'),'38');
  assert.equal(await page.locator('[aria-pressed="true"]').count(),1);
  const faq=page.locator('summary').filter({hasText:'Will it tell me when model quality drops?'});
  await faq.press('Enter');
  assert.equal(await page.getByText('No. The guidance uses recorded capacity',{exact:false}).isVisible(),true);
  await page.getByRole('link',{name:'Get context-status',exact:false}).click();
  assert.equal(new URL(page.url()).hash,'#install');
  // Mock only this isolated test browser's clipboard; never overwrite the user's.
  await page.evaluate(()=>{window.copied='';Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.copied=text;}}});});
  await page.getByRole('button',{name:'Copy commands',exact:true}).click();
  const copied=await page.evaluate(()=>window.copied);
  assert.match(copied,/b19f0a01a18c126a2c69615eef3f4285c73b2c61/);
  assert.equal(copied.split('\n').slice(0,-1).every(line=>line.endsWith('&&')),true);
  assert.match(await page.locator('#copy-feedback').innerText(),/^Copied/);
  await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new Error('denied');}}}));
  await page.getByRole('button',{name:'Copy commands',exact:true}).click();
  assert.match(await page.locator('#copy-feedback').innerText(),/Commands selected/);
  assert.equal(await page.evaluate(()=>getSelection().toString()),copied);
  const brokenAnchors=await page.locator('a[href^="#"]').evaluateAll(links=>links.map(a=>a.getAttribute('href')).filter(h=>h!=='#'&&!document.getElementById(h.slice(1))));
  assert.deepEqual(brokenAnchors,[]);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  if(process.env.LANDING_SCREENSHOTS){
    await mkdir(process.env.LANDING_SCREENSHOTS,{recursive:true});
    await page.evaluate(()=>{getSelection().removeAllRanges();scrollTo(0,0);});
    await page.screenshot({path:resolve(process.env.LANDING_SCREENSHOTS,'landing-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:resolve(process.env.LANDING_SCREENSHOTS,'landing-mobile.png'),fullPage:true});
  }
  console.log('Landing page passed: responsive layout, scenario states, keyboard FAQ, install anchor, copy/fallback, no external requests or JS errors.');
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
