import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse,getpass,hashlib,json,sys,time
from pathlib import Path
import numpy as np
import scipy
from engine import Spec,write,digest,GRID,control,nmse
from numerics import fit_model,structural_key,affine_signature,ranking,public,failures_for,predict
from experiments import relation_reports,validate_question,compile_question,evaluate_observed
from transport import Luna,MODEL
from world import observe,truth

COMMON='''You are gpt-6-luna participating in a bounded scientific-discovery development run.
Use only supplied public observations. You cannot see the simulator equations or new sealed inputs.
The old data were already analyzed: this is a development continuation, not untouched confirmation.
Do not infer physical meaning merely from latent-variable names. Different affine state coordinates
may describe exactly the same input/output behavior. Reuse, merge, revise a relation, or introduce a
state as evidence warrants. Follow current-model held-out prediction failures, not obsolete x/u-only
collisions. Structural properties are local observations, not established universal laws.
All scientific decisions must cite supplied evidence identifiers. No invented sources or observations.
Return a JSON object. Tool fitting uses complete trajectories, two initializations, and holds out all
copies of an input schedule together. It may fail; distinguish bad numerical fits from bad concepts.
Mathematical schema: dx/dt is a fitted linear combination of 1..8 expression terms. You may use
0..2 states z0,z1 initialized at zero, with rates you specify, and 0..3 positive parameters p0,p1,p2.
Parameters require .02<=lower<initial<upper<=4; term coefficients fitted in [-8,8].
Expressions: x,u,t, declared z/p names, constants |c|<=10, + - * /, powers **2/**3,
unary tanh/sin/cos/abs. No arbitrary code. Euler integration dt=.1, horizon12, x initial0.
Input magnitude at most1.5; measured noise std=.005. All trials reset the system.
'''
PROPOSAL='''Propose one executable hypothesis addressing a current prediction failure or observed
structural property. You need not add a new latent variable. A nonlinear relation, removal of a
spurious intercept, or retention of an adequate existing model can be appropriate; choose from evidence.
Return {"parent_id":"existing id","evidence_ids":["provided id"],"concept":"...",
"reason":"...","operation":"revise|new|retain","spec":{"parameters":[{"name":"p0",
"lower":0.05,"initial":0.5,"upper":3.0}],"states":[{"name":"z0","meaning":"...",
"rate":"expression"}],"terms":["expression"]},"observable_consequence":"...",
"analogy":{"domain":"...","relation":"...","mapping":"...","failure_condition":"..."},
"provenance":"model_knowledge_unverified","limitations":"..."}.
Empty parameter/state arrays allowed. The schema contains no proposed scientific formula.
'''
QUESTION='''Choose a scientific QUESTION for the numerical experiment compiler, not a guessed waveform.
Available kinds: polarity (u vs -u), scaling (u vs scale*u), matched_history (different histories,
same u=0 from t=7, compare x at t=8 and next .5s slopes). For polarity/scaling the tool searches
amplitude/duration within your ranges. For matched_history it searches 96 bounded four-segment pairs.
purpose probe_relation is allowed for polarity/scaling even when all models agree: explicitly test
a shared structural assumption outside already observed numeric inputs. purpose discriminate needs
two distinct active models and adequate predicted separation. Matched history requires all guard
models to predict state gap <= half the requested tolerance, leaving a margin, plus slope separation.
A failed search is not proof of impossibility. If the compiler returns failure, revise your question.
Return {"kind":"polarity|scaling|matched_history","purpose":"probe_relation|discriminate",
"target_ids":["active id"],"evidence_ids":["provided id"],"rationale":"...","claim":"...",
"update_if_violated":"...","amplitude_range":[0.2,1.2],"duration_range":[1.0,4.0],
"scale":1.5,"tolerance_x":0.04}. Amplitudes .1..1.5, durations1..5, scale1.2..2,
tolerance .01..04. Even irrelevant fields must be present. For scaling both inputs must stay <=1.5.
'''


