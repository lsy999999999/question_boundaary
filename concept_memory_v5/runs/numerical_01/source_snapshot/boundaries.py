"""Public input features and one-factor experiment search; no simulator access."""
import itertools
import numpy as np
from engine import GRID,control,nmse,digest
from numerics import predict,input_key
from temporal import validate_scope,label

FEATURES={'peak_abs','reversal_count','max_reversal_jump','absolute_area','signed_area','longest_sign_duration','total_variation'}
FAMILIES={'reversal_depth':(.2,1.5),'recovery_gap':(0.,3.),'dwell_time':(1.,4.)}


def features(u):
    u=np.asarray(u,float);levels=[]
    for x in u[:-1]:
        if abs(x)>.1 and (not levels or x!=levels[-1]):levels.append(float(x))
    rev=[abs(b-a) for a,b in zip(levels,levels[1:]) if a*b<0]
    longest=run=0.;last=0
    for x in u[:-1]:
        sign=int(np.sign(x)) if abs(x)>.1 else 0
        run=run+.1 if sign and sign==last else (.1 if sign else 0.)
        longest=max(longest,run);last=sign
    return dict(peak_abs=float(abs(u).max()),reversal_count=len(rev),max_reversal_jump=max(rev,default=0.),
        absolute_area=float(abs(u[:-1]).sum()*.1),signed_area=float(u[:-1].sum()*.1),
        longest_sign_duration=float(round(longest,6)),total_variation=float(abs(np.diff(u)).sum()))


def validate_boundary(b,models):
    if b['model_id'] not in models:raise ValueError('Boundary owner must be executable')
    if b.get('status')=='no_supported_boundary':
        if not b.get('reason'):raise ValueError('Explain abstention')
        return
    validate_scope(b['scope'])
    if b['fit_version']!=digest(dict(spec=models[b['model_id']]['spec'],fit=models[b['model_id']]['fit'])):raise ValueError('Boundary must bind exact current fit')
    if b['error_threshold']!=.05:raise ValueError('Fixed NMSE event threshold is .05')
    if not isinstance(b['reason'],str) or not b['reason']:raise ValueError('Explain proposed scope')


def boundary_label(b,u):
    if b.get('status')=='no_supported_boundary':return None
    return label(b['scope'],u)


def action(family,amplitude,sign,value):
    a=float(sign*amplitude);v=float(value)
    if family=='reversal_depth':pts=[[0,0],[.5,a],[3.5,-sign*v],[6.5,0]]
    elif family=='recovery_gap':pts=[[0,0],[.5,a],[3.5,0],[float(round(3.5+v,1)),-a],[float(round(5.5+v,1)),0]]
    elif family=='dwell_time':pts=[[0,0],[.5,a],[float(round(.5+v,1)),-a],[float(round(3.+v,1)),0]]
    else:raise ValueError('Unknown experiment family')
    # Zero recovery gap is a direct sign reversal, with one event at that time.
    bytime={float(t):float(x) for t,x in pts}
    return dict(points=[[t,bytime[t]] for t in sorted(bytime)])


def validate_question(q,models):
    if q['family'] not in FAMILIES or q['purpose'] not in ('discriminate','boundary_probe'):raise ValueError('Unknown family/purpose')
    if not q['target_ids'] or any(k not in models for k in q['target_ids']):raise ValueError('Unknown executable target')
    if q['purpose']=='discriminate' and len(set(q['target_ids']))<2:raise ValueError('Discrimination needs two models')
    lo,hi=FAMILIES[q['family']]
    if not lo<=q['value_range'][0]<q['value_range'][1]<=hi:raise ValueError('Invalid family value range')
    if not .2<=q['amplitude_range'][0]<=q['amplitude_range'][1]<=1.5:raise ValueError('Conditioning amplitude .2..1.5')
    for k in ('rationale','claim','update_if_violated'):
        if not isinstance(q[k],str) or not q[k]:raise ValueError('Missing '+k)


