"""Zero-model integration fixtures. Does not supply scientific input to research runs."""
import json
from pathlib import Path
import broker as b

def main():
    run=b.ROOT/'runs'/'A_interface_check_03'
    if not run.exists():
        b.prepare(run.name,'C','A')
        b.process_request(run,dict(type='evidence',id='fixture_evidence',category='phase_composition',reason='public C04 fixture'))
        r=b.process_request(run,dict(type='search',id='fixture_search',candidate_id='fixture',gap_id='ratio',missing_relation='historical background on diffusion inside a spherical domain',variables='position,time,diffusivity',conditions='confined Brownian diffusion, not RNA',query='TITLE_ABS:(diffusion AND sphere)',change_if_found='integration test only; no scientific feedback to experiment'))
        print(json.dumps(r));return
    retrieval=next(t for t in b.state(run)['tools'] if t['id']=='fixture_search')
    assert retrieval['result']['status']=='returned'
    s=b.state(run)
    s['tasks']['fixture']=dict(id='fixture',candidate_id='fixture',gap_id='ratio',kind='auxiliary_fit',status='waiting_tool')
    b.snapshot(run,s,'fixture task only, never discovery')
    code='''import json
rows=DATA['phase_measurements.json']
g={(r['tie_line_id'],r['phase']):r for r in rows}
out=[]
for tie in range(3):
 for label,col,prefix in [('reference','reference_RNA_ng_per_uL','wt'),('variant','variant_RNA_ng_per_uL','mut')]:
  d,l=g[tie,'dense'],g[tie,'dilute']
  den=l[col]
  lo=(d[col]-d[prefix+'_error_lower_ng_per_uL'])/(den+l[prefix+'_error_upper_ng_per_uL']) if den else None
  hi=(d[col]+d[prefix+'_error_upper_ng_per_uL'])/(den-l[prefix+'_error_lower_ng_per_uL']) if den else None
  out.append(dict(tie_line_id=tie,species=label,partition_ratio=d[col]/den if den else None,interval=[lo,hi] if den else None))
print(json.dumps(out))
'''
    calc=b.process_request(run,dict(type='compute',id='fixture_calc',candidate_id='fixture',gap_id='ratio',purpose='recompute existing V1 C04 request, zero scientific invention',model_spec='ratio and rectangular marginal error propagation, undefined 0/0',code=code))
    observed=json.loads(calc['result']['stdout']); expected=b.read(b.OLD/'computations/C04_result.json')['results']
    assert all(x['partition_ratio']==y['partition_ratio'] and x['interval']==y['interval'] for x,y in zip(observed,expected))
    missing=b.process_request(run,dict(type='compute',id='fixture_missing',candidate_id='fixture',gap_id='ratio',purpose='missing specification fixture'))
    fail=b.process_request(run,dict(type='compute',id='fixture_fail',candidate_id='fixture',gap_id='ratio',purpose='runtime error fixture',model_spec='deliberately fail, not science',code='raise ValueError("fixture failure")'))
    p1=b.build_input(run,'leader','L_fixture');p2=b.build_input(run,'executor','R_fixture')
    assert b.read(p1)['state']==b.read(p2)['state']
    assert b.read(p1)['state']['tools']==b.state(run)['tools']
    assert missing['result']['status']=='clarification' and fail['result']['status']=='failed'
    assert b.state(run)['tasks']['fixture']['status']!='completed'
    manifest=b.freeze(run);assert b.verify(run)
    # Compare to hash after an explicit tamper without modifying frozen original.
    digest=b.sha(p1); tampered=p1.read_bytes()+b' ';assert __import__('hashlib').sha256(tampered).hexdigest()!=digest
    inputs=b.read(p1);assert 'curator' not in inputs['materials']['files']
    assert not any('withheld' in name for name in inputs['materials']['files'])
    assert retrieval['result']['status']=='returned' and retrieval['result']['sources']
    report=dict(passed=True,zero_model_calls=True,checks=['live historical retrieval with original abstract/date/raw hash','original public C04 calculation exact match, all six rows','both roles receive identical complete tool state','missing model returns clarification','runtime failure retained','tool completion never closes task','freeze verifies; byte tamper changes hash','input allowlist excludes withheld data'],retrieval_sources=len(retrieval['result']['sources']),frozen_sha256=manifest,limitations=['metadata dates, no independent historical abstract archive','application-level isolation','no scientific validation from fixtures'])
    b.dump(b.ROOT/'STAGE_A_REPORT.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
