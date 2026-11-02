"""Independent grouped fits with deterministic aggregation and fixed numerical settings."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import multiprocessing as mp
import numpy as np
from numerics import fit_trajectory,predict,groups,input_key
from engine import nmse


def job(raw,train,heldout,warm):
    try:
        fitted=fit_trajectory(raw,train,warm=warm)
        if heldout is None:return {'fit':fitted}
        m=dict(spec=raw,fit=fitted);ys=[predict(m,o['u']).tolist() for o in heldout]
        return dict(ids=[o['id'] for o in heldout],nmse=float(np.mean([nmse(np.array(y),np.array(o['x'])) for y,o in zip(ys,heldout)])),fit=fitted,predictions=ys)
    except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError) as exc:return dict(error=str(exc))


class Fitter:
    def __init__(self,workers=8):
        self.pool=ProcessPoolExecutor(max_workers=workers,mp_context=mp.get_context('spawn'))
    def close(self):self.pool.shutdown(wait=True)
    def fit(self,specs,obs,warms=None,progress=None):
        gs=groups(obs);pending={};results={};warms=warms or {}
        if len(gs)<2:raise ValueError('Need distinct input groups')
        for key,raw in specs.items():
            for i,g in enumerate(gs):
                train=[o for o in obs if input_key(o)!=input_key(g[0])]
                pending[self.pool.submit(job,raw,train,g,None)]=(key,i)
            pending[self.pool.submit(job,raw,obs,None,warms.get(key))]=(key,-1)
        total=len(pending)
        for future in as_completed(pending):
            tag=pending[future];results[tag]=future.result()
            if progress:progress(len(results),total)
        fitted={};failed={}
        for key,raw in specs.items():
            full=results[(key,-1)]
            if 'error' in full:failed[key]=full['error'];continue
            folds=[];errors=[]
            for i,g in enumerate(gs):
                r=results[(key,i)]
                if 'error' in r:errors.append(dict(ids=[o['id'] for o in g],error=r['error']))
                else:folds.append(r)
            fitted[key]=dict(spec=raw,fit=full['fit'],cv_folds=folds,cv_failures=errors,distinct_inputs=len(gs),
                group_cv_nmse=float(np.mean([f['nmse'] for f in folds])) if not errors else None)
        return fitted,failed
