"""Restricted, model-authored dynamical hypotheses and numerical execution."""
from __future__ import annotations
import ast
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.signal import savgol_filter

GRID = np.arange(121, dtype=float) * .1
FUNCS = {'tanh': np.tanh, 'sin': np.sin, 'cos': np.cos, 'abs': np.abs}


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
    with path.open('x') as f:
        f.write(data)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def expression(source, names):
    if not isinstance(source, str) or len(source) > 180:
        raise ValueError('Expression must be at most 180 characters')
    tree = ast.parse(source, mode='eval')
    nodes = list(ast.walk(tree))
    if len(nodes) > 70:
        raise ValueError('Expression too complex')
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load,
               ast.Constant, ast.Call, ast.Add, ast.Sub, ast.Mult, ast.Div,
               ast.Pow, ast.USub, ast.UAdd)
    for node in nodes:
        if not isinstance(node, allowed):
            raise ValueError('Unsupported expression syntax')
        if isinstance(node, ast.Name) and node.id not in names | set(FUNCS):
            raise ValueError('Unknown symbol: ' + node.id)
        if isinstance(node, ast.Constant) and (type(node.value) not in (int, float)
                or not np.isfinite(node.value) or abs(node.value) > 10):
            raise ValueError('Constants must be finite numbers within [-10,10]')
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            if not isinstance(node.right, ast.Constant) or node.right.value not in (2, 3):
                raise ValueError('Only literal powers 2 and 3 allowed')
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name)
                or node.func.id not in FUNCS or len(node.args) != 1 or node.keywords):
            raise ValueError('Only unary tanh/sin/cos/abs calls allowed')
    code = compile(tree, '<hypothesis>', 'eval')
    fn = lambda env: eval(code, {'__builtins__': {}, **FUNCS}, env)
    try:
        probe = float(fn({name:.3 for name in names}))
        if not np.isfinite(probe):
            raise ValueError('Nonfinite expression')
    except (ValueError, TypeError, ArithmeticError) as exc:
        raise ValueError('Expression must evaluate to a finite numeric value') from exc
    return fn


class Spec:
    def __init__(self, raw):
        self.raw = raw
        self.params = raw['parameters']
        self.states = raw['states']
        self.terms = raw['terms']
        if not (0 <= len(self.params) <= 3 and 0 <= len(self.states) <= 2
                and 1 <= len(self.terms) <= 8):
            raise ValueError('Limits: three parameters, two states, eight derivative terms')
        self.names = {'x', 'u', 't'} | {f'z{i}' for i in range(len(self.states))}
        for i, p in enumerate(self.params):
            if p['name'] != f'p{i}':
                raise ValueError('Parameter names must be p0,p1,p2 in order')
            if not (.02 <= p['lower'] < p['initial'] < p['upper'] <= 4):
                raise ValueError('Require .02 <= lower < initial < upper <= 4')
            self.names.add(p['name'])
        for i, state in enumerate(self.states):
            if state['name'] != f'z{i}' or not isinstance(state.get('meaning'), str):
                raise ValueError('States require ordered names z0,z1 and meaning')
        self.rates = [expression(s['rate'], self.names) for s in self.states]
        self.features = [expression(s, self.names) for s in self.terms]
        self.complexity = sum(len(list(ast.walk(ast.parse(s, mode='eval'))))
                              for s in self.terms + [s['rate'] for s in self.states])

    def env(self, x, u, t, z, p):
        return dict(x=x, u=u, t=t, **{f'z{i}': v for i, v in enumerate(z)},
                    **{f'p{i}': v for i, v in enumerate(p)})

    def features_observed(self, o, p):
        x = savgol_filter(o['x'], 9, 3)
        u, t = np.asarray(o['u']), np.asarray(o['t'])
        z = np.zeros((len(self.states), len(t)))
        with np.errstate(all='ignore'):
            for k in range(len(t)-1):
                env = self.env(x[k], u[k], t[k], z[:, k], p)
                dz = np.asarray([f(env) for f in self.rates], dtype=float)
                z[:, k+1] = z[:, k] + .1 * dz
                if not np.all(np.isfinite(z[:, k+1])) or np.max(np.abs(z[:, k+1]), initial=0) > 30:
                    raise ValueError('Unstable latent state')
            env = self.env(x, u, t, z, p)
            columns = [np.broadcast_to(np.asarray(f(env), dtype=float), x.shape)
                       for f in self.features]
            a = np.column_stack(columns)
        if not np.isfinite(a).all() or abs(a).max() > 1e6:
            raise ValueError('Nonfinite or explosive feature')
        derivative = savgol_filter(o['x'], 9, 3, deriv=1, delta=.1)
        mask = smooth_mask(u)
        return a[mask], derivative[mask]

    def rollout(self, p, weights, u):
        x = np.zeros(len(GRID))
        z = np.zeros(len(self.states))
        with np.errstate(all='ignore'):
            for k in range(len(GRID)-1):
                env = self.env(x[k], u[k], GRID[k], z, p)
                rate = float(np.asarray([f(env) for f in self.features]) @ weights)
                dz = np.asarray([f(env) for f in self.rates])
                x[k+1] = x[k] + .1 * rate
                z = z + .1 * dz
                if (not np.isfinite(x[k+1]) or abs(x[k+1]) > 30 or not np.isfinite(z).all()
                        or np.max(np.abs(z), initial=0) > 30):
                    raise ValueError('Unstable free rollout')
        return x


