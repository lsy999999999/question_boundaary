"""Replay observed V4 failures. No new model call and no simulator truth."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from engine import digest, write
from memory import discover, review
from temporal import op, label


def run(source, out):
    source = Path(source); out = Path(out); out.mkdir(parents=True, exist_ok=False)
    read = lambda p:json.loads(p.read_text())
    used = sorted((source/'observations').glob('*.json'))
    source_before={str(p.relative_to(source.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in source.parent.parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    obs = [read(p) for p in used]
    # Restore initial data order to make duplicate representative choice explicit.
    seed = read(source.parent.parent/'seed_public.json')
    byid = {o['id']:o for o in obs}
    obs = [byid[o['id']] for o in seed['observations']] + [o for o in obs if o['id'] not in {x['id'] for x in seed['observations']}]
    relations = discover(obs)
    modelpath = source/'round_1/models_before_experiment.json'; used.append(modelpath)
    models = read(modelpath)
    checks = review(models, relations, obs)
    pair = read(source/'round_1/forecast_commit.json')['record']; used.append(source/'round_1/forecast_commit.json')
    # Generic temporal composition: duration of zero input during [3.5,4.5).
    quiet = op('le', op('abs', {'signal':'u'}), .1)
    interval = op('and', op('ge', {'signal':'t'}, 3.5), op('lt', {'signal':'t'}, 4.5))
    scope = dict(expression=op('gt', op('duration', op('and', quiet, interval)), .5), reduce='last')
    from engine import control
    from boundaries import features
    us = [control(a) for a in pair['actions']]
    diagnostic = dict(actions=pair['actions'], old_features=[features(u) for u in us],
        generic_temporal_scope=scope, new_labels=[label(scope,u) for u in us],
        purpose='Expressibility test only; does not establish a correct error boundary')
    source_hashes = {str(p.relative_to(source)):__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in used}
    write(out/'observations.json', obs); write(out/'relations.json', relations)
    write(out/'regressions.json', checks); write(out/'temporal_gap.json', diagnostic)
    known = [c for c in checks if c['model_id']=='b4_r1' and
             any(x.startswith('v3_r0_') or x.startswith('v3_r1_') for x in c['observation_ids'])]
    passed = len(known)==2 and all(c['conflict'] for c in known)
    passed &= diagnostic['old_features'][0] == diagnostic['old_features'][1]
    passed &= diagnostic['new_labels'] == [False, True]
    source_after={str(p.relative_to(source.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in source.parent.parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    unchanged=source_before==source_after;passed &= unchanged
    report = dict(time_ns=time.time_ns(), passed=bool(passed), source_hashes=source_hashes,
        mode='posthoc historical replay', model_calls=0, relation_count=len(relations),
        known_regressions=known, total_conflicts=sum(c.get('conflict') is True for c in checks),
        temporal_gap_distinguished=diagnostic['new_labels'],
        raw_observations_sha256=digest(obs), source_unchanged=unchanged,
        source_tree_sha256=digest(source_before),source_tree_files=len(source_before))
    write(out/'RESULT.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_hashes','known_regressions')}, indent=2))
    if not passed:raise RuntimeError('Historical regression check failed')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
    args=p.parse_args();run(args.source,args.out)
