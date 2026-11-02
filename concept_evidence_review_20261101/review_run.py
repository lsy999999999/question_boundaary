"""Read-only post-run review of full or interrupted experiments; no simulator calls."""
import sys,json,hashlib,statistics
from pathlib import Path
import numpy as np

src=Path(sys.argv[1]).resolve();root=src/'runs/development_01'
sys.path.insert(0,str(src))
from engine import digest,control
from ledger import prospective_metrics,check_citations,retention

read=lambda p:json.loads(p.read_text())
errors=[];manifest=read(root/'manifest.json');live=read(root/'LIVE_STATUS.json')
for name,h in manifest['source_hashes'].items():
    if hashlib.sha256((src/name).read_bytes()).hexdigest()!=h:errors.append('changed source '+name)
for name,key in [('PLAN.md','plan_sha256'),('seed_public.json','seed_sha256')]:
    if hashlib.sha256((src/name).read_bytes()).hexdigest()!=manifest[key]:errors.append('changed '+name)
wires=[];ids=[];tokens=[0,0,0];missing=0;elapsed=0
facts=read(root/'preserved_facts.json')
for folder in sorted((root/'wire').iterdir()):
    req=read(folder/'request.json');res=read(folder/'response.json');b=res['body'];u=b['usage'];ids.append(b['id'])
    if req['payload']['model']!='gpt-6-luna' or b['model']!='gpt-6-luna':errors.append('model label')
    if res['time_ns']<=req['time_ns'] or b['choices'][0]['finish_reason']!='stop':errors.append('generation order/completeness')
    if req['payload']['max_completion_tokens']!=2048 or not 0<=u['completion_tokens']<=2048:errors.append('token budget')
    ctx=json.loads(req['payload']['messages'][1]['content']);ctx=ctx.get('original_task',ctx)
    if ctx['facts']!=facts['relations'] or ctx['historical_refutation']!=facts['historical_refutation']:errors.append('preserved evidence absent')
    tokens[0]+=u['prompt_tokens'];tokens[1]+=u['completion_tokens'];details=u.get('completion_tokens_details') or {}
    tokens[2]+=details.get('reasoning_tokens',0);missing+=int('reasoning_tokens' not in details);elapsed+=res['elapsed_seconds']
    value=json.loads(b['choices'][0]['message']['content']);validation=read(folder/'validation_error.json') if (folder/'validation_error.json').exists() else None
    if 'assessment' in folder.name:
        for update in value.get('updates',[]):
            try:check_citations(update['evidence_ids'],ctx,update['id'])
            except ValueError:errors.append('assessment evidence owner '+folder.name)
    wires.append(dict(name=folder.name,value=value,validation=validation))
if len(ids)!=len(set(ids)):errors.append('duplicate response id')
for p in (root/'decisions').glob('*.json'):
    d=read(p);response=read(root/d['generation_records'][-1]['wire']/'response.json')
    if json.loads(response['body']['choices'][0]['message']['content'])!=d['value']:errors.append('decision binding '+p.name)
pairs=[]
for p in sorted(root.glob('round_*/forecast_commit.json')):
    fc=read(p);rec=fc['record'];outcome=read(p.parent/'outcome.json')
    if digest(rec)!=fc['sha256']:errors.append('forecast hash '+p.parent.name)
    obs=[read(root/'observations'/(i+'.json')) for i in rec['observation_ids']]
    for i,o in enumerate(obs):
        if o['time_ns']<=rec['time_ns'] or o['action']!=rec['actions'][i]:errors.append('forecast order/input')
        if not np.array_equal(control(o['action']),np.array(o['u'])):errors.append('control samples')
    if prospective_metrics(rec,obs)!=outcome['metrics']:errors.append('prospective scores')
    pairs.append(dict(round=p.parent.name,descriptor=rec['compiler']['descriptor'],guard=rec['compiler']['guard'],
        question=rec['question'],boundary=rec['boundary'],outcome=outcome))
sealed=read(root/'sealed_input_commit.json')
if digest(sealed['actions'])!=sealed['sha256']:errors.append('sealed inputs hash')
if not sealed['time_ns']<read(root/'wire'/wires[0]['name']/'request.json')['time_ns']:errors.append('sealed input order')
model_summaries={}
for name in ['initial_models.json','round_0/updated_models.json','round_1/updated_models.json','final_models.json']:
    if not (root/name).exists():continue
    models=read(root/name);summary={}
    for k,m in models.items():
        full=min(m['fit']['optimizer_attempts'],key=lambda a:a['objective'])
        folds=[min(f['fit']['optimizer_attempts'],key=lambda a:a['objective']) for f in m['cv_folds']]
        summary[k]=dict(group_cv_nmse=m['group_cv_nmse'],distinct_inputs=m['distinct_inputs'],
            full_optimizer_converged=full['success'],converged_folds=sum(f['success'] for f in folds),folds=len(folds),
            retention=retention(m,facts['relations']))
    model_summaries[name]=summary
result=dict(stage=live['stage'],errors=errors,partial_integrity_passed=not errors,calls=len(wires),
    input_tokens=tokens[0],completion_tokens=tokens[1],reported_reasoning_tokens=tokens[2],
    reasoning_detail_missing=missing,api_elapsed_seconds=elapsed,wall_seconds=(live['time_ns']-manifest['time_ns'])/1e9,
    validation_failures=sum(w['validation'] is not None for w in wires),wires=wires,pairs=pairs,model_summaries=model_summaries,
    final_commit_present=(root/'final_commit.json').exists(),evaluation_present=(root/'sealed_result.json').exists())
if result['evaluation_present']:
    rows=read(root/'sealed_result.json')['checks'];keys=list(rows[0]['nmse'])
    result['evaluation']={k:dict(values=[r['nmse'][k] for r in rows],mean=statistics.mean(r['nmse'][k] for r in rows),
        median=statistics.median(r['nmse'][k] for r in rows),above_0_1=sum(r['nmse'][k]>.1 for r in rows)) for k in keys}
    result['final_decision']=read(root/'final_commit.json')['record']['decision']
    result['full_execution_audit']=read(root/'AUDIT.json')
out=Path(sys.argv[2]);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['wires','pairs','model_summaries','final_decision']},ensure_ascii=False,indent=2))
