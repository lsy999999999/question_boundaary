"""Artifact broker; no model/parameter selection or scientific repair."""
import argparse
import ast
import datetime as dt
import hashlib
import html
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'leader_rna_dev_v1_20261102'
PYTHON = '/Applications/deep_learning_hm/.venv/bin/python'
CUTOFF = '2025-05-12'
EVIDENCE = dict(sequence='sequence_measurements.json', fractionation='fraction_dev.json',
                phase_composition='phase_measurements.json', motion='mobility_dev.json')
ARMS = {
 'A': 'Use the original free scheduling: choose the next action freely using the V1 leader/researcher principles. No additional proactive retrieval or product enforcement scheduling instruction.',
 'B': 'Use original free scheduling, PLUS: when relevant knowledge is missing, proactively issue a relation-oriented search and then explain how the returned knowledge changes or fails to change the candidate.',
 'C': 'For the selected candidate keep its main gap task active until explicitly adjudicated. When a relationship is unknown, construct a marked hypothesis, reduce it, derive/compute across a stated range, and deliver a testable consequence distinct from an alternative. Knowledge retrieval is available as needed. A time fit cannot complete this mechanism task; missing empirical identification does not prevent conditional computation.'}

def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False))

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def event(run, kind, **kw):
    p=run/'events.jsonl'
    with p.open('a') as f:f.write(json.dumps(dict(time=now(),kind=kind,**kw),ensure_ascii=False)+'\n')

def state(run):
    return read(sorted((run/'states').glob('*.json'))[-1])

def snapshot(run, s, reason):
    s=json.loads(json.dumps(s)); s['version']+=1; s['reason']=reason
    p=run/'states'/f"{s['version']:04d}.json"
    dump(p,s); event(run,'state_version',path=str(p.relative_to(run)),sha256=sha(p),reason=reason)
    return s

def prepare(run_id, arm, stage='B'):
    run=ROOT/'runs'/run_id
    run.mkdir(parents=True,exist_ok=False)
    for name in ['states','inputs','replies','tools','visible','code']:(run/name).mkdir()
    files=['case_brief.md','initial_measurements.json']
    if stage=='B':files+=list(EVIDENCE.values())
    for name in files:dump(run/'visible'/name,(OLD/'agent_visible'/name).read_text())
    materials={'files':{n:(run/'visible'/n).read_text() for n in files},
      'method_index':(OLD/'frozen_prompts/METHOD_INDEX.md').read_text(),
      'method_library':read(OLD/'frozen_prompts/METHOD_LIBRARY.json'),
      'v1_role_principles':{n:(OLD/'frozen_prompts'/n).read_text() for n in ['LEADER_SYSTEM_PROMPT.md','RESEARCHER_SYSTEM_PROMPT.md']}}
    if stage=='B':
        materials['round1_to4_replies']={f'{role}_{i:02d}':(OLD/'transcripts'/f'{role}_{i:02d}.md').read_text() for i in range(1,5) for role in ['leader','researcher']}
        materials['round1_to4_compute']={f'C{i:02d}':read(OLD/'computations'/f'C{i:02d}_result.json') for i in range(1,5)}
        # Only actually issued pre-round-5 clarifications, not later interpretations.
        materials['pre5_supplements']={str(i):read(OLD/'agent_visible'/f'researcher_{i:02d}_supplement.json') for i in range(2,5)}
    dump(run/'materials.json',materials)
    config=dict(run_id=run_id,stage=stage,arm=arm,model='gpt-6-luna',schedule=ARMS[arm],
       reply_cap=6 if stage=='B' else 12,search_cap=3 if stage=='B' else 6,compute_cap=3 if stage=='B' else 10,
       material_sha256=sha(run/'materials.json'),created=now(),sampling='agent tool default; no exposed seed/temperature/output-token control',
       isolation='input allowlist and role instructions; not OS sandbox',source_code_sha256=sha(Path(__file__)))
    dump(run/'config.json',config)
    s=dict(version=-1,candidates={},tasks={},actor_events=[],tools=[],literature_use=[],adjudications=[],
        opened=files,counters=dict(replies=0,search=0,compute=0,evidence=0),finals=[])
    snapshot(run,s,'initial reconstructed round-4 state' if stage=='B' else 'initial case')
    return run

