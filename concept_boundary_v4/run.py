import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import argparse,getpass,hashlib,json,sys,time
from pathlib import Path
import numpy as np
import scipy
from engine import Spec,write,digest,control,nmse
from numerics import fit_model,structural_key,ranking,public,failures_for,predict,validate_evidence_ownership
from boundaries import features,diagnostics,validate_boundary,validate_question,compile_question,evaluate,boundary_label,action
from prompts import COMMON,PROPOSAL,QUESTION
from transport import Luna,MODEL
from world import observe,truth


def status(root,stage,**extra):
    data=dict(stage=stage,time_ns=time.time_ns(),pid=os.getpid(),**extra)
    p=root/'LIVE_STATUS.tmp';p.write_text(json.dumps(data));p.replace(root/'LIVE_STATUS.json');print(json.dumps(data),flush=True)


def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def fixed_inputs():
    rng=np.random.default_rng(2026110104);out=[]
    for family in ('reversal_depth','recovery_gap','dwell_time','reversal_depth'):
        ranges={'reversal_depth':(.25,1.4),'recovery_gap':(.2,2.8),'dwell_time':(1.2,3.8)}
        out.append(action(family,float(rng.uniform(.35,1.4)),int(rng.choice([-1,1])),float(round(rng.uniform(*ranges[family]),1))))
    for _ in range(4):
        out.append(dict(points=[[0,0]]+[[float(t),float(v)] for t,v in zip((.7,2.8,5.2,7.6,10.1),rng.uniform(-1.4,1.4,5))]))
    return out


