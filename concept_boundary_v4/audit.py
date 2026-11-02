import json,hashlib
from pathlib import Path
import numpy as np
from engine import digest,control,nmse
from numerics import validate_evidence_ownership
from boundaries import evaluate


def audit(root):
    root=Path(root);read=lambda p:json.loads(p.read_text());errors=[];ids=[];usage=[0,0,0];missing=0;wires=sorted((root/'wire').iterdir())
    if len(wires)>20:errors.append('call cap')
    for w in wires:
        req=read(w/'request.json');res=read(w/'response.json');body=res['body'];ids.append(body.get('id'))
        if req['payload']['model']!='gpt-6-luna' or body['model']!='gpt-6-luna':errors.append('model label')
        if req['payload']['max_completion_tokens']!=2048 or body['usage']['completion_tokens']>2048:errors.append('token cap')
        if res['time_ns']<=req['time_ns']:errors.append('request chronology')
        if body['choices'][0]['finish_reason']!='stop':errors.append('response incomplete')
        usage[0]+=body['usage']['prompt_tokens'];usage[1]+=body['usage']['completion_tokens']
        detail=body['usage'].get('completion_tokens_details',{})
        if 'reasoning_tokens' not in detail:missing+=1
        else:usage[2]+=detail['reasoning_tokens']
    if None in ids or len(set(ids))!=len(ids):errors.append('response uniqueness')
    for p in (root/'decisions').glob('*.json'):
        d=read(p);w=root/d['generation_records'][-1]['wire'];raw=read(w/'response.json')['body']['choices'][0]['message']['content'].strip()
        if raw.startswith('```'):raw=raw.split('\n',1)[1].rsplit('```',1)[0].strip()
        if json.loads(raw)!=d['value']:errors.append('decision binding '+p.name)
        if p.stem.endswith('assessment'):
            payload=json.loads(read(w/'request.json')['payload']['messages'][1]['content']);payload=payload.get('original_task',payload)
            for u in d['value']['updates']:
                try:validate_evidence_ownership(u,payload['evidence'])
                except ValueError:errors.append('evidence ownership '+p.name)
    pairs=0
    for p in root.glob('round_*/forecast_commit.json'):
        fc=read(p);rec=fc['record'];pairs+=1
        if digest(rec)!=fc['sha256']:errors.append('forecast hash')
        if not rec['compiler']['passed'] or not rec['compiler']['guard']['passed']:errors.append('unadmitted design')
        obs=[read(root/'observations'/(i+'.json')) for i in rec['observation_ids']]
        for i,o in enumerate(obs):
            if o['time_ns']<=rec['time_ns']:errors.append('observation before forecast')
            if o['action']!=rec['actions'][i] or o['u']!=control(rec['actions'][i]).tolist():errors.append('action changed')
        computed=evaluate(rec['question'],rec['compiler'],rec['boundary'],obs,rec['forecasts']);saved=read(p.parent/'outcome.json')
        if any(saved[k]!=v for k,v in computed.items()):errors.append('outcome mismatch')
        if not computed['actual_conditions_met']:errors.append('one-factor conditions failed')
    f=read(root/'final_commit.json');s=read(root/'sealed_result.json');c=read(root/'sealed_input_commit.json')
    if digest(f['record'])!=f['sha256'] or digest(c['actions'])!=c['sha256']:errors.append('final/input hash')
    if not c['time_ns']<min(read(w/'request.json')['time_ns'] for w in wires)<f['record']['time_ns']<s['time_ns']:errors.append('evaluation chronology')
    if any(read(w/'request.json')['time_ns']>=f['record']['time_ns'] for w in wires):errors.append('model request after final')
    if f['record']['predictions']['old_frozen']!=c['baseline_predictions']:errors.append('frozen reference changed')
    for i,row in enumerate(s['checks']):
        if row['action']!=c['actions'][i]:errors.append('sealed input changed')
        for k,v in f['record']['predictions'].items():
            expected=nmse(np.array(v[i]),np.array(row['truth'])) if v[i] is not None else None
            if expected!=row['nmse'][k]:errors.append('evaluation score mismatch')
    manifest=read(root/'manifest.json');src=Path(__file__).parent
    for name,h in manifest['source_hashes'].items():
        if hashlib.sha256((src/name).read_bytes()).hexdigest()!=h:errors.append('source changed '+name)
    return dict(passed=not errors,errors=errors,calls=len(wires),executed_pairs=pairs,input_tokens=usage[0],completion_tokens=usage[1],
        reported_reasoning_tokens=usage[2],reasoning_detail_missing_responses=missing)


if __name__=='__main__':
    import sys
    print(json.dumps(audit(sys.argv[1]),indent=2))