def build_input(run, role, label, final=False):
    s=state(run); cfg=read(run/'config.json')
    assert s['counters']['replies']<cfg['reply_cap']
    p=run/'inputs'/f'{label}.json'
    bundle=dict(role=role,turn_label=label,final_reply=final,
      instruction=(ROOT/('ROLE_COMMON_C.md' if cfg['stage']=='C' else 'ROLE_COMMON.md')).read_text(),scheduling=cfg['schedule'],
      role_duty=('Select the gap, issue a concrete task; on final reply adjudicate the actual candidate, computation and executor dissent. Do not invent unexecuted results.' if role=='leader' else 'Execute the leader task, requesting retrieval/computation as needed; on final reply review actual results, repair errors if budget permits and submit your candidate and dissent.'),
      remaining={k:cfg[k+'_cap']-s['counters'][k if k!='reply' else 'replies'] for k in ['reply','search','compute']},
      materials=read(run/'materials.json'),state=s,
      evidence={p.name:read(p) for p in (run/'visible').glob('*.json')},
      output_file=str(run/'replies'/f'{label}.json'),
      constraints='Do not read anything outside this input file. Do not use memory/network or run scientific computations yourself. All tool requests go through broker. No study answer or held-out data supplied.')
    dump(p,bundle); event(run,'actor_input',role=role,label=label,path=str(p.relative_to(run)),sha256=sha(p))
    return p

def search(run, req):
    for key in ['missing_relation','variables','conditions','query','change_if_found']:
        if not req.get(key):return dict(status='clarification',missing=key)
    query=req['query']+f' AND FIRST_PDATE:[1900-01-01 TO {CUTOFF}]'
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',pageSize=5,resultType='core'))
    base=run/'tools'/req['id']; base.mkdir(exist_ok=True)
    if not (base/'request.json').exists():dump(base/'request.json',dict(request=req,url=url,time=now()))
    # Network execution is separate so the exact curl request can use the host's
    # approved network capability without escalating model-authored computation.
    if not (base/'raw.json').exists():return dict(status='waiting_external',url=url,output_path=str(base/'raw.json'),reason='Await exact HTTP transport; no model/curator scientific selection')
    try:data=read(base/'raw.json')
    except Exception as e:return dict(status='failed',reason=str(e))
    if 'errCode' in data or 'resultList' not in data:return dict(status='failed',reason='Search service error',response=data)
    sources=[];excluded=[]
    for x in data.get('resultList',{}).get('result',[]):
        date=x.get('firstPublicationDate','');text=html.unescape(re.sub('<[^>]+>',' ',x.get('abstractText','')))
        identity=(x.get('title','')+' '+x.get('doi','')+' '+text).lower()
        if not date or date>CUTOFF or 's44286-026-00454' in identity or '10.1101/2025.05.13' in identity or not text:
            excluded.append(dict(id=x.get('id'),reason='date/target/no-abstract'));continue
        sources.append(dict(id=req['id']+'_S'+str(len(sources)+1),title=x.get('title'),doi=x.get('doi'),pmid=x.get('id'),first_publication_date=date,
          retrieval_time=now(),scope='abstract only; historical publication metadata verified, historical abstract text version not independently archived',
          original_evidence=text,relation_variables_conditions='Executor must extract from original evidence; no broker scientific synthesis',
          usable_for='Background candidate relations only; transfer to this RNA system requires executor conditions and a marked bridge hypothesis'))
    return dict(status='returned',sources=sources,excluded=excluded,hit_count=data.get('hitCount'),url=url,
                raw_sha256=sha(base/'raw.json'),knowledge_limit='No full-text formulas/units are inferred from the abstract. Refine or request a known historical source if needed.')

