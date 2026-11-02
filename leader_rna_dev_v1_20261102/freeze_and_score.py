"""Record literal final commitments before loading the reserved observations."""
import datetime
import hashlib
import json
from pathlib import Path
from coordinator import ROOT,save,event

def main():
    response=ROOT/'transcripts/researcher_06_final.md'
    commitments=[
        dict(condition='A',time_h=36,predicted=0.00427284867149),
        dict(condition='A',time_h=48,predicted=0.00427284864645),
        dict(condition='B',time_h=36,predicted=0.123866283475),
        dict(condition='B',time_h=48,predicted=0.163521802539),
    ]
    commitment=dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='transcripts/researcher_06_final.md',response_sha256=hashlib.sha256(response.read_bytes()).hexdigest(),selection_source='transcripts/leader_06_final.md',model_choices=dict(A='five-point exponential decay to plateau, C02',B='five-point linear, C02'),parameters=dict(A=dict(a=0.0148725828319,c=0.00427284864642,k_per_h=0.5517275762),B=dict(alpha=0.00489972628450,beta_per_h=0.00330462658863)),predictions=commitments,scope='Literal final actor commitments; within-run unexposed timepoints of an already curator-known development case.')
    path=ROOT/'curator/FINAL_COMMITMENT.json';save(path,commitment)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    save(ROOT/'curator/FINAL_COMMITMENT_HASH.json',dict(path='curator/FINAL_COMMITMENT.json',sha256=digest))
    event('final_commitment_frozen',dict(path='curator/FINAL_COMMITMENT.json',sha256=digest,response_sha256=commitment['response_sha256']))
    # No reserved observations are loaded by this scorer until after the commitment event above.
    reserved=json.loads((ROOT/'curator/withheld_late_timepoints.json').read_text())
    actual={(x['condition'],x['time_h']):x['mean_empty_area_fraction'] for x in reserved};rows=[]
    for r in commitments:
        y=actual[r['condition'],r['time_h']];error=r['predicted']-y
        rows.append(dict(**r,observed=y,error_pred_minus_observed=error,absolute_error=abs(error),absolute_error_percentage_points=100*abs(error)))
    by_condition={c:sum(x['absolute_error'] for x in rows if x['condition']==c)/2 for c in ['A','B']}
    out=dict(run_id=ROOT.name,scored_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),commitment_sha256=digest,rows=rows,prediction_coverage=dict(submitted=4,total=4),mean_absolute_error=sum(x['absolute_error'] for x in rows)/4,mae_by_condition=by_condition,scope='Development time extrapolation only. No preset accuracy acceptance threshold, no mechanism-identification score inferred from this error, no independent preparation-level uncertainty. Original four-turn run saw these timepoints initially and is not a numeric forecast baseline.')
    save(ROOT/'RESULTS.json',out)
    event('reserved_values_scored',dict(result='RESULTS.json',commitment_sha256=digest))
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
