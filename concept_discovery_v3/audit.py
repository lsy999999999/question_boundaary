import json,hashlib
from pathlib import Path
from engine import digest


def audit(root):
    root=Path(root);read=lambda p:json.loads(p.read_text());errors=[];ids=[];usage=[0,0,0]
    wires=sorted((root/'wire').iterdir())
    if len(wires)>20: errors.append('call cap')
    for w in wires:
        req=read(w/'request.json');res=read(w/'response.json');body=res['body'];ids.append(body.get('id'))
        if req['payload']['model']!='gpt-6-luna' or body['model']!='gpt-6-luna': errors.append('model identity')
        if req['payload']['max_completion_tokens']!=2048 or body['usage']['completion_tokens']>2048: errors.append('token cap')
        if res['time_ns']<=req['time_ns']: errors.append('request chronology')
        if body['choices'][0]['finish_reason']!='stop': errors.append('incomplete response')
        usage[0]+=body['usage']['prompt_tokens'];usage[1]+=body['usage']['completion_tokens'];usage[2]+=body['usage'].get('completion_tokens_details',{}).get('reasoning_tokens',0)
    if None in ids or len(set(ids))!=len(ids): errors.append('response uniqueness')
    for p in (root/'decisions').glob('*.json'):
        data=read(p);wire=data['generation_records'][-1]['wire'];body=read(root/wire/'response.json')['body']
        raw=body['choices'][0]['message']['content'].strip()
        if raw.startswith('```'): raw=raw.split('\n',1)[1].rsplit('```',1)[0].strip()
        if json.loads(raw)!=data['value']: errors.append('decision binding '+p.name)
    pairs=0
    for p in root.glob('round_*/forecast_commit.json'):
        fc=read(p);record=fc['record'];pairs+=1
        if digest(record)!=fc['sha256']: errors.append('forecast hash')
        if not record['compiler']['passed'] or not record['compiler']['guard']['passed']: errors.append('unadmitted design executed')
        r=int(p.parent.name.split('_')[1])
        for i in range(2):
            o=read(root/'observations'/f'v3_r{r}_experiment_{i}.json')
            if o['time_ns']<=record['time_ns']: errors.append('observation before prediction')
            if o['action']!=record['actions'][i]: errors.append('input changed after prediction')
    final=read(root/'final_commit.json');sealed=read(root/'sealed_result.json');commit=read(root/'sealed_input_commit.json')
    if digest(final['record'])!=final['sha256']: errors.append('final hash')
    if digest(commit['actions'])!=commit['sha256']: errors.append('sealed input hash')
    if not commit['time_ns']<final['record']['time_ns']<sealed['time_ns']: errors.append('sealed chronology')
    if any(read(w/'request.json')['time_ns']>=final['record']['time_ns'] for w in wires): errors.append('post-sealed model call')
    return dict(passed=not errors,errors=errors,real_model_calls=len(wires),executed_pairs=pairs,
                input_tokens=usage[0],completion_tokens=usage[1],reasoning_included=usage[2])


if __name__=='__main__':
    import sys
    print(json.dumps(audit(sys.argv[1]),indent=2))
