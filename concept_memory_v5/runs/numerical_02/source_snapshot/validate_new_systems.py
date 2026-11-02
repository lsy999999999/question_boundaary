"""Numerical stress test with designer-specified hypotheses, zero LLM calls."""
import argparse
import json
from pathlib import Path
from engine import write
from memory import relation, check, extension_record
from protocol import freeze, commit, execute, audit
from worlds import configuration, designer_model, mirror_pair, observe


def run(root,seed_start=110301):
    root=Path(root);root.mkdir(parents=True,exist_ok=False)
    configs=[configuration(f,s) for f in ('linear_memory','saturated_memory','local_symmetry_only')
             for s in range(seed_start,seed_start+4)]
    freeze(root,dict(mode='designer-specified numerical fixtures', model_calls=0, systems=configs,
        initial_amplitude=.4, test_amplitude=1.3, confidence=.99,
        origin='New synthetic systems; candidates intentionally supplied by designer for tool acceptance'))
    rows=[]
    for i,config in enumerate(configs):
        exact=designer_model(config);odd=designer_model(config,include_even=False)
        models={'designer_exact':exact,'odd_extension':odd}
        packets=[];outcomes=[];relations=[]
        for stage,amplitude in [('local',.4),('extension',1.3)]:
            name=f'system_{i:02d}_{stage}'
            packet=commit(root,name,models,mirror_pair(amplitude),[name+'_positive',name+'_negative'])
            outcome=execute(root,name,packet,lambda a,oid:observe(config,a,oid))
            rel=relation(*outcome['observations'],source='prospective_synthetic_pair')
            rel['forecast_binding']=packet['sha256'];rel['model_binding']=packet['record']['fit_versions']
            packets.append(packet);outcomes.append(outcome);relations.append(rel)
        extension=extension_record(relations[0],relations[1],packets[1]['sha256'])
        byid={o['id']:o for result in outcomes for o in result['observations']}
        regressions=[check(k,m,relations[0],byid) for k,m in models.items()]
        row=dict(system=i,family=config['family'],seed=config['seed'],relations=relations,
            extension=extension,old_relation_regressions=regressions,
            extension_nmse=outcomes[1]['nmse'],
            expected_break=config['family']=='local_symmetry_only',
            observed_break=extension['extension_status']=='counterexample_to_extension')
        rows.append(row)
    write(root/'RESULTS.json',rows)
    result=audit(root)
    result.update(model_calls=0,systems=len(rows),
        local_support_count=sum(r['relations'][0]['claim_status']=='observed_local_support' for r in rows),
        break_detected=sum(r['observed_break'] for r in rows if r['expected_break']),
        broken_systems=sum(r['expected_break'] for r in rows),
        false_breaks=sum(r['observed_break'] for r in rows if not r['expected_break']),
        preserved_systems=sum(not r['expected_break'] for r in rows),
        old_local_regressions=sum(c['conflict'] for r in rows for c in r['old_relation_regressions']),
        interpretation='Tool acceptance with designer-known models; not agent discovery or comparative efficacy')
    write(root/'AUDIT.json',result);print(json.dumps(result,indent=2))
    if not result['passed']:raise RuntimeError('Audit failed')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--seed-start',type=int,default=110301)
    args=p.parse_args();run(args.out,args.seed_start)
