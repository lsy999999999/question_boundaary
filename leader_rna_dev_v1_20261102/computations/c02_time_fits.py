"""Fit exactly the descriptive families requested in researcher turn 2, training only."""
import itertools
import json
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from coordinator import save,event

def evaluate(p,t,cond):
    base,q,k=p
    if cond=='A':return base+(1-base)*q*np.exp(-k*t)
    return base+(1-base)*q*(-np.expm1(-k*t))

def fit(rows,cond):
    t=np.array([r['time_h'] for r in rows]);y=np.array([r['mean_empty_area_fraction'] for r in rows])
    solutions=[]
    for base,q,k in itertools.product([0.001,0.01,0.1],[0.01,0.2,0.9],[0.001,0.05,1.0]):
        res=least_squares(lambda p:evaluate(p,t,cond)-y,[base,q,k],bounds=([0,0,1e-10],[1,1,np.inf]),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=10000)
        solutions.append(res)
    best=min(solutions,key=lambda r:np.sum(r.fun**2));base,q,k=best.x
    params=dict(c_A=float(base),a_A=float(base+(1-base)*q),k_A_per_h=float(k)) if cond=='A' else dict(a_B=float(base),c_B=float(base+(1-base)*q),k_B_per_h=float(k))
    vals=evaluate(best.x,t,cond);future=evaluate(best.x,np.array([36,48]),cond)
    return dict(condition=cond,model='decay_to_plateau' if cond=='A' else 'rise_to_plateau',parameters=params,internal_parameterization=dict(base=float(base),q=float(q),k=float(k)),parameterization_note='A:c=base,a=c+(1-c)q. B:a=base,c=a+(1-a)q; base,q in [0,1],k>0. Same constrained family as requested.',training_times_h=t.tolist(),observed=y.tolist(),fitted=vals.tolist(),residual_pred_minus_obs=(vals-y).tolist(),sse=float(np.sum((vals-y)**2)),multistart=dict(n=len(solutions),success_count=sum(r.success for r in solutions),min_sse=float(min(np.sum(r.fun**2) for r in solutions)),max_sse=float(max(np.sum(r.fun**2) for r in solutions))),predictions=[dict(time_h=t,empty_fraction=float(v),within_unit_interval=bool(0<=v<=1)) for t,v in zip([36,48],future)],limits='Unweighted descriptive least squares; no preparation-level sampling intervals. Boundary parameters may be weakly identified.')

def main():
    rows=json.loads((ROOT/'agent_visible/initial_measurements.json').read_text())
    results=[fit([r for r in rows if r['condition']==c],c) for c in ['A','B']]
    data=[r for r in rows if r['condition']=='B'];t=np.array([r['time_h'] for r in data]);y=np.array([r['mean_empty_area_fraction'] for r in data])
    alpha,beta=np.linalg.lstsq(np.column_stack([np.ones_like(t),t]),y,rcond=None)[0]
    pred=alpha+beta*t
    linear=dict(condition='B',model='linear',parameters=dict(alpha=float(alpha),beta_per_h=float(beta)),sse=float(np.sum((pred-y)**2)),fitted=pred.tolist(),residual_pred_minus_obs=(pred-y).tolist(),predictions=[dict(time_h=t,empty_fraction=float(alpha+beta*t),within_unit_interval=bool(0<=alpha+beta*t<=1)) for t in [36,48]],statistical_interval=None)
    out=dict(compute_id='C02',request_source='transcripts/researcher_02.md',training_data='agent_visible/initial_measurements.json',fits=results,linear_B=linear,hidden_data_accessed=False)
    save(ROOT/'computations/C02_result.json',out)
    event('computation_completed',dict(compute_id='C02',request='transcripts/researcher_02.md',script='computations/c02_time_fits.py',result='computations/C02_result.json',budget_unit=1))
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
