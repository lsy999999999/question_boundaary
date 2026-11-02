import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,getpass,json,time,hashlib,sys
from pathlib import Path
import numpy as np
import scipy
from engine import write,digest,Spec,control,nmse
from numerics import structural_key,predict,public
from parallel_fit import Fitter
from ledger import local_facts,retention,metrics,prospective_metrics,check_citations,choose,fit_id
from scope import label,parse
from design import action,pair,validate,compile_question
from prompts import COMMON,PROPOSAL,RETENTION,QUESTION,ASSESS
from transport import Luna,MODEL
from world import observe,truth


def status(root,stage,**extra):
    d=dict(stage=stage,time_ns=time.time_ns(),pid=os.getpid(),**extra);p=root/'LIVE_STATUS.tmp';p.write_text(json.dumps(d));p.replace(root/'LIVE_STATUS.json');print(json.dumps(d),flush=True)


def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def sealed_inputs():
    rng=np.random.default_rng(2026110105);out=[]
    for family in ('recovery_gap','reversal_depth','dwell_time','polarity'):
        limits={'recovery_gap':(.1,2.9),'reversal_depth':(.2,1.4),'dwell_time':(1.1,3.9),'polarity':(1.1,4.9)}
        out.append(action(family,float(rng.uniform(.35,1.4)),int(rng.choice([-1,1])),float(round(rng.uniform(*limits[family]),1))))
    for _ in range(4):out.append(dict(points=[[0.,0.]]+[[t,float(v)] for t,v in zip((.6,2.3,4.8,7.3,9.9),rng.uniform(-1.4,1.4,5))]))
    return out


