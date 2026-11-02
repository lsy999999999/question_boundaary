"""Fixed transport helpers for the existing leader; no scientific decisions.

The existing leader stays active in the background and schedules the same executor.
Its remaining five scientific replies are logical commits in one active turn;
executor replies remain six separate invocations. This changes runtime packaging,
not scientific inputs, tools, role count or the 12-reply cap. No provider token cap
or uninterrupted service lifetime guarantee is available.
"""
import json
import sys
import broker as b
from manage import next_input

RUN=b.ROOT/'runs/V2_full'
ORDER=['L1','R1','L2','R2','L3','R3','L4','R4','L5','R5','R6','L6']

def heartbeat(stage,**details):
    record=dict(time=b.now(),stage=stage,**details)
    with (RUN/'autonomous_events.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
    print(json.dumps(record,ensure_ascii=False))

def ingest(label):
    s=b.state(RUN);expected=ORDER[s['counters']['replies']]
    assert label==expected,(label,expected)
    role='leader' if label.startswith('L') else 'executor'
    source=('Leader committed an immutable logical scientific reply in its continuing autonomous turn' if role=='leader' else 'Leader observed executor collaboration FINAL_ANSWER before sealing')
    b.complete_actor(RUN,label,role,source)
    s=b.ingest(RUN,label,role)
    heartbeat('ingested',label=label,counters=s['counters'])
    print(json.dumps(dict(pending_searches=[dict(id=t['id'],url=t['result']['url'],output_path=t['result']['output_path']) for t in s['tools'] if t['result']['status']=='waiting_external'],tool_failures=[dict(id=t['id'],result=t['result']) for t in s['tools'] if t['result']['status'] in {'failed','clarification','blocked'}]),ensure_ascii=False))

def next_call():
    s=b.state(RUN);label=ORDER[s['counters']['replies']]
    role='leader' if label.startswith('L') else 'executor'
    assert not any(t['result']['status']=='waiting_external' for t in s['tools']),'Return all pending searches before next input'
    prompt=next_input('V2_full',role,label,final=label in {'R6','L6'})
    heartbeat('input_ready',label=label,role=role)
    print(prompt)

def finish(rid):
    result=b.finish_search(RUN,rid)
    heartbeat('search_return',id=rid,status=result['status'],source_count=len(result.get('sources',[])))

def finalize():
    s=b.state(RUN);assert s['counters']['replies']==12
    assert {f['role'] for f in s['finals']}=={'leader','executor'}
    assert not any(t['result']['status']=='waiting_external' for t in s['tools'])
    heartbeat('freezing_completed_research',counters=s['counters'])
    digest=b.freeze(RUN)
    b.dump(b.ROOT/'RESEARCH_RUN_COMPLETED.json',dict(time=b.now(),status='研究运行已冻结，等待主会话独立审读',run='V2_full',sha256=digest,counters=s['counters'],total_research_replies=48,independent_review_complete=False))
    print(json.dumps(dict(stage='research_run_complete',frozen_sha256=digest,counters=s['counters'])))

if __name__=='__main__':
    action=sys.argv[1]
    if action=='start':
        b.dump(RUN/'AUTONOMOUS_RUNNING.json',dict(time=b.now(),controller_agent='/root/full_leader',stage='autonomous leader turn started',role_count=2,scientific_reply_order=ORDER,cap=12,leader_runtime='L1 separate invocation; L2-L6 logical scientific commits in one active followup turn',executor_runtime='same executor, six invocations',no_scientific_prompt_changes=True))
        heartbeat('autonomous_start')
    elif action=='ingest':ingest(sys.argv[2])
    elif action=='next':next_call()
    elif action=='finish-search':finish(sys.argv[2])
    elif action=='finalize':finalize()
    elif action=='heartbeat':heartbeat(sys.argv[2])
