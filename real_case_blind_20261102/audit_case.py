"""Audit frozen records, historical retrieval dates, and measurement provenance."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
checks = []

def check(name, passed, detail=None):
    checks.append({'check':name,'passed':bool(passed),'detail':detail})

def read(rel):
    return json.loads((ROOT/rel).read_text())

for entry in read('curator/PRE_RUN_FREEZE.json'):
    check('pre_run_hash:'+entry['path'], hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256'])
for entry in read('curator/EVIDENCE_MANIFEST.json'):
    check('evidence_hash:'+entry['path'], hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256'])
for rel,digest in read('curator/FINAL_COMMITMENT_HASH.json')['sha256'].items():
    check('final_commitment_hash:'+rel,hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest)

history=read('agent_workspace/historical_results_01.json')
works=[x for q in history for x in q['results']]
check('historical_queries_cutoff',all(q['cutoff']=='2025-05-12' for q in history))
check('historical_results_dates',all(x['publication_date']<='2025-05-12' for x in works),len(works))
date_audit=read('curator/HISTORICAL_DATE_AUDIT.json')
def date_string(parts):
    return '-'.join(str(x).zfill(4 if i==0 else 2) for i,x in enumerate(parts))
for x in date_audit:
    parts=x.get('dates',{}).get('published-online',x.get('dates',{}).get('published'))
    check('crossref_date:'+x['doi'],parts is not None and date_string(parts[0])<='2025-05-12',parts)

public_text='\n'.join(p.read_text() for p in (ROOT/'agent_workspace').glob('*') if p.is_file())
for token in ['s44286-026-00454-4','chemrxiv-2025-5ffnn','Genetic encoding and mutagenesis of RNA droplet phenotypes','Fig4b_theory','onset_radius_um']:
    check('no_target_answer_in_public_files:'+token,token.lower() not in public_text.lower())

commit=read('curator/FINAL_COMMITMENT.json')
results=read('RESULTS.json')
angle=read('curator/evidence/angles_heldout.json')
mobility={x['condition']:x for x in read('curator/evidence/mobility_heldout.json')}
check('Q1_matches_raw_summary',results['Q1']['observed_A_median_um2']==mobility['A']['median_final_squared_displacement_um2'] and results['Q1']['observed_B_median_um2']==mobility['B']['median_final_squared_displacement_um2'])
check('Q2_matches_raw_summary',results['Q2']['observed_fraction_gt_90']==angle['fraction_angle_gt_90'])
check('Q2_error_from_frozen_prediction',abs(results['Q2']['absolute_error']-abs(commit['Q2']['point_prediction']-angle['fraction_angle_gt_90']))<1e-12)
check('angle_histogram_complete',sum(angle['histogram_30deg_counts'])==angle['n_steps'])
check('all_four_agent_responses_preserved',all((ROOT/f'curator/AGENT_TURN_{i:02d}{"_FINAL" if i==4 else ""}.md').exists() for i in range(1,5)))

broken=[]
for name in ['REPORT.md']:
    file=ROOT/name
    for link in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        if '://' not in link and not (file.parent/link.split('#')[0]).exists():broken.append(link)
check('report_local_links',not broken,broken)

limitations=[
    'No claim that a historical search cutoff erases model pretraining knowledge.',
    'Child was instructed to use no direct tools; an independently inspectable child tool trace was unavailable. This is not OS-level file isolation.',
    'Exact coordinator messages are retained in the conversation tool history; local packet files and four response copies are the research artifacts, not a complete exported raw execution trace.',
    'Hash checks establish current integrity, not independent proof of execution chronology or scientific validity.',
    'No new wet-lab experiment, fitted mechanistic model, or full target-theory recovery.',
    'Nested samples, unequal track durations, coordinate coupling, and missing fraction control remain material limits.'
]
report={'checks_passed':sum(x['passed'] for x in checks),'checks_total':len(checks),'checks':checks,'limitations':limitations}
(ROOT/'AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['checks_passed'],'total':report['checks_total'],'failures':[x for x in checks if not x['passed']]},ensure_ascii=False))
if report['checks_passed']!=report['checks_total']:raise SystemExit(1)
