"""Real Luna experiment on a fresh system. No simulated language-model responses."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse
import getpass
import json
from pathlib import Path
import time
import numpy as np
from engine import Spec, write, digest, control, summary
from numerics import fit_model, predict, ranking, input_key
from boundaries import validate_boundary, validate_question, compile_question, boundary_label, action
from temporal import SCHEMA
from memory import discover, review, fit_version, validate_resolutions
from protocol import freeze, commit, execute, audit
from transport import Luna
from worlds import configuration, mirror_pair, observe

COMMON='''You are conducting an empirical dynamical-system experiment on a new system.
Only supplied measurements are public. The simulator and evaluation inputs are hidden.
Every trial resets to zero; dt=.1, horizon 12, noise std=.005.
Return JSON, Chinese explanations. Cite supplied evidence. Local mirror relationships
are observations on exact input pairs, not universal laws. A proposed narrower scope
remains a hypothesis until tested. Distinguish posthoc regression, grouped CV, and
committed-before-observation prediction errors. Respect their model and fit versions.
The derivative of x is a fitted linear combination of 1..8 expressions; 0..2 states
z0,z1 have specified rates and start at zero; 0..3 parameters p0,p1,p2 require
.02<=lower<initial<upper<=4. Expressions use x,u,t,z,p, numbers |c|<=10,
+ - * /, literal powers 2/3, unary tanh/sin/cos/abs only. Coefficients fitted in [-8,8].
Fitting uses complete trajectories, two starts, grouped input holdouts. Fit failure
is distinct from evidence against the formula. No external literature retrieval.
Temporal scopes are bounded JSON trees. Numeric leaves or {"signal":"u|t"};
operators {"op":"name","args":[...]}, history operators also require integer steps.
Known planned inputs only: no measured x in scopes. Full planned input may be reduced
by any/all/last before observation; each temporal primitive is causal at its index.
'''

PROPOSE='''Propose one equation addressing current model errors; retaining/removing terms is allowed.
Return {"parent_id":"id","evidence_ids":["id"],"operation":"revise|retain|new",
"reason":"...","spec":{"parameters":[{"name":"p0","lower":.05,"initial":.5,"upper":3}],
"states":[{"name":"z0","meaning":"...","rate":"..."}],"terms":["..."]},
"boundary":{"model_id":"parent_id","status":"no_supported_boundary","reason":"..."}}.
If evidence supports a scope guess, replace boundary with {"model_id":"parent_id",
"fit_version":"full current hash","scope":{"expression":JSON_TREE,"reduce":"any|all|last"},
"error_threshold":.05,"reason":"..."}. This predicts parent whole-trajectory NMSE>.05.
Empty parameter/state arrays are allowed. Do not force a boundary when unsupported.
'''

RESOLVE='''Address every conflict for the target model at its exact fit version.
Return {"resolutions":[{"relation_id":"...","fit_version":"...",
"action":"withdraw_candidate|narrow_claim|test_conflict","reason":"..."}]}.
For narrow_claim add scope={expression:JSON_TREE,reduce:any|all|last} and
status=hypothesis_pending_test. It must split observed inputs; it does NOT erase
the historical regression. For test_conflict add status=hypothesis_pending_test,
experiment=[{"points":[[time,value],...]},{"points":[...]}], a sign-reversed pair
whose predicted mirror residual distinguishes the target from mirror extension.
Inputs: start t=0, 2..7 changes, times 0..11 on .1 grid at least .5 apart, |u|<=1.5.
No conflicts => empty array. A withdrawal retires the candidate.
'''

QUESTION='''Choose a new input pair. Return either
{"mode":"mirror","amplitude":number,"end":number,"reason":"...","evidence_ids":["..."]}
(pulses +A/-A start .5, end chosen in [1,11], |A|<=1.5), or
{"mode":"one_factor","question":{"family":"reversal_depth|recovery_gap|dwell_time",
"purpose":"discriminate|boundary_probe","target_ids":["active id"],
"amplitude_range":[.2,1.5],"value_range":[low,high],"rationale":"...","claim":"...",
"update_if_violated":"..."},"evidence_ids":["..."]}.
reversal_depth: first +/-A .5..3.5, opposite value .2..1.5 until6.5.
recovery_gap: first +/-A .5..3.5, wait value0..3, opposite A for2 seconds.
dwell_time: first +/-A .5..(.5+value), value1..4, opposite A for2.5 seconds.
Compiler searches 3 amplitudes, both signs, 4 values; only model predictions guide it.
Discrimination needs >=2 targets separated by 3*.005*sqrt(2) RMS.
boundary_probe requires a declared scope and a pair straddling it.
Mirror mode tests extension of local mirror evidence; no claim of one-factor timing.
'''


def context(models, obs, episodes):
    relations=discover(obs);checks=review(models,relations,obs)
    cv=[dict(id='cv:'+k+':'+fit_version(m),model_id=k,fit_version=fit_version(m),
        mean_nmse=m['group_cv_nmse'],rows=[dict(ids=f['ids'],nmse=f['nmse']) for f in m['cv_folds']],
        kind='adaptive_grouped_cv') for k,m in models.items()]
    compact=[{k:v for k,v in c.items() if k!='predictions'} for c in checks]
    return dict(models={k:dict(spec=m['spec'],fit=m['fit'],fit_version=fit_version(m)) for k,m in models.items()},
        observations=[summary(o) | {'noise_std':o['noise_std']} for o in obs],
        raw_observations=obs,relations=relations,regressions=compact,cv=cv,
        prospective_episodes=episodes,temporal_schema=SCHEMA)


def evidence_ids(ctx):
    return {x['id'] for field in ('relations','regressions','cv') for x in ctx[field]}


def cite(value,ctx,parent=None):
    ids=value['evidence_ids']
    if not ids or any(x not in evidence_ids(ctx) for x in ids):raise ValueError('Cite supplied evidence')
    if parent:
        owners={x['id']:x.get('model_id') for field in ('relations','regressions','cv') for x in ctx[field]}
        if any(owners[x] not in (None,parent) for x in ids):raise ValueError('Wrong model evidence owner')


def heldout(seed):
    rng=np.random.default_rng(seed+400000)
    return [dict(points=[[0,0]]+[[t,float(v)] for t,v in zip((.5,2.8,5.1,7.5,10.),rng.uniform(-1.4,1.4,5))]) for _ in range(8)]


def run(root,client,family,seed):
    root=Path(root);config=configuration(family,seed);sealed=heldout(seed)
    freeze(root,dict(mode='real Luna on fresh synthetic system',model='gpt-6-luna',
        private_world=config,rounds=3,call_cap=20,completion_cap=2048,
        evaluation_input_sha256=digest(sealed),model_service_identity='requested/returned label'))
    write(root/'private_evaluation_inputs.json',sealed)
    obs=[];episodes=[];withdrawn={}
    def status(stage,**kw):
        rec=dict(stage=stage,time_ns=time.time_ns(),calls=client.count,**kw)
        path=root/'STATUS.tmp';path.write_text(json.dumps(rec));path.replace(root/'STATUS.json');print(json.dumps(rec),flush=True)
    def ask(name,instruction,ctx,validator):
        value,records=client.structured(name,COMMON+instruction,ctx,validator)
        write(root/'decisions'/(name+'.json'),dict(time_ns=time.time_ns(),value=value,generation_records=records))
        return value
    for amplitude in (.4,.7):
        for a in mirror_pair(amplitude):
            o=observe(config,a,'initial_'+str(len(obs)));o['time_ns']=time.time_ns();obs.append(o)
    # Initial measurements are public calibration, with no fabricated prior predictions.
    write(root/'initial_observations.json',obs)
    raw=dict(parameters=[],states=[],terms=['x','u'])
    models={'initial':fit_model(raw,obs)}
    write(root/'initial_models.json',models)
    for r in range(3):
        ctx=context(models,obs,episodes);status('proposal',round=r)
        def vp(v):
            if v['parent_id'] not in models:raise ValueError('Unknown parent')
            cite(v,ctx,v['parent_id']);Spec(v['spec']);validate_boundary(v['boundary'],models)
            if v['boundary']['model_id']!=v['parent_id']:raise ValueError('Wrong boundary owner')
            if v['operation'] not in ('revise','retain','new'):raise ValueError('Invalid operation')
        proposal=ask(f'r{r}_proposal',PROPOSE,ctx,vp);key=f'v5_r{r}';boundary=proposal['boundary']
        status('fit_proposal',round=r)
        try:models[key]=fit_model(proposal['spec'],obs)
        except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError) as exc:
            write(root/f'r{r}_fit_failure.json',dict(error=str(exc),proposal=proposal));continue
        ctx=context(models,obs,episodes);write(root/f'r{r}_memory_before.json',ctx)
        conflicts=[c for c in ctx['regressions'] if c['model_id']==key and c.get('conflict') is True]
        resolution=None
        if conflicts:
            ctx['target_model_id']=key
            resolution=ask(f'r{r}_resolution',RESOLVE,ctx,
                lambda v:validate_resolutions(v,key,models[key],ctx['regressions'],ctx['relations'],obs))
            if any(x['action']=='withdraw_candidate' for x in resolution['resolutions']):
                withdrawn[key]=models.pop(key)
        ctx=context(models,obs,episodes);ctx.update(declared_boundary=boundary,conflict_treatment=resolution)
        compiled=None
        for attempt in range(2):
            def vq(v):
                cite(v,ctx)
                if v['mode']=='mirror':
                    if not .2<=v['amplitude']<=1.5 or not 1.<=v['end']<=11.:raise ValueError('Mirror amplitude/end bounds')
                    for a in mirror_pair(v['amplitude'],v['end']):control(a)
                elif v['mode']=='one_factor':validate_question(v['question'],models)
                else:raise ValueError('Unknown question mode')
            q=ask(f'r{r}_question_{attempt}',QUESTION,ctx,vq)
            if q['mode']=='mirror':
                actions=mirror_pair(q['amplitude'],q['end']);known={input_key(o) for o in obs}
                compiled=dict(passed=all(tuple(control(a).round(12)) not in known for a in actions),actions=actions)
            else:compiled=compile_question(q['question'],models,obs,boundary)
            write(root/f'r{r}_design_{attempt}.json',dict(question=q,compiled=compiled))
            if compiled['passed']:break
            ctx['compiler_feedback']=compiled
        if not compiled['passed']:continue
        packet=commit(root,f'r{r}',models,compiled['actions'],[f'r{r}_{i}' for i in range(2)],
            question=q,boundary=boundary,boundary_labels=[boundary_label(boundary,control(a)) for a in compiled['actions']])
        result=execute(root,f'r{r}',packet,lambda a,i:observe(config,a,i));obs.extend(result['observations'])
        owner=boundary['model_id'];labels=packet['record']['boundary_labels'];scores=result['nmse'][owner]
        episode=dict(id=f'prospective:r{r}',fit_versions=packet['record']['fit_versions'],
            forecast_sha256=packet['sha256'],nmse=result['nmse'],kind='prediction_before_observation',
            boundary=boundary,labels=labels,label_correct=[None if l is None else l==(s>.05) for l,s in zip(labels,scores)])
        episodes.append(episode);write(root/f'r{r}_prospective.json',episode)
        status('refit',round=r)
        refreshed={}
        for k,m in models.items():
            try:refreshed[k]=fit_model(m['spec'],obs,warm=m['fit'])
            except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError) as exc:
                write(root/f'r{r}_refit_failure_{k}.json',dict(error=str(exc)))
        models=refreshed
        if not models:raise RuntimeError('No executable models')
        ctx=context(models,obs,episodes);write(root/f'r{r}_memory_after.json',ctx)
        def va(v):
            if v['forecast_sha256']!=packet['sha256']:raise ValueError('Wrong forecast reference')
            if v['boundary_verdict']!=('untested' if all(l is None for l in labels) else
                    ('supported_on_pair' if all(episode['label_correct']) else 'violated_on_pair')):
                raise ValueError('Verdict disagrees with committed predictions')
            if not v['reason'] or not v['next_question']:raise ValueError('Explain assessment')
        ask(f'r{r}_assessment','Assess the last experiment, using prospective errors, not refitted errors. '
            'Return {"forecast_sha256":"...","boundary_verdict":"untested|supported_on_pair|violated_on_pair",'
            '"reason":"...","next_question":"..."}.',ctx,va)
    ctx=context(models,obs,episodes);write(root/'final_memory.json',ctx)
    def vf(v):
        if v['selected_id'] not in models:raise ValueError('Select executable model')
        if v['reason_model_id']!=v['selected_id']:raise ValueError('Reason must bind selected model')
        expected=sorted(c['id'] for c in ctx['regressions'] if c['model_id']==v['selected_id'] and c.get('conflict') is True)
        if sorted(v['unresolved_regression_ids'])!=expected:raise ValueError('Expose all remaining regressions')
        cite(v,ctx,v['selected_id'])
    final=ask('final','Choose final model. Return {"selected_id":"...","reason_model_id":"same id",'
        '"reason":"...","evidence_ids":["..."],"unresolved_regression_ids":["all current conflicting regression IDs"]}. '
        'An acknowledged conflict remains visible; it does not forbid a scientifically warranted new model.',ctx,vf)
    selected=models[final['selected_id']]
    # Same-data old-formula refit and numerical model-selection baseline.
    old=fit_model(raw,obs);cvbest=min(models,key=lambda k:ranking(models[k]))
    packet=commit(root,'evaluation',{'selected':selected,'initial_formula_refit':old,'cv_best':models[cvbest]},
        sealed,[f'evaluation_{i}' for i in range(len(sealed))],final_decision=final,cv_best_id=cvbest)
    execute(root,'evaluation',packet,lambda a,i:observe(config,a,i))
    result=audit(root)
    from audit_agent import audit_agent
    result['agent']=audit_agent(root);result['passed'] &= result['agent']['passed']
    write(root/'AUDIT.json',result);status('completed' if result['passed'] else 'audit_failed')
    if not result['passed']:raise RuntimeError('Audit failed')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    p.add_argument('--family',choices=['linear_memory','saturated_memory','local_symmetry_only'],required=True)
    p.add_argument('--seed',type=int,required=True);p.add_argument('--key-env',default='LUNA_API_KEY')
    args=p.parse_args();key=os.environ.get(args.key_env) or getpass.getpass('API key (hidden, not saved): ')
    if not key:raise SystemExit('API credential required')
    root=Path(args.out);root.mkdir(parents=True,exist_ok=False);client=Luna(key,root)
    try:run(root,client,args.family,args.seed)
    except Exception as exc:
        write(root/'FAILURE.json',dict(time_ns=time.time_ns(),calls=client.count,
            type=type(exc).__name__,error=str(exc).replace(key,'[redacted]')))
        raise SystemExit('Run stopped; redacted failure saved') from None