def compute(run, req):
    if not req.get('model_spec') or not req.get('code'):
        return dict(status='clarification',reason='model_spec and complete code required; broker will not supply missing scientific choices')
    code=req['code'];base=run/'tools'/req['id'];base.mkdir()
    dump(base/'submitted.py',code)
    allowed={'json','math','statistics','itertools','functools','collections','numpy','scipy','sympy'}
    try:
        tree=ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or '']
                if any(n.split('.')[0] not in allowed for n in names):raise ValueError('Only declared scientific/standard modules allowed')
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'open','exec','eval','compile','__import__','input'}:raise ValueError('Filesystem/dynamic execution unavailable')
            if isinstance(node,ast.Attribute) and (node.attr.startswith('__') or node.attr in {'load','save','loadtxt','savetxt','fromfile','tofile','read_csv','read_json','system','popen'}):raise ValueError('External I/O unavailable')
    except Exception as e:return dict(status='clarification',reason=str(e))
    data={p.name:read(p) for p in (run/'visible').glob('*.json')}
    dump(base/'data.json',data)
    bootstrap='import json\nDATA=json.loads('+repr(json.dumps(data))+')\n'+code
    dump(base/'executed.py',bootstrap)
    try:
        out=subprocess.run([PYTHON,str(base/'executed.py')],cwd=base,capture_output=True,text=True,timeout=30,
            env={'PATH':'/opt/homebrew/bin:/usr/bin:/bin','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
        result=dict(status='executed' if out.returncode==0 else 'failed',returncode=out.returncode,stdout=out.stdout[:60000],stderr=out.stderr[:10000],code_sha256=sha(base/'submitted.py'),
          data_sha256=sha(base/'data.json'),scope='Unmodified executor code, broker prepends DATA. Conditional simulation unless model says and evidence supports otherwise.')
    except subprocess.TimeoutExpired as e:result=dict(status='failed',reason='30s timeout',stdout=str(e.stdout)[:1000],stderr=str(e.stderr)[:1000])
    dump(base/'execution.json',result)
    return result

def process_request(run, req):
    s=state(run);cfg=read(run/'config.json');kind=req.get('type');rid=req.get('id','')
    if kind not in {'search','compute','evidence'} or not re.fullmatch('[A-Za-z0-9_-]{1,50}',rid):raise ValueError('Invalid request')
    if rid in [x['id'] for x in s['tools']]:raise ValueError('Duplicate tool ID')
    event(run,'tool_request',request=req)
    cap=cfg.get(kind+'_cap',4)
    if s['counters'][kind]>=cap:result=dict(status='blocked',reason=kind+' budget exhausted')
    else:
        s['counters'][kind]+=1
        if kind=='search':result=search(run,req)
        elif kind=='compute':result=compute(run,req)
        else:
            filename=EVIDENCE.get(req.get('category'))
            if not filename:result=dict(status='unavailable',reason='unknown measurement category')
            else:
                p=run/'visible'/filename
                if not p.exists():dump(p,(OLD/'agent_visible'/filename).read_text())
                if filename not in s['opened']:s['opened'].append(filename)
                result=dict(status='returned',filename=filename,data=read(p),note='Existing measured data, not a new experiment')
    record=dict(id=rid,type=kind,candidate_id=req.get('candidate_id'),gap_id=req.get('gap_id'),request=req,result=result)
    dump(run/'tools'/f'{rid}_record.json',record);s['tools'].append(record)
    for task in s['tasks'].values():
        if task.get('candidate_id')==req.get('candidate_id') and task.get('gap_id')==req.get('gap_id'):
            task['status']='acceptance' if result['status'] in {'returned','executed'} else 'clarification'
    snapshot(run,s,'tool return '+rid)
    event(run,'tool_return',id=rid,status=result['status'])
    return record

def finish_search(run,rid):
    s=state(run);record=next(t for t in s['tools'] if t['id']==rid)
    assert record['type']=='search' and record['result']['status']=='waiting_external'
    result=search(run,record['request']);assert result['status']!='waiting_external'
    record['result']=result
    dump(run/'tools'/f'{rid}_returned.json',record)
    for t in s['tasks'].values():
        if t.get('candidate_id')==record.get('candidate_id') and t.get('gap_id')==record.get('gap_id'):t['status']='acceptance'
    snapshot(run,s,'external search return '+rid);event(run,'external_search_return',id=rid,status=result['status'])
    return result

def complete_actor(run,label,role,completion_source='Root observed collaboration FINAL_ANSWER before sealing'):
    p=run/'replies'/f'{label}.json'
    raw=p.read_bytes();json.loads(raw)
    sealed=run/'sealed_replies'/p.name
    sealed.parent.mkdir(exist_ok=True)
    with sealed.open('xb') as f:f.write(raw)
    dump(run/'actor_finished'/f'{label}.json',dict(role=role,label=label,time=now(),sha256=sha(sealed),source=completion_source))
    event(run,'actor_finished_and_sealed',role=role,label=label,sha256=sha(sealed))

def ingest(run,label,role):
    cfg=read(run/'config.json');p=run/'replies'/f'{label}.json'
    if cfg['stage']=='C':
        completion=read(run/'actor_finished'/f'{label}.json')
        assert completion['role']==role and sha(p)==completion['sha256'],'Reply changed after completion'
        p=run/'sealed_replies'/p.name
        assert sha(p)==completion['sha256']
    reply=read(p);s=state(run)
    assert not any(x['label']==label for x in s['actor_events'])
    assert s['counters']['replies']<cfg['reply_cap']
    for c in reply.get('candidates',[]):
        c=dict(c);cid=c['id'];c['version']=s['candidates'].get(cid,{}).get('version',0)+1;c['author']=role;c['reply']=label
        s['candidates'][cid]=c
    errors=[]
    for t in reply.get('tasks',[]):
        t=dict(t);tid=t['id'];old=s['tasks'].get(tid)
        if old and (old['candidate_id'],old['gap_id'],old['kind'])!=(t['candidate_id'],t['gap_id'],t['kind']):
            errors.append(dict(task_id=tid,error='Task identity changed; update rejected. Keep stable candidate_id/gap_id/kind or explicitly create a new task with prior linkage.'));continue
        if t.get('status') in {'completed','complete'}:t['status']='acceptance'
        if t.get('status')=='assigned':t['status']='todo'
        s['tasks'][tid]=t
    adjudications=reply.get('adjudication',[]) or []
    if isinstance(adjudications,dict):
        errors.append(dict(error='adjudication object received; wrapped as one-element list without modifying scientific content'))
        adjudications=[adjudications]
    for a in adjudications:
        t=s['tasks'].get(a.get('task_id'));valid=False;reason='task/artifact/leader missing'
        refs=a.get('artifact_ids',[]);available=[x['id'] for x in s['tools'] if x['result']['status'] in {'executed','returned'}]
        if cfg['stage']=='C':available += [e['label'] for e in s['actor_events']]
        if role=='leader' and t and a.get('checks') and refs and all(x in available for x in refs):
            valid=True;reason='formal linkage passes; scientific meaning requires substantive audit'
            if t['kind']=='mechanism' and a['decision']=='complete':
                c=s['candidates'].get(t['candidate_id'],{})
                numerical=any(x['type']=='compute' and x['id'] in refs and x['result']['status']=='executed' for x in s['tools'])
                analytical=cfg['stage']=='C' and a.get('derivation_artifact') in refs and a.get('derivation_checks')
                valid=bool(all(c.get(k) for k in ['hypotheses','equations','observation_mapping','alternatives','predictions','checks']) and (numerical or analytical))
                reason='mechanism formal artifact gate '+('passed' if valid else 'failed')
        a=dict(a,formal_gate=valid,formal_gate_reason=reason,reply=label)
        s['adjudications'].append(a)
        if t:t['status']=('completed' if a['decision']=='complete' else a['decision']) if valid else 'rework'
    s['literature_use']+=reply.get('literature_use',[])
    if reply.get('final'):s['finals'].append(dict(role=role,label=label,artifact=reply['final']))
    s['actor_events'].append(dict(label=label,role=role,reply=reply,protocol_errors=errors,input_sha256=sha(run/'inputs'/f'{label}.json'),reply_sha256=sha(p)))
    s['counters']['replies']+=1;snapshot(run,s,'actor reply '+label)
    for req in reply.get('requests',[]):
        if cfg['stage']=='C' and role=='leader':
            event(run,'leader_request_pending_executor',request=req)
        else:process_request(run,req)
    return state(run)

def freeze(run):
    assert not (run/'FROZEN.json').exists()
    files={str(p.relative_to(run)):sha(p) for p in sorted(run.rglob('*')) if p.is_file()}
    dump(run/'FROZEN.json',dict(time=now(),files=files,state_version=state(run)['version'],counters=state(run)['counters']))
    return sha(run/'FROZEN.json')

def verify(run):
    return all((run/p).exists() and sha(run/p)==h for p,h in read(run/'FROZEN.json')['files'].items())

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action');ap.add_argument('run');ap.add_argument('--arm',default='C');ap.add_argument('--stage',default='B');ap.add_argument('--role');ap.add_argument('--label');ap.add_argument('--final',action='store_true');a=ap.parse_args()
    run=ROOT/'runs'/a.run
    if a.action=='prepare':print(prepare(a.run,a.arm,a.stage))
    elif a.action=='input':print(build_input(run,a.role,a.label,a.final))
    elif a.action=='ingest':s=ingest(run,a.label,a.role);print(json.dumps(dict(version=s['version'],counters=s['counters'],tools=[dict(id=t['id'],status=t['result']['status']) for t in s['tools']]),ensure_ascii=False))
    elif a.action=='freeze':print(freeze(run))
    elif a.action=='verify':print(verify(run))
    elif a.action=='finish-search':print(json.dumps(finish_search(run,a.label),ensure_ascii=False))
    elif a.action=='actor-finished':complete_actor(run,a.label,a.role);print('sealed')