def run(root,client,seedfile,fitter):
    seed=json.loads(seedfile.read_text());obs=seed['observations'];models={};nodes={};withdrawn=set();events=[];episodes=[];prospective=[]
    facts=local_facts(obs)
    write(root/'manifest.json',dict(version='concept_evidence_v5',time_ns=time.time_ns(),model=MODEL,workers=8,rounds=2,
        source_hashes={p.name:filehash(p) for p in sorted(Path(__file__).parent.glob('*.py'))},seed_sha256=filehash(seedfile),
        plan_sha256=filehash(Path(__file__).parent/'PLAN.md'),python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
        call_cap=20,completion_cap=2048,fit_starts=2,fit_max_nfev=35,scope='Same inspected system, former sealed data promoted to development'))
    for o in obs:write(root/'observations'/(o['id']+'.json'),o)
    write(root/'preserved_facts.json',dict(relations=facts,historical_refutation=seed['legacy']))
    sealed=sealed_inputs();old=seed['old_frozen_model'];oldpred=[];baseline_errors={}
    for i,a in enumerate(sealed):
        try:oldpred.append(predict(old,control(a)).tolist())
        except (ValueError,ArithmeticError,TypeError) as exc:oldpred.append(None);baseline_errors[str(i)]=str(exc)
    write(root/'sealed_input_commit.json',dict(time_ns=time.time_ns(),actions=sealed,sha256=digest(sealed),baseline=old,baseline_predictions=oldpred,baseline_prediction_errors=baseline_errors))
    def fit(specs,warms,phase):
        last=[0.]
        def progress(done,total):
            if done==total or time.monotonic()-last[0]>10:
                status(root,phase,calls=client.count,fit_jobs_done=done,fit_jobs_total=total);last[0]=time.monotonic()
        values,failed=fitter.fit(specs,obs,warms,progress)
        for m in values.values():m['training_data_hash']=digest(obs)
        return values,failed
    status(root,'initial_fits',calls=0)
    models,failed=fit({k:n['spec'] for k,n in seed['nodes'].items()},{k:n['previous_fit'] for k,n in seed['nodes'].items()},'initial_fits')
    for k,n in seed['nodes'].items():nodes[k]=dict(n,status='active' if k in models else 'fit_failed')
    events.extend(dict(kind='initial_fit_failed',model=k,error=v) for k,v in failed.items())
    if not models:raise RuntimeError('No executable starting model')
    write(root/'initial_models.json',models)
    def context():
        records,windows=metrics(models,obs)
        return dict(models={k:public(m) for k,m in models.items()},statuses={k:n['status'] for k,n in nodes.items()},
            metrics=records+prospective,largest_error_windows=windows,facts=facts,historical_refutation=seed['legacy'],
            preserved_relation_checks={k:retention(m,facts) for k,m in models.items()},
            observation_controls={o['id']:dict(action=o['action'],noise_std=o['noise_std'],origin=o['origin']) for o in obs},
            promotion_scope=seed['promotion_scope'])
    def ask(name,instruction,ctx,validator):
        value,wires=client.structured(name,COMMON+instruction,ctx,validator)
        write(root/'decisions'/(name+'.json'),dict(time_ns=time.time_ns(),value=value,generation_records=wires));return value
    for r in range(2):
        if client.count>=15:break
        dest=root/f'round_{r}';ctx=context();active={k:m for k,m in models.items() if k not in withdrawn and nodes[k]['status']!='retired'}
        if not active:events.append(dict(kind='no_active_candidate',round=r));break
        ctx['active_ids']=list(active)
        def vp(v):
            if v['parent_id'] not in active:raise ValueError('Executable parent required')
            check_citations(v['evidence_ids'],ctx)
            if v['operation'] not in ('new','revise','retain') or v['provenance']!='model_knowledge_unverified':raise ValueError('Invalid operation/provenance')
            Spec(v['spec']);b=v['boundary']
            if b['model_id']!=v['parent_id'] or b['status'] not in ('proposed','abstain'):raise ValueError('Boundary must refer to current parent')
            if b['status']=='proposed':
                parse(b['expression'])
                for o in obs:label(b,o['u'])
            elif b['expression']!='':raise ValueError('Abstention has empty expression')
        status(root,'proposal',round=r,calls=client.count);proposal=ask(f'r{r}_proposal',PROPOSAL,ctx,vp)
        boundary=proposal['boundary'];key=f'e5_r{r}';nodes[key]=dict(proposal,status='active')
        equivalent=next((k for k,m in models.items() if structural_key(m['spec'])==structural_key(proposal['spec'])),None)
        if equivalent:
            nodes[key]['status']='merged_duplicate';events.append(dict(kind='exact_duplicate',id=key,into=equivalent));key=equivalent
        else:
            added,errors=fit({key:proposal['spec']},{},f'round_{r}_fit_proposal')
            if errors:
                nodes[key]['status']='fit_failed';events.append(dict(kind='proposal_fit_failed',id=key,error=errors[key]))
            models.update(added)
        if key in models:
            checks=retention(models[key],facts);ctx=context();ctx.update(proposal_id=key,proposal_relation_checks=checks)
            def vr(v):
                if v['model_id']!=key or v['disposition'] not in ('keep_for_test','withdraw'):raise ValueError('Unknown retention decision')
                expected={x['relation_id']:x for x in checks};rows=v['relations']
                if len(rows)!=len(expected) or {x['relation_id'] for x in rows}!=set(expected):raise ValueError('Acknowledge every local relation exactly once')
                for row in rows:
                    e=expected[row['relation_id']];required={'compatible':'retain_local_fact','conflict':'acknowledge_conflict','unavailable':'unavailable'}[e['status']]
                    if row['computed_status']!=e['status'] or row['response']!=required:raise ValueError('Preserve computed relationship result, not a rewritten observation')
            review=ask(f'r{r}_retention',RETENTION,ctx,vr);write(dest/'retention.json',dict(checks=checks,review=review))
            if review['disposition']=='withdraw':withdrawn.add(key);nodes[key]['status']='withdrawn'
            else:withdrawn.discard(key);nodes[key]['status']='active'
        active={k:m for k,m in models.items() if k not in withdrawn and nodes[k]['status']!='retired'}
        if boundary['model_id'] not in active:
            events.append(dict(kind='boundary_owner_unavailable',round=r));continue
        write(dest/'models_before_experiment.json',models);ctx=context();ctx.update(active_ids=list(active),declared_boundary=boundary)
        compiled=None
        for attempt in range(2):
            def vq(q):validate(q,set(active),boundary);check_citations(q['evidence_ids'],ctx)
            question=ask(f'r{r}_question_{attempt}',QUESTION,ctx,vq);compiled=compile_question(question,active,obs,boundary)
            write(dest/f'design_attempt_{attempt}.json',dict(question=question,result=compiled))
            if compiled['passed']:break
            ctx['compiler_feedback']=compiled
        if not compiled['passed']:events.append(dict(kind='design_not_executed',round=r,result=compiled));continue
        forecasts={};failures={}
        for k,m in active.items():
            try:forecasts[k]=[predict(m,control(a)).tolist() for a in compiled['actions']]
            except (ValueError,ArithmeticError,TypeError) as exc:failures[k]=str(exc)
        if any(k not in forecasts for k in question['target_ids']+[boundary['model_id']]):
            events.append(dict(kind='target_forecast_failed',round=r,failures=failures));continue
        rec=dict(time_ns=time.time_ns(),question=question,boundary=boundary,models=active,compiler=compiled,actions=compiled['actions'],
            forecasts=forecasts,failed_forecasts=failures,observation_ids=[f'e5_r{r}_experiment_{i}' for i in range(2)])
        write(dest/'forecast_commit.json',dict(record=rec,sha256=digest(rec)));new=[]
        for i,a in enumerate(rec['actions']):
            o=observe(a,rec['observation_ids'][i]);o.update(time_ns=time.time_ns(),noise_std=.005,origin='new_v5_intervention');write(root/'observations'/(o['id']+'.json'),o);new.append(o)
        met=prospective_metrics(rec,new);prospective.extend(met);owner=boundary['model_id'];owned=[m for m in met if m['owner_model_id']==owner]
        labels=[label(boundary,o['u']) for o in new];actual=[m['high_error'] for m in owned]
        verdict='untested' if boundary['status']=='abstain' else ('supported_on_pair' if labels==actual else 'violated_on_pair')
        conditions=all(np.array_equal(control(a),np.array(o['u'])) for a,o in zip(pair(compiled['descriptor']),new))
        outcome=dict(round=r,actual_conditions_met=conditions,metrics=met,boundary=boundary,boundary_fit_version=fit_id(active[owner]['spec'],active[owner]['fit']),
            predicted_high_error=labels,observed_high_error=actual,boundary_verdict=verdict,boundary_metric_ids=[m['id'] for m in owned])
        if question['family']=='polarity':outcome['observed_mirror_rms']=float(np.sqrt(np.mean((np.array(new[0]['x'])+new[1]['x'])**2)))
        write(dest/'outcome.json',outcome);episodes.append(outcome);obs.extend(new)
        fitset={k:m for k,m in models.items() if k not in withdrawn and nodes[k]['status']!='retired'}
        fresh,errors=fit({k:m['spec'] for k,m in fitset.items()},{k:m['fit'] for k,m in fitset.items()},f'round_{r}_refit')
        for k,error in errors.items():models.pop(k,None);nodes[k]['status']='fit_failed';events.append(dict(kind='refit_failure',id=k,error=error))
        models.update(fresh);write(dest/'updated_models.json',models);ctx=context();ctx['actual_outcome']=outcome
        def va(v):
            if v['boundary_verdict']!=verdict:raise ValueError('Boundary verdict must use committed prospective labels')
            wanted=[] if verdict=='untested' else outcome['boundary_metric_ids']
            if sorted(v['boundary_metric_ids'])!=sorted(wanted):raise ValueError('Cite the original prospective boundary metrics, not refitted CV')
            seen=set()
            if not v['updates']:raise ValueError('At least one update')
            for u in v['updates']:
                if u['id'] not in models or u['id'] in seen or u['status'] not in ('active','weakened','retired'):raise ValueError('Invalid model update')
                seen.add(u['id']);check_citations(u['evidence_ids'],ctx,u['id'])
        assessment=ask(f'r{r}_assessment',ASSESS,ctx,va)
        for u in assessment['updates']:nodes[u['id']]['status']=u['status'];events.append(dict(kind='assessment',round=r,**u))
    # Ensure the old formula reference is fitted to exactly the same final development observations.
    if 'v3_r1' not in models or models['v3_r1'].get('training_data_hash')!=digest(obs):
        fresh,errors=fit({'v3_r1':seed['nodes']['v3_r1']['spec']},{},'final_reference_fit')
        if errors:raise RuntimeError('Old-formula numerical reference failed')
        models.update(fresh)
    blocked=withdrawn|{k for k,n in nodes.items() if n['status']=='retired'}
    final=choose(models,blocked,facts);selected=models.get(final['selected_id']);refs=dict(old_frozen=old,old_formula_refit=models['v3_r1'])
    if selected:refs['selected']=selected
    ys={};errors={}
    for key,m in refs.items():
        ys[key]=[]
        for i,a in enumerate(sealed):
            try:ys[key].append(predict(m,control(a)).tolist())
            except (ValueError,ArithmeticError,TypeError) as exc:ys[key].append(None);errors[f'{key}:{i}']=str(exc)
    record=dict(time_ns=time.time_ns(),decision=final,models=refs,predictions=ys,prediction_errors=errors)
    write(root/'final_models.json',models);write(root/'final_commit.json',dict(record=record,sha256=digest(record)))
    result=[]
    for i,a in enumerate(sealed):
        x=truth(a);result.append(dict(id=i,action=a,truth=x.tolist(),nmse={k:nmse(np.array(v[i]),x) if v[i] is not None else None for k,v in ys.items()}))
    write(root/'sealed_result.json',dict(time_ns=time.time_ns(),checks=result,scope='new inputs, same inspected system'))
    write(root/'concept_graph.json',dict(nodes=nodes,withdrawn=sorted(blocked),events=events,episodes=episodes,final=final))
    from audit import audit
    checked=audit(root);write(root/'AUDIT.json',checked)
    if not checked['passed']:raise RuntimeError('Execution audit failed')
    status(root,'completed',calls=client.count,pairs=len(episodes),selected=final['selected_id'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--seed',required=True);a=p.parse_args()
    root=Path(a.out);root.mkdir(parents=True,exist_ok=False);secret=getpass.getpass('API key (hidden): ');client=Luna(secret,root);fitter=Fitter(8)
    try:run(root,client,Path(a.seed),fitter)
    except Exception as exc:
        status(root,'failed',calls=client.count,error_type=type(exc).__name__,error=str(exc).replace(secret,'[redacted]'));raise SystemExit(1) from None
    finally:fitter.close()