def smooth_mask(u):
    mask = np.ones(len(u), dtype=bool)
    mask[:5] = mask[-5:] = False
    for i in np.flatnonzero(np.abs(np.diff(u)) > .05)+1:
        mask[max(0, i-4):min(len(u), i+5)] = False
    return mask


def fit_core(spec, obs):
    size = sum(int(smooth_mask(o['u']).sum()) for o in obs)
    if size < 15:
        raise ValueError('Too few derivative samples after excluding input jumps')

    def solve(p):
        blocks = [spec.features_observed(o, p) for o in obs]
        a, b = np.vstack([q[0] for q in blocks]), np.concatenate([q[1] for q in blocks])
        scale = np.maximum(np.sqrt(np.mean(a*a, axis=0)), 1e-5)
        norm = a / scale
        w = np.linalg.solve(norm.T @ norm + np.eye(a.shape[1]) * len(b) * 1e-5,
                            norm.T @ b) / scale
        return w, a @ w-b

    def objective(p):
        try:
            return solve(p)[1]
        except (ValueError, ArithmeticError, TypeError, np.linalg.LinAlgError):
            return np.full(size, 1e3)

    p = np.array([v['initial'] for v in spec.params])
    if len(p):
        opt = least_squares(objective, p, bounds=([v['lower'] for v in spec.params],
            [v['upper'] for v in spec.params]), max_nfev=40, ftol=1e-5, xtol=1e-5, gtol=1e-5)
        p = opt.x
        solver = dict(success=bool(opt.success), nfev=int(opt.nfev), message=str(opt.message))
    else:
        solver = dict(success=True, nfev=0, message='No nonlinear parameters')
    weights, residual = solve(p)
    return dict(parameters=p.tolist(), coefficients=weights.tolist(), solver=solver,
                derivative_mse=float(np.mean(residual**2)))


def predict(model, u):
    return Spec(model['spec']).rollout(model['fit']['parameters'], model['fit']['coefficients'], u)


def nmse(pred, observed):
    return float(np.mean((np.asarray(pred)-observed)**2) / max(float(np.var(observed)), .02))


