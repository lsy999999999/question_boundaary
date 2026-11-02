"""Compile scientific questions using submitted models only. No world imports."""
import numpy as np
from engine import GRID,control
from numerics import predict,groups,input_key,ranking


def relation_reports(obs):
    gs=groups(obs);out=[]
    for i,a in enumerate(gs):
        ua=np.array(a[0]['u']);xa=np.mean([o['x'] for o in a],axis=0)
        if np.linalg.norm(ua)<.1: continue
        for b in gs[i+1:]:
            ub=np.array(b[0]['u']);xb=np.mean([o['x'] for o in b],axis=0)
            factor=float(ua@ub/(ua@ua))
            if abs(factor)<.1 or not np.allclose(ub,factor*ua,atol=1e-10): continue
            kind='polarity' if abs(factor+1)<1e-8 else 'scaling'
            rms=float(np.sqrt(np.mean((xb-factor*xa)**2)))
            noise=float(.005*np.sqrt(1/len(b)+factor**2/len(a)))
            out.append(dict(id='relation_'+a[0]['id']+'_'+b[0]['id'],kind=kind,
                observations=[[o['id'] for o in a],[o['id'] for o in b]],factor=factor,
                measured_relation_rms=rms,expected_noise_rms=noise,
                description='Consistent with noise scale on these inputs' if rms<=2*noise else 'Deviation exceeds twice noise RMS; descriptive only'))
    return out


def validate_question(q,ids):
    if q['kind'] not in ('polarity','scaling','matched_history'): raise ValueError('Unsupported executable question kind')
    if q['purpose'] not in ('probe_relation','discriminate'): raise ValueError('Unknown purpose')
    if not q['target_ids'] or any(k not in ids for k in q['target_ids']): raise ValueError('Unknown active target')
    if q['purpose']=='discriminate' and len(set(q['target_ids']))<2: raise ValueError('Need two different active targets')
    if q['kind']=='matched_history' and q['purpose']!='discriminate': raise ValueError('Matched history needs competing predictions')
    for key in ('rationale','claim','update_if_violated'):
        if not isinstance(q[key],str) or not q[key]: raise ValueError('Missing scientific rationale')
    if not .1<=q['amplitude_range'][0]<=q['amplitude_range'][1]<=1.5: raise ValueError('Amplitude range .1..1.5')
    if not 1<=q['duration_range'][0]<=q['duration_range'][1]<=5: raise ValueError('Duration range 1..5')
    if not 1.2<=q['scale']<=2: raise ValueError('Scale 1.2..2')
    if not .01<=q['tolerance_x']<=.04: raise ValueError('Tolerance .01..04')


def model_guard(q,actions,models):
    try: forecasts={k:[predict(m,control(a)).tolist() for a in actions] for k,m in models.items()}
    except (ValueError,TypeError,ArithmeticError) as exc:
        return dict(passed=False,reason='Model rollout failure: '+str(exc),forecasts={})
    targets=q['target_ids'];noise=.005*np.sqrt(2)
    if q['kind']=='matched_history':
        k=80
        gaps={name:abs(y[0][k]-y[1][k]) for name,y in forecasts.items()}
        effects={name:((y[0][85]-y[0][80])-(y[1][85]-y[1][80]))/.5 for name,y in forecasts.items()}
        contrast=max(effects[t] for t in targets)-min(effects[t] for t in targets)
        passed=max(gaps.values())<=q['tolerance_x']*.5 and contrast>=.06
        return dict(passed=bool(passed),reason='conditional matching and contrast checked',forecasts=forecasts,
            predicted_gaps=gaps,predicted_effects=effects,contrast=float(contrast),
            required_predicted_match=q['tolerance_x']*.5,endpoint_effect_noise_sd=.02)
    contrast=max([float(np.sqrt(np.mean((np.array(forecasts[a])-forecasts[b])**2)))
                  for a in targets for b in targets]+[0.])
    passed=q['purpose']=='probe_relation' or contrast>=3*noise
    return dict(passed=bool(passed),reason='Explicit structural probe' if q['purpose']=='probe_relation' else 'Candidate prediction separation',
        forecasts=forecasts,contrast=contrast,noise_rms=noise,
        note='A structural probe may test a shared assumption even when candidate predictions agree; no discrimination claim then.')


