"""Forecast and observation binding shared by tools and real-model runs."""
import hashlib
import json
from pathlib import Path
import time
import sys
import numpy as np
import scipy
from engine import write, digest, control, nmse
from memory import fit_version, observation_hash
from numerics import predict


def freeze(root, extra):
    src=Path(__file__).parent
    value=dict(time_ns=time.time_ns(), source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(src.glob('*.py'))}, plan_sha256=hashlib.sha256((src/'PLAN.md').read_bytes()).hexdigest(),
        runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__), **extra)
    write(Path(root)/'manifest.json',value);return value


def commit(root, name, models, actions, observation_ids, **extra):
    if len(actions)!=len(observation_ids) or len(set(observation_ids))!=len(actions):
        raise ValueError('Actions and unique observation IDs must align')
    predictions={k:[predict(m,control(a)).tolist() for a in actions] for k,m in models.items()}
    record=dict(time_ns=time.time_ns(), models=models, fit_versions={k:fit_version(m) for k,m in models.items()},
        actions=actions, observation_ids=observation_ids, predictions=predictions, **extra)
    packet=dict(record=record,sha256=digest(record));write(Path(root)/(name+'_forecast.json'),packet)
    return packet


def execute(root, name, packet, observer):
    rec=packet['record']; observations=[]
    for action, identifier in zip(rec['actions'],rec['observation_ids']):
        obs=observer(action,identifier);obs['time_ns']=time.time_ns();observations.append(obs)
    result=dict(time_ns=time.time_ns(), forecast_sha256=packet['sha256'], observations=observations,
        observation_hashes=[observation_hash(o) for o in observations],
        nmse={k:[nmse(y,np.array(o['x'])) for y,o in zip(ys,observations)] for k,ys in rec['predictions'].items()})
    write(Path(root)/(name+'_outcome.json'),result);return result


def audit_pair(packet, outcome):
    errors=[];rec=packet['record'];obs=outcome['observations']
    if digest(rec)!=packet['sha256'] or outcome['forecast_sha256']!=packet['sha256']:
        errors.append('forecast hash mismatch')
    if len(obs)!=len(rec['actions']):errors.append('observation count mismatch')
    if [observation_hash(o) for o in obs]!=outcome['observation_hashes']:errors.append('observation hash mismatch')
    for a,oid,o in zip(rec['actions'],rec['observation_ids'],obs):
        if not rec['time_ns']<o['time_ns']<=outcome['time_ns']:errors.append('forecast/observation order')
        if o['id']!=oid or o['action']!=a or not np.array_equal(o['u'],control(a)):errors.append('input/ID mismatch')
    for key,model in rec['models'].items():
        if rec['fit_versions'][key]!=fit_version(model):errors.append('fit binding mismatch')
        for i,a in enumerate(rec['actions']):
            if not np.allclose(predict(model,control(a)),rec['predictions'][key][i],rtol=1e-12,atol=1e-12):
                errors.append('prediction recomputation mismatch')
            score=nmse(rec['predictions'][key][i],np.array(obs[i]['x']))
            if not np.isclose(score,outcome['nmse'][key][i],rtol=1e-12,atol=1e-12):errors.append('score mismatch')
    return errors


def audit(root):
    root=Path(root);read=lambda p:json.loads(p.read_text());errors=[];count=0
    for p in sorted(root.glob('*_forecast.json')):
        count+=1;outcome=read(p.with_name(p.name.replace('_forecast.json','_outcome.json')))
        errors.extend(p.name+': '+e for e in audit_pair(read(p),outcome))
    manifest=read(root/'manifest.json');src=Path(__file__).parent
    for name,h in manifest['source_hashes'].items():
        if hashlib.sha256((src/name).read_bytes()).hexdigest()!=h:errors.append('source changed '+name)
    if hashlib.sha256((src/'PLAN.md').read_bytes()).hexdigest()!=manifest['plan_sha256']:errors.append('plan changed')
    for p in root.glob('*_forecast.json'):
        if read(p)['record']['time_ns']<=manifest['time_ns']:errors.append('prediction before freeze')
    return dict(passed=not errors, errors=errors, committed_experiments=count)
