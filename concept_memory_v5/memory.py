"""Executable local relationships. Historical support is immutable evidence."""
import itertools
import numpy as np
from scipy.stats import chi2
from engine import GRID, digest
from numerics import predict, input_key
from temporal import validate_scope, label


def fit_version(model):
    return digest(dict(spec=model['spec'], fit=model['fit']))


def observation_hash(o):
    return digest({k:o[k] for k in ('id', 'action', 't', 'u', 'x', 'noise_std')})


def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x, float)**2)))


def noise_limit(sigma, n):
    return float(sigma * np.sqrt(chi2.ppf(.99, n) / n)) if sigma else 1e-10


def relation(a, b, window=(0., 12.), source='observed_local_relation'):
    if any(not np.isfinite(o['noise_std']) or o['noise_std']<0 for o in (a,b)):
        raise ValueError('Nonnegative finite measurement noise required')
    if not (len(window)==2 and 0<=window[0]<=window[1]<=12):
        raise ValueError('Window within observed horizon required')
    if a['id'] == b['id'] or not np.allclose(a['u'], -np.asarray(b['u']), rtol=0, atol=1e-12):
        raise ValueError('Two distinct sign-reversed input records required')
    if not (np.array_equal(a['t'], GRID) and np.array_equal(b['t'], GRID)):
        raise ValueError('Aligned time grid required')
    if any(np.asarray(o['x']).shape!=GRID.shape or not np.isfinite(o['x']).all() for o in (a,b)):
        raise ValueError('Finite aligned measurement trajectories required')
    mask = (GRID >= window[0]) & (GRID <= window[1])
    if not mask.any():
        raise ValueError('Empty relationship window')
    sigma = float(np.hypot(a['noise_std'], b['noise_std']))
    residual = (np.asarray(a['x']) + b['x'])[mask]
    threshold = noise_limit(sigma, int(mask.sum()))
    data = dict(kind='local_sign_reversal', observation_ids=[a['id'], b['id']],
                observation_hashes=[observation_hash(a), observation_hash(b)],
                window=list(window), source=source)
    return dict(id='relation:' + digest(data)[:20], **data,
        claim_status='observed_local_support' if rms(residual) <= threshold else 'observed_counterexample',
        input_scope=dict(kind='exact_recorded_pair', actions=[a['action'], b['action']],
                         input_hashes=[digest(a['u']), digest(b['u'])], reset='zero'),
        noise=dict(std_by_observation=[a['noise_std'], b['noise_std']], pair_std=sigma,
                   assumption='independent Gaussian samples and independent deterministic-reset trials',
                   test='chi-square upper .99 per relationship; no multiple-test correction'),
        metric=dict(name='RMS(x_a+x_b)', value=rms(residual), threshold=threshold,
                    sample_count=int(mask.sum()), residual=residual.tolist()),
        model_binding=None, forecast_binding=None,
        interpretation='Local relationship on this pair/window, not a universal law')


def discover(obs):
    # First record per exact input, deterministic input ordering; no cherry-picked repeats.
    groups = {}
    for o in obs:
        groups.setdefault(input_key(o), o)
    found = []
    for a, b in itertools.combinations(groups.values(), 2):
        if np.any(np.abs(a['u']) > 1e-12) and np.allclose(a['u'], -np.asarray(b['u']), rtol=0, atol=1e-12):
            found.append(relation(a, b))
    return found


def check(model_id, model, rel, byid, forecast=None):
    obs = [byid[i] for i in rel['observation_ids']]
    if [observation_hash(o) for o in obs] != rel['observation_hashes']:
        raise ValueError('Observation content changed')
    mask = (GRID >= rel['window'][0]) & (GRID <= rel['window'][1])
    ys = [predict(model, o['u']).tolist() for o in obs]
    predicted = (np.asarray(ys[0]) + ys[1])[mask]
    actual = np.asarray(rel['metric']['residual'])
    limit = rel['metric']['threshold']
    conflict = rel['claim_status'] == 'observed_local_support' and rms(predicted) > limit
    record = dict(relation_id=rel['id'], model_id=model_id, fit_version=fit_version(model),
        prediction_origin='posthoc_original_input_replay', forecast_binding=forecast,
        observation_ids=rel['observation_ids'], observation_hashes=rel['observation_hashes'],
        window=rel['window'], predictions=ys, predicted_relation_rms=rms(predicted),
        observed_relation_rms=rel['metric']['value'], discrepancy_rms=rms(predicted-actual),
        noise_upper=limit, conflict=bool(conflict),
        relation_fit_compatible=bool(rms(predicted-actual) <= limit))
    record['id'] = 'regression:' + digest(record)[:20]
    return record


def review(models, relations, obs):
    byid = {o['id']:o for o in obs}; out = []
    for key, model in models.items():
        for rel in relations:
            try:
                out.append(check(key, model, rel, byid))
            except (ValueError, ArithmeticError, TypeError) as exc:
                out.append(dict(id='regression_failure:'+key+':'+rel['id'], model_id=key,
                    fit_version=fit_version(model), relation_id=rel['id'], conflict=None,
                    numerical_error=str(exc)))
    return out


def validate_resolutions(value, model_id, model, checks, relations, obs):
    relevant = [c for c in checks if c['model_id'] == model_id and c.get('conflict') is True]
    required = {c['relation_id'] for c in relevant}
    items = value['resolutions']
    if len(items) != len({x['relation_id'] for x in items}) or {x['relation_id'] for x in items} != required:
        raise ValueError('Address every current conflict exactly once')
    for item in items:
        if item['fit_version'] != fit_version(model):
            raise ValueError('Resolution cites stale fit')
        if not isinstance(item['reason'], str) or not item['reason']:
            raise ValueError('Explain treatment of old success')
        if item['action'] not in ('withdraw_candidate', 'narrow_claim', 'test_conflict'):
            raise ValueError('Choose withdraw_candidate/narrow_claim/test_conflict')
        if item['action'] == 'narrow_claim':
            validate_scope(item['scope'])
            labels = [label(item['scope'], o['u']) for o in obs]
            if not any(labels) or all(labels):
                raise ValueError('Proposed narrower scope must split observed inputs')
            if item.get('status') != 'hypothesis_pending_test':
                raise ValueError('Narrowing is a hypothesis, not resolved evidence')
        if item['action'] == 'test_conflict':
            if item.get('status') != 'hypothesis_pending_test':
                raise ValueError('Experiment must remain pending until actually observed')
            a = item['experiment']
            from engine import control
            us = [control(x) for x in a]
            if len(us) != 2 or not np.allclose(us[0], -us[1], rtol=0, atol=1e-12):
                raise ValueError('Conflict test needs a mirror input pair')
            if rms(predict(model, us[0]) + predict(model, us[1])) < 3 * .005 * np.sqrt(2):
                raise ValueError('Test does not distinguish candidate from mirror extension')
    return True


def extension_record(parent, new_relation, forecast_commit):
    """A fresh pair tests an extension, never rewrites the old observation."""
    rec = dict(parent_relation_id=parent['id'], new_relation_id=new_relation['id'],
        forecast_commit=forecast_commit, old_local_status=parent['claim_status'],
        extension_status=('counterexample_to_extension' if new_relation['claim_status'] == 'observed_counterexample'
                          else 'supported_on_new_pair'),
        retained_original_scope=parent['input_scope'])
    rec['id'] = 'extension:' + digest(rec)[:20]
    return rec