def compile_question(q,models,obs,seed):
    targets={k:models[k] for k in q['target_ids']}
    # Include current best as a guard when it is not explicitly targeted.
    best=min(models,key=lambda k:ranking(models[k]));targets[best]=models[best]
    known={input_key(o) for o in obs};candidates=[]
    if q['kind']=='matched_history':
        rng=np.random.default_rng(seed)
        for _ in range(96):
            amps=rng.uniform(-q['amplitude_range'][1],q['amplitude_range'][1],4)
            if np.linalg.norm(amps)<.3: continue
            candidates.append([dict(points=[[0,0]]+[[t,float(sign*v)] for t,v in zip((.5,2,4,6),amps)]+[[7,0]]) for sign in (1,-1)])
    else:
        for amp in np.linspace(*q['amplitude_range'],4):
            for duration in np.unique(np.round(np.linspace(*q['duration_range'],4),1)):
                factor=-1 if q['kind']=='polarity' else q['scale']
                if abs(amp*factor)>1.5: continue
                candidates.append([dict(points=[[0,0],[.5,float(amp*f)],[round(.5+duration,1),0]]) for f in (1,factor)])
    admitted=[];rejected=[]
    for actions in candidates:
        us=[control(a) for a in actions]
        if all(tuple(u.round(12)) in known for u in us):
            rejected.append(dict(reason='Both numeric input schedules already observed'));continue
        guard=model_guard(q,actions,targets)
        if not guard['passed']:
            rejected.append({k:v for k,v in guard.items() if k!='forecasts'});continue
        novelty=min(float(np.sqrt(np.mean((u-np.array(o['u']))**2))) for u in us for o in obs)
        score=guard['contrast']+(.2*novelty if q['purpose']=='probe_relation' else 0)
        admitted.append((score,actions,guard))
    if not admitted:
        return dict(passed=False,reason='No admissible design in bounded candidate search; not proof of infeasibility',
            considered=len(candidates),rejected_examples=rejected[:3])
    _,actions,guard=max(admitted,key=lambda a:a[0])
    return dict(passed=True,actions=actions,guard=guard,considered=len(candidates),
        rejected_count=len(rejected),rejected_examples=rejected[:3],
        conditional='Based only on submitted fitted models. Actual conditions must still be checked.')


def evaluate_observed(q,new_obs,forecasts):
    from engine import nmse
    a,b=new_obs;xa,xb=np.array(a['x']),np.array(b['x'])
    result=dict(prediction_nmse={k:[nmse(y,np.array(o['x'])) for y,o in zip(v,new_obs)] for k,v in forecasts.items()})
    if q['kind']=='matched_history':
        gap=abs(xa[80]-xb[80]);same=np.allclose(a['u'][80:86],b['u'][80:86])
        result.update(actual_conditions_met=bool(gap<=q['tolerance_x'] and same),actual_state_gap=float(gap),
            observed_slope_effect=float(((xa[85]-xa[80])-(xb[85]-xb[80]))/.5),
            interpretation='Matched-history inference is unavailable if actual conditions failed; full prediction errors remain usable.')
    else:
        factor=-1 if q['kind']=='polarity' else q['scale']
        condition=bool(np.allclose(np.array(b['u']),factor*np.array(a['u'])))
        rms=float(np.sqrt(np.mean((xb-factor*xa)**2)));noise=float(.005*np.sqrt(1+factor**2))
        result.update(actual_conditions_met=condition,relation_rms=rms,expected_noise_rms=noise,
            relation_result='consistent_at_noise_scale' if rms<=2*noise else 'deviation_above_noise_scale',
            predicted_relation_rms={k:float(np.sqrt(np.mean((np.array(v[1])-factor*np.array(v[0]))**2))) for k,v in forecasts.items()},
            interpretation='Descriptive evidence for these executed inputs, not a universal law or significance certificate.')
    return result
