"""Counterexample-indexed hypothesis branches; all scientific language from Luna."""
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
import argparse
import getpass
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from engine import (Spec, GRID, write, digest, fit_model, predict, nmse,
                    collisions, summary, validate_action, control)
from transport import Luna, MODEL, ENDPOINT
from world import INITIAL, SEALED, observe, truth

BASE = dict(parameters=[], states=[], terms=['1', 'x', 'u'])
COMMON = '''You are a scientific discovery agent. Only the supplied observations are evidence.
The hidden simulator, its equation and independent future tests are inaccessible to you.
Your task is to construct an executable explanation, not select a named template.
Return one JSON object only. Do not invent observations, citations, executed tests, or proof.
Analogies are hypotheses from your parametric knowledge, not retrieved literature.
You may introduce latent variables, but they must have operational dynamics and a testable consequence.
The experiment resets x and all hypothesized latent states to zero at t=0. Input u is held constant
between specified changes, horizon 12 seconds, sample dt=.1. Observation noise std=.005.
Numerics fit only models you submit. No prewritten library of hidden mechanisms is searched.
The derivative dx/dt is a fitted linear combination of your terms (weights may be negative).
Your additional positive parameters p0,p1,p2 are fitted; coefficients for terms are separate.
Expressions allow x,u,t,z0,z1, declared parameters, numeric constants |c|<=10, + - * /,
literal powers **2/**3, and unary tanh/sin/cos/abs. No other calls or code.
Zero to two states, zero to three parameters, one to eight terms. State update is Euler:
z_next=z+.1*rate. Every latent starts at zero. Each parameter requires .02<=lower<initial<upper<=4.
Parameter names p0,p1,p2 and state names z0,z1 must be sequential. Keep dynamics stable.
An approximate current-state collision is a clue; noise, input timing and imperfect matching also matter.
Models are compared on complete left-out observed trajectories, not random samples.
'''
PROPOSE = '''Construct ONE hypothesis addressing the supplied unresolved evidence. Prefer a small,
interpretable extension or a defensible competing explanation. You may reuse, edit or reject a
parent concept, and invent formulas within the expression language. Do not add states merely to
sound novel. Explain exactly what your new variable distinguishes that x,u alone cannot.
Schema:
{"parent_id":"existing id", "target_witnesses":["provided witness id"],
 "concept":"short concept name", "explanation":"evidence-based account",
 "analogy":{"domain":"source field","relation":"source mechanism",
 "mapping":"explicit source-to-target variable/relationship map",
 "breaks_when":"a condition where this analogy should fail",
 "provenance":"model_knowledge_unverified"},
 "spec":{"parameters":[{"name":"p0","lower":0.05,"initial":0.8,"upper":3.0}],
 "states":[{"name":"z0","meaning":"operational meaning","rate":"expression"}],
 "terms":["expression"]},
 "distinguishing_prediction":"how an intervention separates this from a competitor",
 "falsifier":"observable failure condition", "limitations":"remaining ambiguity"}
Arrays for parameters/states/target_witnesses can be empty. Schema values are placeholders, not a suggested mechanism.
'''
DESIGN = '''Design TWO executable input trajectories that most directly distinguish the competing
explanations or test a proposed failure condition. You can aim to produce similar x and u after
different histories, then compare future changes. Such matching is NOT guaranteed by your text;
the actual pair and forecasts will be saved before measurement. No adaptive stopping/reset mid-trial.
Use piecewise-constant inputs: 2..7 ordered [time,value] points; first time 0; times 0..11 on .1 grid;
changes at least .5 seconds apart; values -1.5..1.5. Values are held until next point, then to t=12.
Schema: {"rationale":"...", "hypotheses":["existing id","existing id"],
"claim_under_test":"...", "expected_separation":"...", "comparison_time":8.0,
"matching_tolerance_x":0.04, "actions":[{"points":[[0,0],[1,1],[3,0]]},
{"points":[[0,0],[1,-1],[3,0]]}], "failure_of_design":"..."}.
comparison_time in [0,11.5]. It identifies where actual x,u and next .5s slopes will be compared.
Your example input is not prescribed: choose values from scientific reasoning about the supplied models.
'''


def status(root, stage, **extra):
    value = dict(stage=stage, time_ns=time.time_ns(), pid=os.getpid(), **extra)
    tmp = root / 'LIVE_STATUS.tmp'
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    tmp.replace(root / 'LIVE_STATUS.json')
    print(json.dumps(value, ensure_ascii=False), flush=True)


def public_model(identifier, m, node):
    return dict(id=identifier, model=m, origin=node)