def run(root,client,seedfile):
    seed=json.loads(seedfile.read_text());obs=seed['observations'];nodes={};models={};events=[];episodes=[];seen={}
    write(root/'manifest.json',dict(version='concept_boundary_v4',time_ns=time.time_ns(),model=MODEL,
        source_hashes={p.name:filehash(p) for p in sorted(Path(__file__).parent.glob('*.py'))},seed_sha256=filehash(seedfile),
        plan_sha256=filehash(Path(__file__).parent/'PLAN.md'),python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
        rounds=3,call_cap=20,completion_cap=2048,fit_starts=2,fit_max_nfev=35,boundary_nmse_threshold=.05,
        scope='same previously inspected system; all old sealed inputs promoted to development'))
    for o in obs:write(root/'observations'/(o['id']+'.json'),o)
    sealed=fixed_inputs();baseline=seed['previous_fixed_model']
    # Predictions only; no evaluation truth calculated before final commitment.
    old_predictions=[predict(baseline,control(a)).tolist() for a in sealed]
    write(root/'sealed_input_commit.json',dict(time_ns=time.time_ns(),actions=sealed,sha256=digest(sealed),baseline_model=baseline,baseline_predictions=old_predictions))
    for key,node in seed['nodes'].items():
        status(root,'initial_fit',model=key,calls=client.count);models[key]=fit_model(node['spec'],obs)
        nodes[key]=dict(node,status='active');seen[structural_key(node['spec'])]=key
    write(root/'initial_models.json',models)
    def context():
        viable=[k for k in models if nodes[k]['status']!='retired'] or list(models)
        best=min(viable,key=lambda k:ranking(models[k]));evidence=diagnostics(models,obs)
        for key,m in models.items():evidence+=failures_for(m,obs,key)
        for j,event in enumerate(episodes):
            for key,scores in event.get('prediction_nmse',{}).items():
                evidence.append(dict(id=f'prospective:{j}:{key}',owner_model_id=key,kind='prediction_before_observation',
                    round=j,prediction_nmse=scores,actual_conditions_met=event['actual_conditions_met'],
                    features=event['features'],boundary_test=({k:event[k] for k in ('boundary','predicted_high_error','observed_high_error','boundary_label_correct')} if key==event['boundary_owner'] else None)))
        return dict(current_best_id=best,models={k:public(m) for k,m in models.items()},statuses={k:n['status'] for k,n in nodes.items()},
            evidence=evidence,observation_count=len(obs),promotion_scope=seed['promotion_scope'])
    def cite(v,ctx,owner=None):
        if not v['evidence_ids']:raise ValueError('At least one supplied evidence ID required')
        byid={e['id']:e for e in ctx['evidence']}
        if any(e not in byid for e in v['evidence_ids']):raise ValueError('Unknown evidence ID')
        if owner:validate_evidence_ownership(dict(id=owner,evidence_ids=v['evidence_ids']),ctx['evidence'])
    def ask(name,instruction,ctx,validator):
        value,records=client.structured(name,COMMON+instruction,ctx,validator)
        write(root/'decisions'/(name+'.json'),dict(time_ns=time.time_ns(),value=value,generation_records=records));return value
    for r in range(3):
        if client.count>=15:break
        dest=root/f'round_{r}';ctx=context()
        def vp(v):
            if v['parent_id'] not in models or nodes[v['parent_id']]['status']=='retired':raise ValueError('Parent must be executable')
            cite(v,ctx,v['parent_id']);validate_boundary(v['boundary'],models)
            if v['boundary']['model_id']!=v['parent_id']:raise ValueError('Boundary must assess the parent model')
            if v['operation'] not in ('new','revise','retain'):raise ValueError('Unknown operation')
            if v['provenance']!='model_knowledge_unverified':raise ValueError('No external retrieval occurred')
            for field in ('concept','reason','observable_consequence','limitations'):
                if not isinstance(v[field],str) or not v[field]:raise ValueError('Missing '+field)
            Spec(v['spec'])
        status(root,'proposal',round=r,calls=client.count);proposal=ask(f'r{r}_proposal',PROPOSAL,ctx,vp)
        boundary=proposal['boundary'];key=f'b4_r{r}';node=dict(proposal,status='active');nodes[key]=node
        sk=structural_key(proposal['spec'])
        if sk in seen:
            nodes[key]['status']='merged_duplicate';events.append(dict(kind='duplicate',id=key,into=seen[sk]))
        else:
            try:
                status(root,'fit_proposal',round=r,calls=client.count);models[key]=fit_model(proposal['spec'],obs);seen[sk]=key
            except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError) as exc:
                nodes[key]['status']='numerical_fit_failed';events.append(dict(kind='fit_failure',id=key,error=str(exc)))
        write(dest/'models_before_experiment.json',models);ctx=context();ctx['declared_boundary']=boundary
        active={k:m for k,m in models.items() if nodes[k]['status']!='retired'}
        # A retired parent cannot silently become an experimental target.
        if boundary['model_id'] not in active:
            write(dest/'not_executed.json',dict(reason='Boundary owner retired'));continue
        ctx['active_ids']=list(active);compiled=None
        for attempt in range(2):
            def vq(q):validate_question(q,active);cite(q,ctx)
            status(root,'question',round=r,attempt=attempt,calls=client.count)
            q=ask(f'r{r}_question_{attempt}',QUESTION,ctx,vq);compiled=compile_question(q,active,obs,boundary)
            write(dest/f'design_attempt_{attempt}.json',dict(question=q,result=compiled))
            if compiled['passed']:break
            ctx['compiler_feedback']=compiled
        if not compiled['passed']:
            events.append(dict(kind='question_not_executed',round=r,reason=compiled));continue
        forecasts={};failed={}
        for k,m in active.items():
            try:forecasts[k]=[predict(m,control(a)).tolist() for a in compiled['actions']]
            except (ValueError,ArithmeticError,TypeError) as exc:failed[k]=str(exc)
        if any(k not in forecasts for k in q['target_ids']+[boundary['model_id']]):
            write(dest/'not_executed.json',dict(reason='Target final rollout failure',failures=failed));continue
        record=dict(time_ns=time.time_ns(),question=q,boundary=boundary,compiler=compiled,models=active,actions=compiled['actions'],
            observation_ids=[f'b4_r{r}_experiment_{i}' for i in range(2)],forecasts=forecasts,forecast_failures=failed)
        write(dest/'forecast_commit.json',dict(record=record,sha256=digest(record)));new=[]
        for i,a in enumerate(compiled['actions']):
            o=observe(a,record['observation_ids'][i]);o.update(time_ns=time.time_ns(),noise_std=.005,origin='new_boundary_intervention')
            write(root/'observations'/(o['id']+'.json'),o);new.append(o)
        result=dict(round=r,**evaluate(q,compiled,boundary,new,forecasts));write(dest/'outcome.json',result);episodes.append(result);obs.extend(new)
        status(root,'refit',round=r,calls=client.count);refreshed={}
        for k,m in models.items():
            if nodes[k]['status']=='retired':refreshed[k]=m;continue
            try:refreshed[k]=fit_model(m['spec'],obs,warm=m['fit'])
            except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError) as exc:
                nodes[k]['status']='numerical_fit_failed';events.append(dict(kind='refit_failure',id=k,error=str(exc)))
        models=refreshed
        if not models:raise RuntimeError('No executable models remain')
        write(dest/'updated_models.json',models);ctx=context();ctx['latest_boundary_test']=result
        def va(v):
            has_boundary=boundary.get('status')!='no_supported_boundary'
            ids=[u['id'] for u in v['updates']]
            if len(ids)!=len(set(ids)):raise ValueError('Duplicate status update')
            for u in v['updates']:
                if u['id'] not in models or u['status'] not in ('active','weakened','retired','undistinguished'):raise ValueError('Invalid status')
                cite(u,ctx,u['id'])
                if not u['reason']:raise ValueError('Explain status')
            if v['boundary_verdict'] not in ('supported_on_pair','violated_on_pair','untested'):raise ValueError('Boundary verdict enum')
            if not has_boundary and v['boundary_verdict']!='untested':raise ValueError('No boundary was asserted')
            if has_boundary and v['boundary_verdict']=='supported_on_pair' and not all(result['boundary_label_correct']):raise ValueError('Predicted boundary labels failed on this pair')
            if has_boundary and v['boundary_verdict']=='violated_on_pair' and all(result['boundary_label_correct']):raise ValueError('No wrong label on this pair')
            if has_boundary and v['boundary_verdict']=='untested':raise ValueError('This pair was executed; give a local verdict')
            for k in ('boundary_reason','next_question'):
                if not isinstance(v[k],str) or not v[k]:raise ValueError('Missing '+k)
        assessment=ask(f'r{r}_assessment','''Assess the actual pair, separating scope-label correctness from numerical model accuracy.
Each model status MUST cite its own evidence. A correct threshold label on two inputs establishes only
local descriptive support. If boundary.status=no_supported_boundary, return untested. A new model can fit a trajectory better while the parent boundary guess fails.
Return {"updates":[{"id":"model","status":"active|weakened|retired|undistinguished","evidence_ids":["id"],"reason":"Chinese"}],
"boundary_verdict":"supported_on_pair|violated_on_pair|untested","boundary_reason":"Chinese",
"next_question":"Chinese"}.''',ctx,va)
        for u in assessment['updates']:
            events.append(dict(kind='model_status',round=r,previous=nodes[u['id']]['status'],**u));nodes[u['id']]['status']=u['status']
    ctx=context()
    def vf(v):
        if v['selected_id'] is not None and (v['selected_id'] not in models or nodes[v['selected_id']]['status']=='retired'):raise ValueError('Select executable non-retired model or null')
        for field in ('reason','scope_learned','unresolved'):
            if not isinstance(v[field],str) or not v[field]:raise ValueError('Missing '+field)
    final=ask('final','''Choose final model or null. Return Chinese conclusions about actually tested scope claims,
not latent physical discovery. {"selected_id":"id or null","reason":"...","scope_learned":"...","unresolved":"..."}''',ctx,vf)
    selected=models.get(final['selected_id']);old_refit=models.get('v3_r1')
    # Explicit final-data refit reference even if Luna retired the old formula earlier.
    if old_refit is None or nodes['v3_r1']['status']=='retired':old_refit=fit_model(baseline['spec'],obs,warm=baseline['fit'])
    refs={'old_frozen':baseline,'old_formula_refit':old_refit}
    if selected:refs['selected']=selected
    predicted={};prediction_errors={}
    for k,m in refs.items():
        predicted[k]=[]
        for i,a in enumerate(sealed):
            try:predicted[k].append(predict(m,control(a)).tolist())
            except (ValueError,ArithmeticError,TypeError) as exc:
                predicted[k].append(None);prediction_errors[f'{k}:{i}']=str(exc)
    record=dict(time_ns=time.time_ns(),decision=final,models=refs,predictions=predicted,prediction_errors=prediction_errors)
    write(root/'final_commit.json',dict(record=record,sha256=digest(record)));checks=[]
    for i,a in enumerate(sealed):
        y=truth(a);scores={k:nmse(np.array(v[i]),y) if v[i] is not None else None for k,v in predicted.items()}
        checks.append(dict(id=i,action=a,truth=y.tolist(),nmse=scores))
    write(root/'sealed_result.json',dict(time_ns=time.time_ns(),checks=checks,scope='new inputs on same development system'))
    write(root/'concept_graph.json',dict(nodes=nodes,events=events,episodes=episodes,final=final))
    from audit import audit
    result=audit(root);write(root/'AUDIT.json',result)
    if not result['passed']:raise RuntimeError('Audit failed')
    status(root,'completed',calls=client.count,pairs=len(episodes),selected=final['selected_id'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--seed',required=True);args=p.parse_args()
    root=Path(args.out);root.mkdir(parents=True,exist_ok=False);secret=getpass.getpass('API key (hidden): ');client=Luna(secret,root)
    try:run(root,client,Path(args.seed))
    except Exception as exc:
        status(root,'failed',calls=client.count,error_type=type(exc).__name__,error=str(exc).replace(secret,'[redacted]'))
        raise SystemExit(1) from None
