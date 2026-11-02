"""Check recorded integrity and chronology; scientific interpretation is reviewed separately."""
import hashlib
import json
import math
import re
from pathlib import Path
from coordinator import ROOT,save,read_events

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    checks=[]
    def check(name,ok):checks.append(dict(name=name,passed=bool(ok)))
    pre=json.loads((ROOT/'curator/PRE_RUN_MANIFEST.json').read_text())
    check('pre-run files unchanged',all((ROOT/p).exists() and sha(ROOT/p)==h for p,h in pre.items()))
    events=read_events()
    leader=sorted((ROOT/'transcripts').glob('leader_*.md'));researcher=sorted((ROOT/'transcripts').glob('researcher_*.md'))
    check('six leader and six researcher replies archived',len(leader)==len(researcher)==6)
    check('model requests recorded as fresh gpt-6-luna actors',len([e for e in events if e['kind']=='actor_created' and e['model_requested']=='gpt-6-luna' and e['fork_turns']=='none'])==2)
    comp=[e for e in events if e['kind']=='computation_completed'];release=[e for e in events if e['kind']=='evidence_release']
    check('five computation requests have results',len(comp)==5 and all((ROOT/e['script']).exists() and (ROOT/e['result']).exists() and (ROOT/e['request']).exists() for e in comp))
    check('four allowed evidence categories released once',len(release)==4 and len({e['category'] for e in release})==4)
    check('released evidence matches saved source hashes',all(sha(ROOT/e['path'])==e['sha256']==sha(Path(e['source'])) for e in release))
    initial=json.loads((ROOT/'agent_visible/initial_measurements.json').read_text())
    check('initial actor observations stop at 24h',len(initial)==10 and all(r['time_h']<=24 for r in initial))
    final=json.loads((ROOT/'curator/FINAL_COMMITMENT.json').read_text());hashrec=json.loads((ROOT/'curator/FINAL_COMMITMENT_HASH.json').read_text())
    check('final response bound to commitment',sha(ROOT/final['source'])==final['response_sha256'])
    check('commitment hash unchanged',sha(ROOT/'curator/FINAL_COMMITMENT.json')==hashrec['sha256'])
    freeze=[i for i,e in enumerate(events) if e['kind']=='final_commitment_frozen'];score=[i for i,e in enumerate(events) if e['kind']=='reserved_values_scored']
    check('commitment event precedes scoring',len(freeze)==len(score)==1 and freeze[0]<score[0])
    check('literal prediction numbers occur in final reply',all(str(p['predicted']) in (ROOT/final['source']).read_text() for p in final['predictions']))
    results=json.loads((ROOT/'RESULTS.json').read_text())
    check('four errors recompute',len(results['rows'])==4 and all(math.isclose(abs(r['predicted']-r['observed']),r['absolute_error'],abs_tol=1e-15) for r in results['rows']))
    # Target identity scan only, not an assurance against semantic leakage or pretrained recognition.
    text='\n'.join(p.read_text().lower() for p in list((ROOT/'agent_visible').glob('*'))+leader+researcher if p.is_file())
    forbidden=['s44286-026-00454-4','chemrxiv-2025-5ffnn','genetic encoding and mutagenesis of rna droplet phenotypes']
    check('no listed target identifiers in supplied packets or actor replies',not any(x in text for x in forbidden))
    old=ROOT.parent/'real_case_blind_20261102'
    orig=json.loads((old/'curator/EVIDENCE_MANIFEST.json').read_text())
    check('original prepared evidence unchanged',all(sha(old/r['path'])==r['sha256'] for r in orig))
    prompt=ROOT.parent/'leader_methods_v1_20261102'
    check('frozen prompt/library copies match parent v1',all(sha(p)==sha(prompt/p.name) for p in (ROOT/'frozen_prompts').glob('*')))
    out=dict(status='passed' if all(c['passed'] for c in checks) else 'failed',checks=checks,passed=sum(c['passed'] for c in checks),total=len(checks),limits=['Artifact/chronology checks do not establish scientific correctness.','No OS-level isolation or independently exported complete child tool trace.','Coordinator messages include operational extracts and summaries, not a verbatim exported complete raw execution trace. Full actor replies are archived.','Zero background queries: the date-filtered retrieval path was not exercised.','The curator had already seen reserved values; this is a development replay.'])
    save(ROOT/'AUDIT.json',out)
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