def hypothesis_validator(value, ids, witnesses):
    if value['parent_id'] not in ids:
        raise ValueError('Unknown parent id')
    if not isinstance(value['target_witnesses'], list) or any(v not in witnesses for v in value['target_witnesses']):
        raise ValueError('Unknown target witness')
    for key in ('concept','explanation','distinguishing_prediction','falsifier','limitations'):
        if not isinstance(value[key], str) or not value[key]:
            raise ValueError('Missing explanation: '+key)
    for key in ('domain','relation','mapping','breaks_when','provenance'):
        if not isinstance(value['analogy'][key], str) or not value['analogy'][key]:
            raise ValueError('Incomplete analogy')
    if value['analogy']['provenance'] != 'model_knowledge_unverified':
        raise ValueError('No external source retrieval has occurred')
    Spec(value['spec'])


def design_validator(value, ids):
    if not isinstance(value['actions'], list) or len(value['actions']) != 2:
        raise ValueError('Exactly two experiments required')
    for a in value['actions']:
        validate_action(a)
    if not isinstance(value['hypotheses'],list) or len(set(value['hypotheses'])) < 2 or any(v not in ids for v in value['hypotheses']):
        raise ValueError('Select at least two existing competing hypotheses')
    if not 0 <= value['comparison_time'] <= 11.5 or not .001 <= value['matching_tolerance_x'] <= .1:
        raise ValueError('Comparison time/tolerance out of bounds')
    for key in ('rationale','claim_under_test','expected_separation','failure_of_design'):
        if not isinstance(value[key],str) or not value[key]:
            raise ValueError('Missing design rationale')


def source_hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.glob('*.py'))}