def compile_question(q,models,obs,boundary):
    known={input_key(o) for o in obs};accepted=[];rejected=[];count=0
    values=np.unique(np.round(np.linspace(*q['value_range'],4),1))
    targets=list(dict.fromkeys(q['target_ids']+[boundary['model_id']]))
    for amp,sign,pair in itertools.product(np.unique(np.linspace(*q['amplitude_range'],3)),(1,-1),itertools.combinations(values,2)):
        count+=1;acts=[action(q['family'],float(amp),sign,float(v)) for v in pair]
        try:us=[control(a) for a in acts]
        except ValueError as exc:rejected.append('Invalid input schedule: '+str(exc));continue
        if any(tuple(u.round(12)) in known for u in us):rejected.append('At least one input already observed');continue
        try:ys={k:[predict(models[k],u).tolist() for u in us] for k in targets}
        except (ValueError,ArithmeticError,TypeError) as exc:rejected.append('Target rollout failed: '+str(exc));continue
        try:labels=[boundary_label(boundary,u) for u in us]
        except ValueError as exc:rejected.append('Scope undefined: '+str(exc));continue
        contrasts=[float(np.sqrt(np.mean((np.array(ys[a])-ys[b])**2))) for a,b in itertools.combinations(q['target_ids'],2)]
        contrast=max(contrasts,default=0.);straddles=labels[0]!=labels[1]
        if q['purpose']=='boundary_probe' and not straddles:rejected.append('Does not straddle declared boundary');continue
        if q['purpose']=='discriminate' and contrast<3*.005*np.sqrt(2):rejected.append('Predicted separation below 3 noise RMS');continue
        descriptor=dict(family=q['family'],amplitude=float(amp),sign=sign,values=[float(x) for x in pair])
        accepted.append((contrast+(3*.005*np.sqrt(2) if straddles else 0.),acts,descriptor,labels,contrast))
    if not accepted:return dict(passed=False,considered=count,rejected_count=len(rejected),reasons={k:rejected.count(k) for k in sorted(set(rejected))},note='Bounded search only; failure is not proof of impossibility')
    _,acts,descriptor,labels,contrast=max(accepted,key=lambda row:row[0])
    return dict(passed=True,actions=acts,descriptor=descriptor,guard=dict(passed=True,contrast_rms=contrast,
        minimum_discrimination_rms=float(3*.005*np.sqrt(2)),boundary_labels=labels,straddles_boundary=labels[0]!=labels[1]),
        considered=count,rejected_count=len(rejected),reasons={k:rejected.count(k) for k in sorted(set(rejected))})


def evaluate(question,compiled,boundary,observations,forecasts):
    desc=compiled['descriptor'];expected=[action(desc['family'],desc['amplitude'],desc['sign'],v) for v in desc['values']]
    conditions=all(np.array_equal(control(a),np.array(o['u'])) for a,o in zip(expected,observations))
    scores={k:[nmse(np.array(y),np.array(o['x'])) for y,o in zip(ys,observations)] for k,ys in forecasts.items()}
    owner=boundary['model_id'];observed=[x>.05 for x in scores[owner]];predicted=[boundary_label(boundary,o['u']) for o in observations]
    return dict(actual_conditions_met=conditions,prediction_nmse=scores,
        boundary_owner=owner,boundary=boundary,predicted_high_error=predicted,observed_high_error=observed,
        boundary_label_correct=[a==b if a is not None else None for a,b in zip(predicted,observed)],
        features=[features(o['u']) for o in observations],
        scope='Prospective errors on this one-factor pair only; .05 is a fixed operational threshold, not a physical law')


def diagnostics(models,obs):
    byid={o['id']:o for o in obs};out=[]
    for key,m in models.items():
        fitid=digest(dict(spec=m['spec'],fit=m['fit']));rows=[]
        for fold in m['cv_folds']:
            for oid,y in zip(fold['ids'],fold['predictions']):
                o=byid[oid];score=nmse(np.array(y),np.array(o['x']));err=np.array(y)-o['x'];ix=int(np.argmax(abs(err)))
                rows.append(dict(observation=oid,nmse=score,high_error=score>.05,features=features(o['u']),peak_error_time=float(GRID[ix]),signed_peak_error=float(err[ix]),origin=o['origin']))
        out.append(dict(id='scope:'+key+':'+fitid,owner_model_id=key,fit_version=fitid,kind='adaptive_grouped_cv_scope',rows=rows))
    return out
