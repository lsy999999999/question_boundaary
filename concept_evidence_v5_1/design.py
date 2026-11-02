"""Finite input search using submitted predictions, never simulator truth."""
import itertools
import numpy as np
from engine import control
from numerics import predict,input_key
from scope import label

RANGES={'reversal_depth':(.2,1.5),'recovery_gap':(0.,3.),'dwell_time':(1.,4.),'polarity':(1.,5.)}


def action(family,amplitude,sign,value):
    a=float(sign*amplitude);v=float(value)
    if family=='reversal_depth':pts=[[0,0],[.5,a],[3.5,-sign*v],[6.5,0]]
    elif family=='recovery_gap':pts=[[0,0],[.5,a],[3.5,0],[float(round(3.5+v,1)),-a],[float(round(5.5+v,1)),0]]
    elif family=='dwell_time':pts=[[0,0],[.5,a],[float(round(.5+v,1)),-a],[float(round(3+v,1)),0]]
    elif family=='polarity':pts=[[0,0],[.5,a],[float(round(.5+v,1)),0]]
    else:raise ValueError('Unknown family')
    points={float(t):float(x) for t,x in pts};return dict(points=[[t,points[t]] for t in sorted(points)])


def pair(desc):
    if desc['family']=='polarity':return [action('polarity',desc['amplitude'],s,desc['values'][0]) for s in (1,-1)]
    return [action(desc['family'],desc['amplitude'],desc['sign'],v) for v in desc['values']]


def validate(q,ids,boundary):
    if q['family'] not in RANGES:raise ValueError('Unsupported family')
    if q['purpose'] not in ('discriminate','boundary_probe','probe_relation'):raise ValueError('Unknown purpose')
    if not q['target_ids'] or any(k not in ids for k in q['target_ids']):raise ValueError('Unknown executable target')
    if q['purpose']=='discriminate' and len(set(q['target_ids']))<2:raise ValueError('Need two distinct targets')
    if q['purpose']=='probe_relation' and q['family']!='polarity':raise ValueError('Relation probe only for polarity')
    if q['purpose']=='boundary_probe' and boundary['status']!='proposed':raise ValueError('No proposed boundary to probe')
    lo,hi=RANGES[q['family']]
    if not lo<=q['value_range'][0]<q['value_range'][1]<=hi:raise ValueError('Invalid value range')
    if not .2<=q['amplitude_range'][0]<=q['amplitude_range'][1]<=1.5:raise ValueError('Amplitude range .2..1.5')
    if not isinstance(q['rationale'],str) or not q['rationale']:raise ValueError('Explain experiment intent')


def compile_question(q,models,obs,boundary):
    known={input_key(o) for o in obs};targets=list(dict.fromkeys(q['target_ids']+[boundary['model_id']]))
    values=np.unique(np.round(np.linspace(*q['value_range'],4),1));amps=np.unique(np.linspace(*q['amplitude_range'],3));candidates=[]
    if q['family']=='polarity':
        candidates=[dict(family='polarity',amplitude=float(a),sign=1,values=[float(v)]) for a,v in itertools.product(amps,values)]
    else:candidates=[dict(family=q['family'],amplitude=float(a),sign=s,values=[float(v) for v in vv]) for a,s,vv in itertools.product(amps,(1,-1),itertools.combinations(values,2))]
    rejected=[];admitted=[]
    for desc in candidates:
        acts=pair(desc);us=[control(a) for a in acts]
        if any(tuple(u.round(12)) in known for u in us):rejected.append('input already observed');continue
        try:
            predictions={k:[predict(models[k],u).tolist() for u in us] for k in targets};labels=[label(boundary,u) for u in us]
        except (ValueError,ArithmeticError,TypeError) as exc:rejected.append('unexecutable forecast or predicate');continue
        contrasts=[float(np.sqrt(np.mean((np.array(predictions[a])-predictions[b])**2))) for a,b in itertools.combinations(q['target_ids'],2)]
        contrast=max(contrasts,default=0.);split=labels[0]!=labels[1]
        if q['purpose']=='discriminate' and contrast<3*.005*np.sqrt(2):rejected.append('insufficient predicted separation');continue
        if q['purpose']=='boundary_probe' and not split:rejected.append('not straddling declared predicate');continue
        novelty=min(float(np.sqrt(np.mean((u-np.array(o['u']))**2))) for u in us for o in obs)
        score=contrast+(.021213203435596427 if split else 0.)+(.2*novelty if q['purpose']=='probe_relation' else 0.)
        admitted.append((score,acts,desc,labels,contrast))
    summary=dict(considered=len(candidates),rejected_count=len(rejected),reasons={k:rejected.count(k) for k in sorted(set(rejected))})
    if not admitted:return dict(passed=False,reason='No design in this bounded search; not proof of impossibility',**summary)
    _,acts,desc,labels,contrast=max(admitted,key=lambda row:row[0])
    return dict(passed=True,actions=acts,descriptor=desc,guard=dict(passed=True,contrast_rms=contrast,boundary_labels=labels,straddles=labels[0]!=labels[1]),**summary)