def run(root, luna):
    started = time.time_ns()
    write(root / 'manifest.json', dict(version='concept_discovery_v1', start_ns=started,
        model=MODEL, endpoint=ENDPOINT, source_hashes=source_hashes(), python=sys.version,
        numpy=np.__version__, scipy=scipy.__version__, rounds=3, max_calls=20,
        max_completion_tokens=2048, state_limit=2, parameter_limit=3, term_limit=8,
        initial_observations=3, new_observations=6, sealed_observations=6,
        scope='One exploratory trajectory, no agent-count ablation or novelty claim'))
    obs = []
    for i, action in enumerate(INITIAL):
        o = observe(action, f'initial_{i}')
        write(root / 'observations' / (o['id']+'.json'), dict(time_ns=time.time_ns(), **o))
        obs.append(o)
    nodes = {'initial': dict(concept='current-state linear explanation', parent_id=None,
                            spec=BASE, origin='human initial hypothesis only')}
    models = {'initial': fit_model(BASE, obs)}
    history = []
    for round_no in range(3):
        dest = root / f'round_{round_no}'
        witnesses = collisions(obs)
        # Witness identifiers include their round; otherwise identical local ids
        # would point to different evidence as the observation set grows.
        for w in witnesses:
            w['id'] = f'r{round_no}_'+w['id']
        write(dest / 'witnesses.json', witnesses)
        context = dict(observations=[summary(o) for o in obs], witnesses=witnesses,
            hypotheses=[public_model(i,m,nodes[i]) for i,m in models.items()],
            prior_prospective_experiments=history)
        # Snapshot shared before either sibling proposes: branches are independent.
        branch_count = min(2, max(1,len(witnesses)))
        for branch in range(branch_count):
            identifier = f'r{round_no}_b{branch}'
            status(root, 'proposing', round=round_no, branch=branch, calls=luna.count)
            payload = dict(context, focus=witnesses[branch] if witnesses else None,
                instruction=('Seek a compact extension of an existing explanation.' if branch==0 else
                             'Seek a structurally distinct competing account; do not assume missing history is the only possibility.'))
            proposal, records = luna.structured(identifier, COMMON+PROPOSE, payload,
                lambda v: hypothesis_validator(v, set(models), {w['id'] for w in witnesses}))
            nodes[identifier] = dict(**proposal, generation_records=records, round=round_no)
            write(dest / (identifier+'_proposal.json'), nodes[identifier])
            status(root, 'fitting', hypothesis=identifier, calls=luna.count)
            try:
                models[identifier] = fit_model(proposal['spec'], obs)
                write(dest / (identifier+'_fit.json'), models[identifier])
            except (ValueError, np.linalg.LinAlgError, ArithmeticError, TypeError) as exc:
                nodes[identifier]['execution_failure'] = str(exc)
                write(dest / (identifier+'_execution_failure.json'), dict(error=str(exc)))
        if len(models) < 2:
            raise RuntimeError('No executable competing model; preserved actual proposals')
        status(root, 'designing_intervention', round=round_no, calls=luna.count)
        design, records = luna.structured(f'r{round_no}_design', COMMON+DESIGN,
            dict(observations=[summary(o) for o in obs], witnesses=witnesses,
                 hypotheses=[public_model(i,m,nodes[i]) for i,m in models.items()],
                 prior_prospective_experiments=history), lambda v: design_validator(v,set(models)))
        write(dest / 'design.json', dict(design=design, generation_records=records))
        forecasts, failed = {}, {}
        for identifier, model in models.items():
            try:
                forecasts[identifier] = [predict(model,control(a)).tolist() for a in design['actions']]
            except (ValueError, ArithmeticError, TypeError) as exc:
                failed[identifier] = str(exc)
        record = dict(time_ns=time.time_ns(), actions=design['actions'], models=models,
                      forecasts=forecasts, failed_rollouts=failed)
        write(dest / 'forecast_commit.json', dict(record=record, sha256=digest(record)))
        new_obs = []
        for i, action in enumerate(design['actions']):
            o = observe(action, f'r{round_no}_experiment_{i}')
            write(root / 'observations' / (o['id']+'.json'), dict(time_ns=time.time_ns(), **o))
            new_obs.append(o)
        k = int(round(design['comparison_time']/.1))
        pair = [dict(x=o['x'][k], u=o['u'][k],
                     next_half_second_slope=(o['x'][k+5]-o['x'][k])/.5) for o in new_obs]
        matched = abs(pair[0]['x']-pair[1]['x']) <= design['matching_tolerance_x'] and abs(pair[0]['u']-pair[1]['u']) < 1e-8
        prospective = {identifier: [nmse(y,np.asarray(o['x'])) for y,o in zip(pred,new_obs)]
                       for identifier,pred in forecasts.items()}
        outcome = dict(round=round_no, design=design, pair_comparison=pair,
            same_current_input_and_approximately_same_x=bool(matched),
            next_half_second_same_input_sequence=bool(np.allclose(new_obs[0]['u'][k:k+5],new_obs[1]['u'][k:k+5])),
            prospective_nmse=prospective, failed_rollouts=failed,
            note='A matched pair is diagnostic only; no causal or noise-significance certificate.')
        write(dest / 'outcome.json', outcome)
        history.append(outcome)
        obs.extend(new_obs)
        status(root, 'updating_from_observation', round=round_no, calls=luna.count)
        refreshed = {}
        for identifier, model in models.items():
            try:
                refreshed[identifier] = fit_model(model['spec'],obs)
            except (ValueError, np.linalg.LinAlgError,ArithmeticError,TypeError) as exc:
                write(dest / (identifier+'_refit_failure.json'),dict(error=str(exc)))
        models = refreshed
        if not models:
            raise RuntimeError('All hypotheses failed numerical execution')
        write(dest / 'updated_models.json', models)
    status(root, 'final_commit', calls=luna.count)
    def validate_final(v):
        if v['selected_id'] not in models:
            raise ValueError('Unknown selected hypothesis')
        for name in ('reason','concept_progress','unresolved','next_experiment'):
            if not isinstance(v[name],str) or not v[name]:
                raise ValueError('Missing final explanation')
    final, records = luna.structured('final', COMMON+'''Select the most defensible currently executable
hypothesis using only observed evidence. Do not claim to know the hidden equation. Summarize in Chinese.
JSON: {"selected_id":"existing id","reason":"...","concept_progress":"...",
"unresolved":"...","next_experiment":"..."}. Distinguish generated concepts from verified mechanisms.''',
        dict(hypotheses=[public_model(i,m,nodes[i]) for i,m in models.items()],
             prospective_experiments=history, remaining_witnesses=collisions(obs)), validate_final)
    selected = models[final['selected_id']]
    committed = dict(time_ns=time.time_ns(), decision=final, model=selected,generation_records=records)
    write(root / 'final_commit.json',dict(record=committed,sha256=digest(committed)))
    # Sealed actions and observations only read after final commitment; no later model calls.
    checks = []
    for i, action in enumerate(SEALED):
        y = truth(action)
        try:
            predicted = predict(selected,control(action))
            score = nmse(predicted,y)
            failure = None
        except (ValueError,ArithmeticError,TypeError) as exc:
            predicted, score, failure = None, None, str(exc)
        checks.append(dict(id=f'sealed_{i}',action=action, truth=y.tolist(),
            prediction=predicted.tolist() if predicted is not None else None,nmse=score,failure=failure))
    write(root / 'sealed_predictions.json',dict(time_ns=time.time_ns(),checks=checks))
    write(root / 'theory_graph.json',dict(nodes=nodes, intervention_edges=history,
        final_selected_id=final['selected_id'], scope='Generated hypotheses; not established scientific theories'))
    from audit import audit
    result = audit(root)
    write(root / 'AUDIT.json',result)
    if not result['passed']:
        raise RuntimeError('Execution provenance audit failed')
    status(root, 'completed', calls=luna.count, selected=final['selected_id'],
           sealed_mean_nmse=float(np.mean([c['nmse'] for c in checks])) if all(c['nmse'] is not None for c in checks) else None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    args = parser.parse_args()
    root = Path(args.out)
    root.mkdir(parents=True,exist_ok=False)
    key = getpass.getpass('API key (hidden): ')
    luna = Luna(key,root)
    try:
        run(root,luna)
    except Exception as exc:
        status(root,'failed',calls=luna.count,error_type=type(exc).__name__,
               error=str(exc).replace(key,'[redacted]'))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
