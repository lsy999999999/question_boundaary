"""Typed evidence: stable fit identity, scoring phase, window and observation provenance."""
import numpy as np
from engine import digest,GRID,nmse,control
from numerics import predict


def fit_id(spec,fit):return digest(dict(spec=spec,fit=fit))


def local_facts(obs):
    byid={o['id']:o for o in obs};facts=[]
    for r,factor in ((0,-1.),(1,-1.),(2,1.5)):
        ids=[f'v3_r{r}_experiment_{i}' for i in (0,1)];a,b=[byid[i] for i in ids]
        if not np.allclose(np.array(b['u']),factor*np.array(a['u'])):raise ValueError('Historical relation inputs changed')
        residual=np.array(b['x'])-factor*np.array(a['x']);noise=float(np.hypot(b['noise_std'],factor*a['noise_std']));value=float(np.sqrt(np.mean(residual**2)))
        facts.append(dict(id=f'local_relation_{r}',kind='observed_local_relation',observations=ids,actions=[a['action'],b['action']],
            factor=factor,metric='relation_rms',phase='observed_property',time_window=[0.,12.],value=value,noise_rms=noise,
            property='near_mirror' if value<=2*noise else 'nonproportional_response',
            scope='Only these recorded inputs and reset initial conditions; not a universal law'))
    return facts


def retention(model,facts):
    result=[]
    for fact in facts:
        try:
            y=[predict(model,control(a)) for a in fact['actions']];rms=float(np.sqrt(np.mean((y[1]-fact['factor']*y[0])**2)))
            compatible=(rms<=2*fact['noise_rms']) if fact['property']=='near_mirror' else (rms>2*fact['noise_rms'])
            result.append(dict(relation_id=fact['id'],property=fact['property'],fit_version=fit_id(model['spec'],model['fit']),
                metric='predicted_relation_rms',time_window=[0.,12.],value=rms,status='compatible' if compatible else 'conflict',
                check_scope='qualitative property on original inputs; not complete trajectory accuracy'))
        except (ValueError,ArithmeticError,TypeError) as exc:result.append(dict(relation_id=fact['id'],property=fact['property'],status='unavailable',error=str(exc)))
    return result


def metrics(models,obs):
    byid={o['id']:o for o in obs};rows=[];windows=[]
    for mid,m in models.items():
        snapshot=fit_id(m['spec'],m['fit'])
        rows.append(dict(id='aggregate:'+mid+':'+snapshot[:12],owner_model_id=mid,model_snapshot=snapshot,
            metric='group_mean_trajectory_nmse',phase='adaptive_group_held_out_diagnostic',time_window=[0.,12.],value=m['group_cv_nmse']))
        snippets=[]
        for fold in m['cv_folds']:
            fid=fit_id(m['spec'],fold['fit'])
            for oid,pred in zip(fold['ids'],fold['predictions']):
                o=byid[oid];y=np.array(pred);x=np.array(o['x']);err=y-x;score=nmse(y,x)
                identifier='cv:'+mid+':'+fid[:12]+':'+oid
                rows.append(dict(id=identifier,owner_model_id=mid,fit_version=fid,model_snapshot=snapshot,observation=oid,
                    metric='trajectory_nmse',phase='adaptive_group_held_out_diagnostic',time_window=[0.,12.],value=score,
                    denominator=max(float(np.var(x)),.02),high_error=score>.05))
                k=int(np.argmax(np.convolve(err**2,np.ones(6)/6,mode='valid')))
                snippets.append(dict(metric_id=identifier,owner_model_id=mid,fit_version=fid,metric='window_rmse',
                    time_window=[float(GRID[k]),float(GRID[k+5])],value=float(np.sqrt(np.mean(err[k:k+6]**2))),
                    samples_t_u_observed_predicted=[[float(GRID[i]),o['u'][i],float(x[i]),float(y[i])] for i in range(k,k+6)]))
        windows.extend(sorted(snippets,key=lambda s:s['value'],reverse=True)[:2])
    return rows,windows


def prospective_metrics(record,observations):
    out=[]
    for mid,ys in record['forecasts'].items():
        fid=fit_id(record['models'][mid]['spec'],record['models'][mid]['fit'])
        for oid,y,o in zip(record['observation_ids'],ys,observations):
            value=nmse(np.array(y),np.array(o['x']))
            out.append(dict(id='prospective:'+mid+':'+fid[:12]+':'+oid,owner_model_id=mid,fit_version=fid,observation=oid,
                metric='trajectory_nmse',phase='observed_error_of_precommitted_prediction',time_window=[0.,12.],value=value,high_error=value>.05,
                forecast_commit_time_ns=record['time_ns'],observation_time_ns=o['time_ns']))
    return out


def check_citations(ids,ctx,owner=None):
    evidence={x['id']:x for x in ctx['metrics']+ctx['facts']+[ctx['historical_refutation']]}
    if not ids or any(i not in evidence for i in ids):raise ValueError('Cite existing typed evidence IDs')
    if owner and any(evidence[i].get('owner_model_id',owner)!=owner for i in ids):raise ValueError('Model status cannot cite another model owner')


def choose(models,withdrawn,facts):
    assessments={k:retention(m,facts) for k,m in models.items()};eligible=[]
    for k,m in models.items():
        mirrors=[a for a in assessments[k] if a['property']=='near_mirror']
        if k not in withdrawn and m['group_cv_nmse'] is not None and len(mirrors)==2 and all(a['status']=='compatible' for a in mirrors):eligible.append(k)
    ordered=sorted(eligible,key=lambda k:(models[k]['group_cv_nmse'],k))
    selected=ordered[0] if ordered else None
    return dict(selected_id=selected,criterion='minimum_group_cv_among_not_withdrawn_complete_cv_and_two_local_mirror_compatible',
        eligible_order=ordered,scores={k:models[k]['group_cv_nmse'] for k in ordered},retention=assessments,
        explanation=(f'按冻结规则选择 {selected}，当前分组CV NMSE={models[selected]["group_cv_nmse"]:.8f}。' if selected else '没有满足冻结选择条件的候选。'),
        decision_author='deterministic_tool_rule_not_Luna_free_choice')
