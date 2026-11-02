"""Post-hoc diagnosis of immutable recorded data; no API or simulator calls.

Uses local numeric environment for diagnostic refits only, not to replace scores.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import sys
import json
import hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
import scipy
from scipy.signal import savgol_filter
from scipy.optimize import linprog, brentq

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent/'concept_discovery_v2'
RUN = SOURCE/'runs/discovery_01'
sys.path.insert(0,str(SOURCE))
from engine import Spec, GRID, fit_core, predict, control, nmse, smooth_mask


def read(p): return json.loads(p.read_text())
def dump(name,data): (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False))
def actionkey(o):
    # Compare actual numeric inputs, not JSON spelling (1 and 1.0 are identical).
    return json.dumps(np.asarray(o['u'],dtype=float).round(12).tolist(),separators=(',',':'))


def main():
    initial_hashes={str(p.relative_to(RUN)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in RUN.rglob('*') if p.is_file()}
    observations=[read(RUN/'observations'/f'initial_{i}.json') for i in range(3)]
    observations += [read(RUN/'observations'/f'r{r}_experiment_{i}.json') for r in range(3) for i in range(2)]
    by_id={o['id']:o for o in observations}
    final=read(RUN/'final_commit.json')['record']
    models=read(RUN/'round_2/updated_models.json')
    groups=defaultdict(list)
    for o in observations: groups[actionkey(o)].append(o)
    unique_models={k:m for k,m in models.items() if k!='r0_b0'}
    out=dict(scope='Post-hoc diagnostic; no new model calls or simulator experiments; frozen results unchanged',
             python=sys.version,numpy=np.__version__,scipy=scipy.__version__)
    out['input_coverage']=dict(observations=len(observations),unique_inputs=len(groups),
        groups=[dict(ids=[o['id'] for o in v],points=v[0]['action']['points']) for v in groups.values()])
    out['derivative_fit_support']=[dict(id=o['id'],retained_points=int(smooth_mask(o['u']).sum()),
        retained_nonzero_input_points=int(np.sum(smooth_mask(o['u']) & (np.abs(o['u'])>1e-8)))) for o in observations]

    preflight=[]
    for r in range(3):
        dest=RUN/f'round_{r}'
        committed=read(dest/'forecast_commit.json')['record']
        design=read(dest/'design.json')['design']; outcome=read(dest/'outcome.json')
        k=round(design['comparison_time']/.1)
        gaps={key:abs(v[0][k]-v[1][k]) for key,v in committed['forecasts'].items()}
        actual=abs(outcome['pair_comparison'][0]['x']-outcome['pair_comparison'][1]['x'])
        preflight.append(dict(round=r,target_hypotheses=design['hypotheses'],predicted_gaps=gaps,
            observed_gap=actual,tolerance=design['matching_tolerance_x'],
            all_target_models_predicted_failure=all(gaps[h]>design['matching_tolerance_x'] for h in design['hypotheses']),
            actual_tolerance_multiple=actual/design['matching_tolerance_x']))
    out['preflight']=preflight

    # Original final fit, replayed on observed data, without fitting anything.
    training=[]
    for o in observations:
        pred=predict(final['model'],o['u'])
        measured=np.array(o['x'])
        training.append(dict(id=o['id'],nmse=nmse(pred,measured),
            observed_end=float(measured[-1]),predicted_end=float(pred[-1]),
            rmse=float(np.sqrt(np.mean((pred-measured)**2)))))
    out['original_final_fit_on_observed_data']=training

    # Mirror-symmetry statistic uses only actually measured trajectories.
    positive=np.mean([by_id[f'r{r}_experiment_0']['x'] for r in range(3)],axis=0)
    negative=np.array(by_id['r2_experiment_1']['x'])
    mirror_sum=positive+negative
    c2=read(RUN/'round_2/forecast_commit.json')['record']
    out['mirror_symmetry']=dict(
        positive_ids=[f'r{r}_experiment_0' for r in range(3)],negative_id='r2_experiment_1',
        actual_inputs_are_negatives=bool(np.allclose(by_id['r2_experiment_0']['u'],-np.array(by_id['r2_experiment_1']['u']))),
        measured_sum_rms=float(np.sqrt(np.mean(mirror_sum**2))),
        expected_sum_noise_sd=float(.005*np.sqrt(1+1/3)),
        positive_signal_rms=float(np.sqrt(np.mean(positive**2))),
        normalized_even_component=float(np.linalg.norm(mirror_sum)/(np.linalg.norm(positive)+np.linalg.norm(negative))),
        prospective_models={key:dict(sum_rms=float(np.sqrt(np.mean((np.array(v[0])+np.array(v[1]))**2))),
            nmse=read(RUN/'round_2/outcome.json')['prospective_nmse'][key]) for key,v in c2['forecasts'].items()},
        caution='Observed approximate odd response for this particular pulse, not a global symmetry proof.')

    # Exact affine change of coordinates of the final model. No fit or truth lookup.
    a,b,c,d=final['model']['fit']['coefficients'];p=final['model']['fit']['parameters'][0]
    ratio=d/c;q=p+ratio;B=b+ratio;k=b+q;D=-ratio*k;h=a/k
    transformed=dict(spec=dict(parameters=[],states=[dict(name='z0',meaning='affine output-history coordinate',
        rate=f'x-({q!r})*z0+({h!r})')],terms=['1','x','u','z0']),
        fit=dict(parameters=[],coefficients=[a,B,c,D]))
    discrepancies=[]
    for o in observations:
        discrepancies.append(float(np.max(np.abs(predict(final['model'],o['u'])-predict(transformed,o['u'])))))
    out['coordinate_equivalence']=dict(original_coefficients=dict(a=a,b=b,c=c,d=d,p=p),
        transformed=dict(q=q,B=B,D=D,hidden_affine_term=h,k=k),
        coordinate='w=(x-c*z)/(b+p+d/c)',
        equations=['dx=a+(b+d/c)*x+c*u-(d/c)*(b+p+d/c)*w',
                   'dw=x-(p+d/c)*w+a/(b+p+d/c)'],
        maximum_recorded_input_replay_difference=max(discrepancies),
        conditions='c != 0 and b+p+d/c != 0; initial x=z=w=0. Exact for the same simultaneous Euler scheme.',
        scope='Affine output-history realization of final input-history model, NOT equality of the two separately fitted hypotheses.',
        restriction='When a=0 the hidden affine term vanishes. Actual output-history proposal did not include this term; exact equality is not asserted for its frozen parameters.')

    # Canonical linear transfer descriptors, independent of names of latent variables.
    descriptors={}
    for key in ('r1_b0','r1_b1'):
        m=models[key];aa,bb,cc,dd=m['fit']['coefficients'];pp=m['fit']['parameters'][0]
        if key=='r1_b0':
            numerator=[cc,cc*pp+dd];denominator=[1,pp-bb,-bb*pp]
        else:
            numerator=[cc,cc*pp];denominator=[1,pp-bb,-bb*pp-dd]
        descriptors[key]=dict(numerator=numerator,denominator=denominator,
            poles=np.roots(denominator).tolist(),zero=float(-numerator[1]/numerator[0]),
            note='Input-dependent transfer only; affine forcing separate.')
    out['fitted_transfer_functions']=descriptors

    # Leave an entire input schedule out, so repeated noisy copies cannot sit in training.
    cv=[]
    for key,m in unique_models.items():
        folds=[]
        for action,held in groups.items():
            train=[o for o in observations if actionkey(o)!=action]
            f=fit_core(Spec(m['spec']),train)
            fitted=dict(spec=m['spec'],fit=f)
            values=[nmse(predict(fitted,o['u']),np.array(o['x'])) for o in held]
            folds.append(dict(ids=[o['id'] for o in held],mean_nmse=float(np.mean(values))))
        cv.append(dict(hypothesis=key,original_leave_one_trajectory_nmse=m['trajectory_cv_nmse'],
            grouped_equal_input_mean_nmse=float(np.mean([v['mean_nmse'] for v in folds])),
            grouped_equal_observation_mean_nmse=float(sum(v['mean_nmse']*len(v['ids']) for v in folds)/len(observations)),
            folds=folds))
    out['posthoc_grouped_diagnostic']=dict(results=cv,
        note='New local numeric refits on existing observations only; different grouping/weighting from original. Not replacement benchmark scores.')

    # Parameter profile: nonlinear fit optimizes derivative residual, not rollout error.
    profiles={}
    for key in ('r1_b0','r1_b1'):
        m=models[key];spec=Spec(m['spec']);pr=spec.params[0]
        points=[]
        for param in np.linspace(pr['lower'],pr['upper'],81):
            blocks=[spec.features_observed(o,[param]) for o in observations]
            A=np.vstack([v[0] for v in blocks]);y=np.concatenate([v[1] for v in blocks])
            scale=np.maximum(np.sqrt(np.mean(A*A,axis=0)),1e-5);N=A/scale
            coef=np.linalg.solve(N.T@N+np.eye(A.shape[1])*len(y)*1e-5,N.T@y)/scale
            mm=dict(spec=m['spec'],fit=dict(parameters=[float(param)],coefficients=coef.tolist()))
            score=float(np.mean([nmse(predict(mm,o['u']),np.array(o['x'])) for o in observations]))
            points.append(dict(p=float(param),derivative_mse=float(np.mean((A@coef-y)**2)),in_sample_rollout_nmse=score))
        profiles[key]=dict(recorded_p=m['fit']['parameters'][0],
            derivative_min_on_grid=min(points,key=lambda v:v['derivative_mse']),
            rollout_min_on_grid=min(points,key=lambda v:v['in_sample_rollout_nmse']),points=points,
            caution='Both objectives use training data. No generalization claim or score replacement.')
    out['parameter_profiles']=profiles

    # Conditional feasibility search under two frozen linear fits + initial model.
    # No query to the hidden simulator and no experiment executed.
    ms=read(RUN/'round_1/forecast_commit.json')['record']['models']
    chosen=['initial','r1_b0','r1_b1'];times=[.5,2,4,6,7];comparison=80
    basis=[]
    for j in range(4):
        u=np.zeros(len(GRID));u[(GRID>=times[j])&(GRID<times[j+1])]=1;basis.append(u)
    match,slope=[],[]
    for name in chosen:
        zero=predict(ms[name],np.zeros(len(GRID)))
        responses=[predict(ms[name],u)-zero for u in basis]
        match.append([r[comparison] for r in responses])
        slope.append([(r[comparison+5]-r[comparison])/.5 for r in responses])
    match,slope=np.array(match),np.array(slope)
    contrast=slope[1]-slope[2]
    opt=linprog(-contrast,A_ub=np.vstack([match,-match]),b_ub=np.full(6,.04),bounds=[(-3,3)]*4,method='highs')
    feasibility=dict(solved=bool(opt.success),scope='Model-only diagnostic. These inputs have NOT been observed or tested on the simulator.')
    if opt.success:
        pair=[]
        for sign in (1,-1):
            pair.append(dict(points=[[0,0]]+[[times[j],float(sign*opt.x[j]/2)] for j in range(4)]+[[7,0]]))
        pred={name:[predict(ms[name],control(a)) for a in pair] for name in chosen}
        feasibility.update(actions=pair,
            predicted_match_gaps={name:float(abs(v[0][comparison]-v[1][comparison])) for name,v in pred.items()},
            max_slope_effect_disagreement_in_this_four_segment_class=float(contrast@opt.x),
            endpoint_pair_slope_noise_sd=.02,
            caution='Linear-program optimum for these fixed fits/segment times only; not proof about all designs, actual matching, or scientific mechanisms.')
    out['conditional_design_feasibility']=feasibility

    sealed=read(RUN/'sealed_predictions.json')['checks']
    scores=np.array([r['nmse'] for r in sealed])
    worst=sealed[int(np.argmax(scores))]
    ix=int(np.argmax(np.abs(np.array(worst['prediction'])-np.array(worst['truth']))))
    out['sealed_posthoc']=dict(mean=float(scores.mean()),worst_id=worst['id'],worst_nmse=worst['nmse'],
        worst_fraction_of_sum_nmse=float(max(scores)/sum(scores)),max_abs_error_time=float(GRID[ix]),
        predicted_at_max_error=worst['prediction'][ix],truth_at_max_error=worst['truth'][ix],
        note='Already evaluated sealed data, now inspected for diagnosis. Must not become a new untouched confirmation set.')

    # Privileged theoretical diagnosis from the already-read simulator definition.
    # Never used in any hypothesis fitting or model-only planning above.
    equilibrium=brentq(lambda x:-.85*x+.65*np.tanh(1.8*x),.1,2)
    eigen=[dict(real=float(v.real),imag=float(v.imag)) for v in
           np.linalg.eigvals(np.array([[-.85,.65*1.8],[.45,-.45]]))]
    out['privileged_world_diagnosis']=dict(nonzero_equilibria=[-equilibrium,equilibrium],
        zero_equilibrium_eigenvalues=eigen,
        note='Analyst access to simulator equations, NOT an agent discovery or inference from finite observations. Do not put equations/labels in next agent prompt.')
    end_hashes={str(p.relative_to(RUN)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in RUN.rglob('*') if p.is_file()}
    assert initial_hashes==end_hashes
    out['frozen_run_unchanged']=True
    dump('DIAGNOSTICS.json',out)
    print(json.dumps({k:v for k,v in out.items() if k not in ('parameter_profiles','original_final_fit_on_observed_data')},ensure_ascii=False,indent=2))
    make_plot(preflight,positive,negative,worst)


def make_plot(preflight,positive,negative,worst):
    os.environ['MPLCONFIGDIR'] = str(HERE/'plot_cache')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(15,4.2),constrained_layout=True)
    ax=axes[0]
    for i,r in enumerate(preflight):
        values=[r['predicted_gaps'][h]/.04 for h in r['target_hypotheses']]
        ax.plot([i,i],[min(values),max(values)],color='#2563a5',lw=4)
        ax.scatter([i]*len(values),values,color='#2563a5',s=35)
        ax.scatter(i+.16,r['actual_tolerance_multiple'],color='#d05532',marker='x',s=70)
    ax.axhline(1,color='#555555',ls='--',lw=1)
    ax.set(xticks=[0,1,2],xticklabels=['Round 1','Round 2','Round 3'],ylabel='State gap / allowed tolerance',
           title='A  Failure was predictable')
    ax.plot([],[],color='#2563a5',marker='o',label='Committed model prediction')
    ax.plot([],[],color='#d05532',marker='x',ls='',label='Observed gap')
    ax.legend(fontsize=8,frameon=False)
    ax=axes[1]
    ax.plot(GRID,positive,label='Mean response to + pulse',color='#2563a5')
    ax.plot(GRID,-negative,label='Negated response to - pulse',color='#d05532',ls='--')
    ax.set(xlabel='Time (s)',ylabel='Observed x',title='B  The data still contain a useful pattern')
    ax.legend(fontsize=8,frameon=False)
    ax=axes[2]
    ax.plot(GRID,worst['truth'],label='Stored simulator trajectory',color='#2563a5')
    ax.plot(GRID,worst['prediction'],label='Committed final prediction',color='#d05532',ls='--')
    ax.set(xlabel='Time (s)',ylabel='x',title='C  Largest sealed-input failure')
    ax.legend(fontsize=8,frameon=False)
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.15)
    fig.savefig(HERE/'data_review.png',dpi=180)
    plt.close(fig)


if __name__=='__main__': main()