def status(root,stage,**extra):
    value=dict(stage=stage,time_ns=time.time_ns(),pid=os.getpid(),**extra)
    p=root/'LIVE_STATUS.tmp';p.write_text(json.dumps(value));p.replace(root/'LIVE_STATUS.json')
    print(json.dumps(value),flush=True)


def source_hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))}


def run(root,luna,seedfile):
    seed=json.loads(seedfile.read_text());obs=seed['observations'];nodes={};models={};aliases={};seen={};events=[]
    write(root/'manifest.json',dict(version='concept_discovery_v3',time_ns=time.time_ns(),model=MODEL,
        seed_file_sha256=hashlib.sha256(seedfile.read_bytes()).hexdigest(),source_hashes=source_hashes(),
        python=sys.version,numpy=np.__version__,scipy=scipy.__version__,round_limit=3,call_limit=20,
        max_completion_tokens=2048,fit_nfev=35,fit_starts=2,
        scope='Development continuation on an already inspected system; new inputs are not a new system'))
    for o in obs: write(root/'observations'/(o['id']+'.json'),o)
    # Sealed controls fixed before any model calls; never included in prompts.
    rng=np.random.default_rng(20261101)
    sealed=[dict(points=[[0,0]]+[[t,float(v)] for t,v in zip((.5,2.5,5,7.5,10),rng.uniform(-1.4,1.4,5))]) for _ in range(6)]
    write(root/'sealed_input_commit.json',dict(time_ns=time.time_ns(),actions=sealed,sha256=digest(sealed)))
    for identifier,node in seed['nodes'].items():
        nodes[identifier]=dict(node,status='active',origin='previous recorded Luna proposal' if identifier!='initial' else 'initial baseline')
        key=structural_key(node['spec'])
        if key in seen:
            aliases[identifier]=seen[key];nodes[identifier]['status']='merged_duplicate'
            events.append(dict(kind='exact_structure_merge',id=identifier,into=seen[key]));continue
        seen[key]=identifier;status(root,'initial_trajectory_fit',hypothesis=identifier)
        models[identifier]=fit_model(node['spec'],obs)
    write(root/'initial_models.json',models)
    # Historical guards are engineering replays, not new experiments/model proposals.
    write(root/'historical_gate_replay.json',seed['historical_guard_cases'])
    episode=[]
    def context():
        viable=[k for k in models if nodes[k]['status']!='retired'] or list(models)
        best=min(viable,key=lambda k:ranking(models[k]));evidence=failures_for(models[best],obs)+relation_reports(obs)
        for i,event in enumerate(episode):
            evidence.append(dict(id=f'outcome_{i}',kind='prospective_intervention',record=event))
        return dict(current_best_id=best,models={k:public(m) for k,m in models.items()},
            concept_status={k:dict(status=v['status'],concept=v.get('concept','')) for k,v in nodes.items()},
            aliases=aliases,evidence=evidence,observations_count=len(obs)),{e['id'] for e in evidence}
    def ask(name,instruction,payload,validator):
        value,records=luna.structured(name,COMMON+instruction,payload,validator)
        write(root/'decisions'/(name+'.json'),dict(value=value,generation_records=records))
        return value
    for round_no in range(3):
        if luna.count>=15: break
        dest=root/f'round_{round_no}';ctx,eids=context()
        def vp(v):
            if v['parent_id'] not in nodes: raise ValueError('Unknown parent')
            if not v['evidence_ids'] or any(e not in eids for e in v['evidence_ids']): raise ValueError('Cite actual evidence identifiers')
            if v['operation'] not in ('new','revise','retain'): raise ValueError('Unknown operation')
            for k in ('concept','reason','observable_consequence','limitations'):
                if not isinstance(v[k],str) or not v[k]: raise ValueError('Missing '+k)
            if v['provenance']!='model_knowledge_unverified': raise ValueError('No external literature retrieved')
            Spec(v['spec'])
        status(root,'propose_from_current_failure',round=round_no,calls=luna.count)
        proposal=ask(f'r{round_no}_proposal',PROPOSAL,ctx,vp)
        identifier=f'v3_r{round_no}';nodes[identifier]=dict(proposal,status='active')
        key=structural_key(proposal['spec'])
        if key in seen:
            aliases[identifier]=seen[key];nodes[identifier]['status']='merged_duplicate'
            events.append(dict(kind='exact_structure_merge',id=identifier,into=seen[key],round=round_no))
        else:
            status(root,'fit_proposed_trajectory_model',round=round_no,calls=luna.count)
            try:
                models[identifier]=fit_model(proposal['spec'],obs);seen[key]=identifier
            except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError) as exc:
                nodes[identifier]['status']='numerical_fit_failed'
                events.append(dict(kind='fit_failure',id=identifier,error=str(exc),round=round_no))
        signatures={k:affine_signature(m) for k,m in models.items()}
        signature_seen={}
        for key,sig in signatures.items():
            if sig is None: continue
            encoded=json.dumps(sig,sort_keys=True)
            if encoded in signature_seen:
                parent=signature_seen[encoded];aliases[key]=parent;nodes[key]['status']='merged_affine_equivalent'
                events.append(dict(kind='exact_stored_decimal_affine_equivalence',id=key,into=parent))
            else: signature_seen[encoded]=key
        models={k:m for k,m in models.items() if k not in aliases}
        write(dest/'affine_signatures.json',signatures)
        write(dest/'models_before_experiment.json',models)
        active={k:m for k,m in models.items() if nodes[k]['status']!='retired'}
        if not active:
            write(dest/'no_active_hypothesis.json',dict(reason='Agent retired every executable hypothesis'));continue
        ctx,eids=context();ctx['active_ids']=list(active);compiled=None
        for attempt in range(2):
            def vq(v):
                validate_question(v,set(active))
                if not v['evidence_ids'] or any(e not in eids for e in v['evidence_ids']): raise ValueError('Question needs actual evidence')
            status(root,'compile_experiment_question',round=round_no,attempt=attempt,calls=luna.count)
            question=ask(f'r{round_no}_question_{attempt}',QUESTION,ctx,vq)
            compiled=compile_question(question,active,obs,20261101+round_no*11+attempt)
            write(dest/f'design_attempt_{attempt}.json',dict(question=question,result=compiled))
            if compiled['passed']: break
            ctx['compiler_feedback']=compiled
        if not compiled['passed']:
            episode.append(dict(round=round_no,kind='design_not_executed',reason=compiled));continue
        actions=compiled['actions'];forecasts={};failed={}
        for key,m in active.items():
            try: forecasts[key]=[predict(m,control(a)).tolist() for a in actions]
            except (ValueError,ArithmeticError,TypeError) as exc: failed[key]=str(exc)
        if any(k not in forecasts for k in question['target_ids']):
            write(dest/'not_executed.json',dict(reason='Target model failed final forecast',failures=failed));continue
        record=dict(time_ns=time.time_ns(),question=question,actions=actions,models=active,forecasts=forecasts,
                    failed_forecasts=failed,compiler=compiled)
        write(dest/'forecast_commit.json',dict(record=record,sha256=digest(record)))
        new=[]
        for i,a in enumerate(actions):
            o=observe(a,f'v3_r{round_no}_experiment_{i}');o['time_ns']=time.time_ns()
            write(root/'observations'/(o['id']+'.json'),o);new.append(o)
        outcome=dict(id=f'outcome_{len(episode)}',round=round_no,question=question,
                     **evaluate_observed(question,new,forecasts))
        write(dest/'outcome.json',outcome);episode.append(outcome);obs.extend(new)
        status(root,'refit_after_actual_observation',round=round_no,calls=luna.count)
        refreshed={}
        for key,m in models.items():
            if nodes[key]['status']=='retired': refreshed[key]=m;continue
            try: refreshed[key]=fit_model(m['spec'],obs,warm=m['fit'])
            except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError) as exc:
                nodes[key]['status']='numerical_fit_failed';events.append(dict(kind='refit_failure',id=key,error=str(exc)))
        models=refreshed
        if not models: raise RuntimeError('No executable model remains')
        write(dest/'updated_models.json',models)
        ctx,eids=context()
        def vr(v):
            if not isinstance(v['updates'],list): raise ValueError('Need explicit updates')
            for u in v['updates']:
                if u['id'] not in models or u['status'] not in ('active','weakened','retired','undistinguished'): raise ValueError('Invalid hypothesis status')
                if not u['evidence_ids'] or any(e not in eids for e in u['evidence_ids']): raise ValueError('Status change needs evidence')
                if not isinstance(u['reason'],str) or not u['reason']: raise ValueError('Explain status change')
            if not isinstance(v['next_question'],str): raise ValueError('Explain next question')
        assessment=ask(f'r{round_no}_assessment','''Review actual intervention outcomes and current prediction failures.
Change concept status only with explicit evidence. Failed matching alone does not refute a model;
full-trajectory errors or other actually measured properties may still be informative. An observed
relation on one input range is not a universal law. Numerical failure is not proof of a wrong concept.
Return {"updates":[{"id":"existing model","status":"active|weakened|retired|undistinguished",
"evidence_ids":["actual id"],"reason":"..."}],"next_question":"..."}.''',ctx,vr)
        for u in assessment['updates']:
            events.append(dict(kind='Luna_evidence_assessment',round=round_no,previous_status=nodes[u['id']]['status'],**u))
            nodes[u['id']]['status']=u['status']
    ctx,eids=context()
    def vf(v):
        if v['selected_id'] is not None and (v['selected_id'] not in models or nodes[v['selected_id']]['status']=='retired'): raise ValueError('Final model must be an executable non-retired hypothesis')
        for k in ('reason','what_changed','unresolved'):
            if not isinstance(v[k],str) or not v[k]: raise ValueError('Missing final explanation')
    final=ask('final','''Return a Chinese summary of the actual evidence changes. Select an executable
model, or null if none is defensible. Do not call a latent coordinate a discovered physical entity.
{"selected_id":"id or null","reason":"...","what_changed":"...","unresolved":"..."}''',ctx,vf)
    selected=models[final['selected_id']] if final['selected_id'] else None
    record=dict(time_ns=time.time_ns(),decision=final,model=selected)
    write(root/'final_commit.json',dict(record=record,sha256=digest(record)))
    checks=[]
    if selected:
        for i,a in enumerate(sealed):
            try:
                y=predict(selected,control(a));actual=truth(a)
                checks.append(dict(id=i,action=a,prediction=y.tolist(),truth=actual.tolist(),nmse=nmse(y,actual)))
            except (ValueError,ArithmeticError,TypeError) as exc: checks.append(dict(id=i,error=str(exc)))
    write(root/'sealed_result.json',dict(time_ns=time.time_ns(),checks=checks,development_only=True))
    write(root/'concept_graph.json',dict(nodes=nodes,aliases=aliases,events=events,episodes=episode,final=final))
    from audit import audit
    checked=audit(root);write(root/'AUDIT.json',checked)
    if not checked['passed']: raise RuntimeError('Record audit failed')
    status(root,'completed',calls=luna.count,executed_pairs=sum('prediction_nmse' in e for e in episode),selected=final['selected_id'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--seed',required=True);a=p.parse_args()
    root=Path(a.out);root.mkdir(parents=True,exist_ok=False)
    key=getpass.getpass('API key (hidden): ');luna=Luna(key,root)
    try: run(root,luna,Path(a.seed))
    except Exception as exc:
        status(root,'failed',calls=luna.count,error_type=type(exc).__name__,error=str(exc).replace(key,'[redacted]'))
        raise SystemExit(1) from None
