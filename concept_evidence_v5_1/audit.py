import json,hashlib
from pathlib import Path
import numpy as np
from engine import digest,control,nmse
from ledger import choose,check_citations,prospective_metrics
from design import pair
from scope import label


def audit(root):
    root=Path(root);read=lambda p:json.loads(p.read_text());errors=[];ids=[];usage=[0,0,0];missing=0
    wires=sorted((root/'wire').iterdir())
    if len(wires)>20:errors.append('call cap')
    for w in wires:
        req=read(w/'request.json');res=read(w/'response.json');b=res['body'];ids.append(b.get('id'));u=b['usage']
        if req['payload']['model']!='gpt-6-luna' or b['model']!='gpt-6-luna':errors.append('model label')
        if req['payload']['max_completion_tokens']!=2048 or u['completion_tokens']>2048:errors.append('token budget')
        if res['time_ns']<=req['time_ns'] or b['choices'][0]['finish_reason']!='stop':errors.append('response order/completeness')
        usage[0]+=u['prompt_tokens'];usage[1]+=u['completion_tokens'];d=u.get('completion_tokens_details',{})
        if 'reasoning_tokens' in d:usage[2]+=d['reasoning_tokens']
        else:missing+=1
    if None in ids or len(set(ids))!=len(ids):errors.append('response uniqueness')
    facts=read(root/'preserved_facts.json')
    for p in (root/'decisions').glob('*.json'):
        d=read(p);w=root/d['generation_records'][-1]['wire'];b=read(w/'response.json')['body'];raw=b['choices'][0]['message']['content'].strip()
        if raw.startswith('```'):raw=raw.split('\n',1)[1].rsplit('```',1)[0].strip()
        if json.loads(raw)!=d['value']:errors.append('decision binding '+p.name)
        ctx=json.loads(read(w/'request.json')['payload']['messages'][1]['content']);ctx=ctx.get('original_task',ctx)
        if ctx['facts']!=facts['relations'] or ctx['historical_refutation']!=facts['historical_refutation']:errors.append('forgot preserved evidence '+p.name)
        if p.stem.endswith('assessment'):
            for u in d['value']['updates']:
                try:check_citations(u['evidence_ids'],ctx,u['id'])
                except ValueError:errors.append('wrong evidence owner')
            if d['value']['boundary_verdict']!=ctx['actual_outcome']['boundary_verdict']:errors.append('boundary verdict mismatch')
    pairs=0
    for p in root.glob('round_*/forecast_commit.json'):
        fc=read(p);rec=fc['record'];pairs+=1
        if digest(rec)!=fc['sha256']:errors.append('forecast hash')
        if not rec['compiler']['passed'] or not rec['compiler']['guard']['passed']:errors.append('unadmitted design')
        obs=[read(root/'observations'/(i+'.json')) for i in rec['observation_ids']]
        for i,o in enumerate(obs):
            if o['time_ns']<=rec['time_ns'] or o['action']!=rec['actions'][i]:errors.append('forecast/observation order/input')
            if not np.array_equal(control(pair(rec['compiler']['descriptor'])[i]),np.array(o['u'])):errors.append('actual input condition')
        outcome=read(p.parent/'outcome.json');computed=prospective_metrics(rec,obs)
        if computed!=outcome['metrics']:errors.append('prospective score/fit metadata mismatch')
        labels=[label(rec['boundary'],o['u']) for o in obs];owner=rec['boundary']['model_id'];actual=[x['high_error'] for x in computed if x['owner_model_id']==owner]
        verdict='untested' if rec['boundary']['status']=='abstain' else ('supported_on_pair' if labels==actual else 'violated_on_pair')
        if labels!=outcome['predicted_high_error'] or actual!=outcome['observed_high_error'] or verdict!=outcome['boundary_verdict']:errors.append('scope verdict')
    f=read(root/'final_commit.json');s=read(root/'sealed_result.json');c=read(root/'sealed_input_commit.json');g=read(root/'concept_graph.json')
    if digest(f['record'])!=f['sha256'] or digest(c['actions'])!=c['sha256']:errors.append('final/input hash')
    if not c['time_ns']<min(read(w/'request.json')['time_ns'] for w in wires)<f['record']['time_ns']<s['time_ns']:errors.append('evaluation order')
    if any(read(w/'request.json')['time_ns']>=f['record']['time_ns'] for w in wires):errors.append('post-final generation')
    recomputed=choose(read(root/'final_models.json'),set(g['withdrawn']),facts['relations'])
    if recomputed!=f['record']['decision']:errors.append('final rule/text/choice inconsistency')
    if f['record']['predictions']['old_frozen']!=c['baseline_predictions']:errors.append('old frozen predictions changed')
    for i,row in enumerate(s['checks']):
        if row['action']!=c['actions'][i]:errors.append('sealed input changed')
        for k,v in f['record']['predictions'].items():
            score=nmse(np.array(v[i]),np.array(row['truth'])) if v[i] is not None else None
            if score!=row['nmse'][k]:errors.append('sealed score mismatch')
    m=read(root/'manifest.json');src=Path(__file__).parent
    for name,h in m['source_hashes'].items():
        if hashlib.sha256((src/name).read_bytes()).hexdigest()!=h:errors.append('source changed '+name)
    return dict(passed=not errors,errors=errors,calls=len(wires),executed_pairs=pairs,input_tokens=usage[0],completion_tokens=usage[1],reported_reasoning_tokens=usage[2],reasoning_detail_missing_responses=missing,
        final_selection_author='deterministic_frozen_rule',scope='Execution and typed evidence audit, not a certificate for free-form scientific prose')

if __name__=='__main__':
    import sys
    print(json.dumps(audit(sys.argv[1]),indent=2))
