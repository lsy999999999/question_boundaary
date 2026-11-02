"""Real-response, decision, evidence-owner and evaluation-order audit."""
import json
from pathlib import Path
from engine import digest
from memory import fit_version, validate_resolutions


def audit_agent(root):
    root=Path(root);read=lambda p:json.loads(p.read_text());errors=[];ids=[];usage=[0,0];times=[]
    wires=sorted((root/'wire').iterdir())
    if len(wires)>20:errors.append('call cap')
    for wire in wires:
        if not (wire/'response.json').exists():errors.append('missing response');continue
        req=read(wire/'request.json');res=read(wire/'response.json');body=res['body']
        ids.append(body.get('id'));times.append(req['time_ns'])
        if not req['time_ns']<res['time_ns']:errors.append('request order')
        if req['payload']['model']!='gpt-6-luna' or body['model']!='gpt-6-luna':errors.append('model label')
        if req['payload']['max_completion_tokens']!=2048 or body['usage']['completion_tokens']>2048:errors.append('token cap')
        if body['choices'][0]['finish_reason']!='stop':errors.append('incomplete response')
        usage[0]+=body['usage']['prompt_tokens'];usage[1]+=body['usage']['completion_tokens']
    if not ids or None in ids or len(ids)!=len(set(ids)):errors.append('missing/duplicate response ID')
    for path in (root/'decisions').glob('*.json'):
        decision=read(path);wire=root/decision['generation_records'][-1]['wire'];response=read(wire/'response.json')
        text=response['body']['choices'][0]['message']['content'].strip()
        if text.startswith('```'):text=text.split('\n',1)[1].rsplit('```',1)[0].strip()
        if json.loads(text)!=decision['value']:errors.append('decision binding '+path.name)
        if response['time_ns']>decision['time_ns']:errors.append('decision before response')
        payload=json.loads(read(wire/'request.json')['payload']['messages'][1]['content'])
        payload=payload.get('original_task',payload);value=decision['value']
        if 'evidence_ids' in value:
            byid={e['id']:e for field in ('cv','relations','regressions') for e in payload[field]}
            parent=value.get('parent_id',value.get('selected_id'))
            for eid in value['evidence_ids']:
                if eid not in byid or (parent and byid[eid].get('model_id') not in (None,parent)):
                    errors.append('evidence ownership '+path.name)
        if path.stem.endswith('resolution'):
            target=payload['target_model_id']
            try:validate_resolutions(value,target,payload['models'][target],payload['regressions'],payload['relations'],payload['raw_observations'])
            except ValueError:errors.append('conflict resolution '+path.name)
    evaluation=read(root/'evaluation_forecast.json');rec=evaluation['record']
    manifest=read(root/'manifest.json')
    if digest(rec['actions'])!=manifest['evaluation_input_sha256']:errors.append('evaluation input changed')
    if not times or max(times)>=rec['time_ns']:errors.append('request after final commit')
    final=read(root/'decisions/final.json')
    if final['value']!=rec['final_decision'] or final['time_ns']>=rec['time_ns']:errors.append('final binding/order')
    memory=read(root/'final_memory.json');selected=final['value']['selected_id']
    if fit_version(memory['models'][selected])!=fit_version(rec['models']['selected']):errors.append('selected fit changed')
    return dict(passed=not errors,errors=errors,calls=len(wires),input_tokens=usage[0],completion_tokens=usage[1],
        scope='Structural and numerical audit; free-text scientific interpretation still needs semantic review')
