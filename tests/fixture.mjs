import {mkdtemp, mkdir, writeFile, appendFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

// A synthetic Codex home keeps integration tests independent of personal chats.
export async function makeFixture(used=60000) {
  const id='00000000-0000-4000-8000-000000000123';
  const home=await mkdtemp(join(tmpdir(),'context-status-test-'));
  await mkdir(join(home,'sessions'));
  const log=join(home,'sessions',`test-${id}.jsonl`);
  async function write(tokens,withUsage=true) {
    const records=[
      {type:'session_meta',payload:{id}},
      {type:'turn_context',payload:{model:'Test model',effort:'high',turn_id:'one'}},
    ];
    if(withUsage) records.push({type:'event_msg',timestamp:new Date().toISOString(),payload:{
      type:'token_count',info:{model_context_window:100000,last_token_usage:{
        input_tokens:tokens-1000,cached_input_tokens:tokens-3000,output_tokens:1000,total_tokens:tokens,
      }},
    }});
    await writeFile(log,records.map(record=>JSON.stringify(record)).join('\n')+'\n');
  }
  await write(used);
  const append=record=>appendFile(log,JSON.stringify({...record,timestamp:new Date().toISOString()})+'\n');
  return {id,home,write,append,cleanup:()=>rm(home,{recursive:true,force:true})};
}