def fit_model(raw, obs):
    spec = Spec(raw)
    cv = []
    for i, o in enumerate(obs):
        folded = fit_core(spec, [v for j, v in enumerate(obs) if j != i])
        try:
            y = spec.rollout(folded['parameters'], folded['coefficients'], o['u'])
            cv.append(nmse(y, o['x']))
        except ValueError:
            cv.append(1e6)
    fitted = fit_core(spec, obs)
    for o in obs:
        spec.rollout(fitted['parameters'], fitted['coefficients'], o['u'])
    return dict(spec=raw, fit=fitted, trajectory_cv_nmse=float(np.mean(cv)),
                fold_nmse=cv, complexity=spec.complexity)


def validate_action(raw):
    points = raw['points']
    if not isinstance(points, list) or not 2 <= len(points) <= 7:
        raise ValueError('Input needs 2 to 7 [time,value] change points')
    prev = -1.0
    for point in points:
        if len(point) != 2 or any(type(v) not in (float, int) or not np.isfinite(v) for v in point):
            raise ValueError('Input points must be finite numbers')
        t, val = point
        if not 0 <= t <= 11 or t <= prev or not -1.5 <= val <= 1.5:
            raise ValueError('Ordered times in [0,11]; amplitudes in [-1.5,1.5]')
        if prev >= 0 and t-prev < .5:
            raise ValueError('At least .5s between changes')
        if abs(t*10-round(t*10)) > 1e-6:
            raise ValueError('Times must be on the .1s grid')
        prev = t
    if points[0][0] != 0:
        raise ValueError('First change point must be time zero')
    return raw


def control(action):
    validate_action(action)
    u = np.zeros(len(GRID))
    for t, val in action['points']:
        u[GRID >= t-1e-9] = val
    return u


def summary(o):
    ix = np.arange(0, len(GRID), 5)
    return dict(id=o['id'], input=o['action'],
                samples_t_u_x=np.round(np.column_stack([GRID[ix], np.asarray(o['u'])[ix],
                    np.asarray(o['x'])[ix]]), 5).tolist())


def collisions(obs):
    rows = []
    for o in obs:
        smooth = savgol_filter(o['x'], 9, 3)
        deriv = savgol_filter(o['x'], 9, 3, deriv=1, delta=.1)
        mask = smooth_mask(o['u'])
        for i in np.flatnonzero(mask):
            rows.append((o['id'], i, float(smooth[i]), float(o['u'][i]), float(deriv[i])))
    if not rows:
        return []
    # Correct the small allowed x mismatch using a visible-state linear fit.
    # Without this, even duplicate noiseless linear trajectories create false
    # witnesses merely because nearby x values have slightly different slopes.
    features = np.array([[1,r[2],r[3]] for r in rows])
    rates = np.array([r[4] for r in rows])
    weights = np.linalg.lstsq(features,rates,rcond=None)[0]
    residuals = rates-features@weights
    candidates = []
    for i, a in enumerate(rows):
        for j in range(i+1,len(rows)):
            b=rows[j]
            if a[0] == b[0] or abs(a[2]-b[2]) > .035 or abs(a[3]-b[3]) > .001:
                continue
            delta = abs(residuals[i]-residuals[j])
            if delta < .03:
                continue
            candidates.append((delta, a, b))
    found, pairs = [], set()
    for delta, a, b in sorted(candidates, reverse=True):
        pair = tuple(sorted((a[0], b[0])))
        if pair in pairs:
            continue
        pairs.add(pair)
        found.append(dict(id='witness_'+str(len(found)),
            a=dict(observation=a[0], time=float(a[1]*.1), x=a[2], u=a[3], dx=a[4]),
            b=dict(observation=b[0], time=float(b[1]*.1), x=b[2], u=b[3], dx=b[4]),
            absolute_derivative_difference=abs(a[4]-b[4]),
            visible_linear_corrected_difference=float(delta),
            visible_linear_correction_coefficients=weights.tolist(),
            caution='Approximate matching, smoothed noisy derivative; not proof of a missing state.'))
        if len(found) == 4:
            break
    return found
