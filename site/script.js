'use strict';
const samples={
  room:{used:38,cached:35.5,other:2.5,remaining:'160,208 remaining',cache:'94%',cacheWidth:94,title:'Room to continue',copy:'This recorded estimate has room. Keep going on the current task.',meta:'Example model · Reasoning: high',time:'Recorded example · 10:42 AM',note:'Cache reuse saves repeated processing. Cached input still uses context.'},
  full:{used:84,cached:78,other:6,remaining:'41,344 remaining',cache:'93%',cacheWidth:93,title:'Prepare a handoff before a large step',copy:'Save the goal, decisions, and next action. This checkpoint is guidance, not a quality warning.',meta:'Example model · Reasoning: high',time:'Recorded example · 11:18 AM',note:'The 80% and 90% checkpoints are advisory, not known compaction thresholds.'},
  model:{used:null,cached:0,other:0,remaining:'Waiting for a new limit',cache:'Waiting',cacheWidth:0,title:'Waiting for fresh usage',copy:'The recorded model changed. Capacity will return when new usage and a context limit are available.',meta:'New example model · Reasoning: high',time:'Model change example · 11:24 AM',note:'A recorded model transition can arrive before the next usage measurement.'}
};
const byId=id=>document.getElementById(id);
for(const button of document.querySelectorAll('[data-scenario]')){
  button.addEventListener('click',()=>{
    const sample=samples[button.dataset.scenario];
    document.querySelectorAll('[data-scenario]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    const meter=document.querySelector('.capacity-track');
    if(sample.used===null){meter.setAttribute('role','img');meter.removeAttribute('aria-valuenow');meter.removeAttribute('aria-valuemin');meter.removeAttribute('aria-valuemax');meter.setAttribute('aria-label','Example context capacity unavailable after model change');}
    else{meter.setAttribute('role','meter');meter.setAttribute('aria-valuemin','0');meter.setAttribute('aria-valuemax','100');meter.setAttribute('aria-valuenow',String(sample.used));meter.setAttribute('aria-label','Example estimated context usage');}
    byId('capacity-value').textContent=sample.used===null?'Awaiting usage':`${sample.used}% used`;
    byId('cached-fill').style.width=`${sample.cached}%`;byId('fresh-fill').style.width=`${sample.other}%`;
    byId('remaining-value').textContent=sample.remaining;
    document.querySelector('.meter-ticks span:last-child').textContent=sample.used===null?'Limit unknown':'258,400 tokens';
    byId('cache-value').textContent=sample.cache;byId('cache-fill').style.width=`${sample.cacheWidth}%`;
    byId('advice-title').textContent=sample.title;byId('advice-copy').textContent=sample.copy;
    byId('demo-meta').textContent=sample.meta;byId('demo-time').textContent=sample.time;byId('demo-footnote').textContent=sample.note;
    byId('scenario-announcement').textContent=`${button.textContent} example: ${sample.title}. ${sample.copy}`;
  });
}
byId('copy-command').addEventListener('click',async()=>{
  const code=byId('install-command');
  try{await navigator.clipboard.writeText(code.textContent);byId('copy-feedback').textContent='Copied. Paste into your terminal to preview the installation.';}
  catch{const range=document.createRange();range.selectNodeContents(code);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);byId('copy-feedback').textContent='Copy unavailable here. Commands selected; use your keyboard to copy.';}
});
