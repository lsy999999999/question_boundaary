"""Leader turn 5 requested retrospective 24h checks and five-point refits."""
import json
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'computations'))
from coordinator import save,event
from c02_time_fits import fit,evaluate

def main():
    data=json.loads((ROOT/'agent_visible/initial_measurements.json').read_text());results=[]
    for cond in ['A','B']:
        all_rows=[r for r in data if r['condition']==cond]
        target24=next(r['mean_empty_area_fraction'] for r in all_rows if r['time_h']==24)
        for n in [4,5]:
            rows=all_rows[:n];t=np.array([r['time_h'] for r in rows]);y=np.array([r['mean_empty_area_fraction'] for r in rows])
            expo=fit(rows,cond);p=expo['internal_parameterization'];pred24=float(evaluate([p['base'],p['q'],p['k']],np.array([24]),cond)[0])
            expo.update(n_training_points=n,prediction24=pred24,error24_pred_minus_obs=pred24-target24,is_24h_training_point=n==5)
            results.append(expo)
            alpha,beta=np.linalg.lstsq(np.column_stack([np.ones_like(t),t]),y,rcond=None)[0];pred=alpha+beta*t
            results.append(dict(condition=cond,model='linear',n_training_points=n,parameters=dict(alpha=float(alpha),beta_per_h=float(beta)),sse=float(np.sum((pred-y)**2)),training_times_h=t.tolist(),fitted=pred.tolist(),residual_pred_minus_obs=(pred-y).tolist(),prediction24=float(alpha+beta*24),error24_pred_minus_obs=float(alpha+beta*24-target24),is_24h_training_point=n==5,predictions=[dict(time_h=h,empty_fraction=float(alpha+beta*h),within_unit_interval=bool(0<=alpha+beta*h<=1)) for h in [36,48]],constraint_note='Ordinary linear comparator, not truncated or interpreted as globally bounded. Exponential family alone has bounded monotone constraints.'))
    out=dict(compute_id='C05',request_source='transcripts/leader_05.md',fits=results,definition='Equal-weight fits; exponential constraints and 27 starts identical to C02. No SEM likelihood. 24h was already visible and this is retrospective model criticism, not blind validation. Five-point 24h errors are training residuals.',hidden_data_accessed=False)
    save(ROOT/'computations/C05_result.json',out)
    event('computation_completed',dict(compute_id='C05',request='transcripts/leader_05.md',script='computations/c05_retrospective_fits.py',result='computations/C05_result.json',budget_unit=1))
    print(json.dumps([dict(condition=x['condition'],model=x['model'],n=x['n_training_points'],params=x['parameters'],sse=x['sse'],pred24=x['prediction24'],error24=x['error24_pred_minus_obs'],future=x['predictions']) for x in results],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
