"""Shared representation grammar, numerical fitting and predictive diagnostics."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import savgol_filter

TAUS = np.array([0.25, 0.5, 1.0, 2.0, 4.0, 8.0])
LAGS = np.array([0.25, 0.5, 1.0, 2.0])
FREQS = np.array([0.4, 0.8, 1.6])
DESCRIPTIONS = {
    "state": "Current x, input u, and intercept; no additional state.",
    "state_cubic": "Add x squared and x cubed for nonlinear instantaneous response.",
    "memory_fast": "Add exponentially accumulated past x and u, timescales 0.25, 0.5, 1 s.",
    "memory_slow": "Add exponentially accumulated past x and u, timescales 2, 4, 8 s.",
    "memory_multiscale": "Combine fast and slow accumulated history.",
    "saturating_memory": "Add nonlinear current state and saturating transforms of accumulated history.",
    "delay": "Add x and u from 0.25, 0.5, 1 and 2 s in the past.",
    "clock": "Add sin/cos functions of elapsed time, frequencies 0.4, 0.8, 1.6 rad/s.",
    "memory_clock": "Combine accumulated history with elapsed-time periodic forcing.",
    "nonlinear_delay": "Combine nonlinear instantaneous response, lags and accumulated history.",
    "history_all": "Regularized model containing all available history, nonlinear and clock features.",
}


def feature_indices(rep: str) -> np.ndarray:
    if rep not in DESCRIPTIONS:
        raise ValueError(rep)
    # Full feature vector: [1,x,u,x²,x³,mx(6),mu(6),tanh(mx)(6),lagx(4),lagu(4),sin(3),cos(3)].
    base = [0, 1, 2]
    mx, mu, sat = list(range(5, 11)), list(range(11, 17)), list(range(17, 23))
    lag, clock = list(range(23, 31)), list(range(31, 37))
    if rep == "state_cubic": base += [3, 4]
    elif rep == "memory_fast": base += mx[:3] + mu[:3]
    elif rep == "memory_slow": base += mx[3:] + mu[3:]
    elif rep == "memory_multiscale": base += mx + mu
    elif rep == "saturating_memory": base += [3, 4] + mx + mu + sat
    elif rep == "delay": base += lag
    elif rep == "clock": base += clock
    elif rep == "memory_clock": base += mx + mu + clock
    elif rep == "nonlinear_delay": base += [3, 4] + mx + mu + lag
    elif rep == "history_all": base = list(range(37))
    return np.asarray(base, dtype=int)


def all_features(t, x, u):
    n, dt = len(t), float(t[1] - t[0])
    mx, mu = np.zeros((n, len(TAUS))), np.zeros((n, len(TAUS)))
    decay = np.exp(-dt / TAUS)
    for i in range(1, n):
        mx[i] = decay * mx[i - 1] + (1 - decay) * x[i - 1]
        mu[i] = decay * mu[i - 1] + (1 - decay) * u[i - 1]
    lagx = np.column_stack([np.interp(t - lag, t, x, left=0.0) for lag in LAGS])
    lagu = np.column_stack([np.interp(t - lag, t, u, left=0.0) for lag in LAGS])
    return np.column_stack((np.ones(n), x, u, x*x, x*x*x, mx, mu, np.tanh(mx), lagx, lagu, np.sin(t[:, None]*FREQS), np.cos(t[:, None]*FREQS)))


def training_arrays(obs, rep):
    blocks = []
    for o in obs:
        dt = float(o.t[1] - o.t[0])
        smooth = savgol_filter(o.y, 9, 3)
        derivative = savgol_filter(o.y, 9, 3, deriv=1, delta=dt)
        features = all_features(o.t, smooth, o.u)[:, feature_indices(rep)]
        mask = np.ones(len(o.t), dtype=bool)
        mask[:5] = mask[-5:] = False
        # Exclude smoothing windows crossing input jumps.
        for i in np.flatnonzero(np.abs(np.diff(o.u)) > 0.15) + 1:
            mask[max(0, i - 4):min(len(mask), i + 5)] = False
        blocks.append((features[mask], derivative[mask]))
    return blocks


@dataclass
class Model:
    representation: str
    coefficients: np.ndarray
    ridge: float
    cv_nmse: float = float("nan")

    def rollout(self, t, u):
        x = np.zeros(len(t))
        dt = float(t[1] - t[0])
        decay = np.exp(-dt / TAUS)
        mx, mu = np.zeros(len(TAUS)), np.zeros(len(TAUS))
        ix = feature_indices(self.representation)
        for i in range(len(t) - 1):
            lagx = np.array([np.interp(t[i] - lag, t[:i+1], x[:i+1], left=0.0) for lag in LAGS])
            lagu = np.array([np.interp(t[i] - lag, t, u, left=0.0) for lag in LAGS])
            row = np.concatenate(([1, x[i], u[i], x[i]**2, x[i]**3], mx, mu, np.tanh(mx), lagx, lagu, np.sin(t[i]*FREQS), np.cos(t[i]*FREQS)))
            rate = float(row[ix] @ self.coefficients)
            value = x[i] + dt * rate
            if not np.isfinite(value) or abs(value) > 20:
                x[i+1:] = 20.0 if value > 0 else -20.0
                break
            x[i+1] = value
            mx = decay * mx + (1 - decay) * x[i]
            mu = decay * mu + (1 - decay) * u[i]
        return x

    def public(self):
        return {"representation": self.representation, "ridge": self.ridge, "cv_nmse": self.cv_nmse, "coefficients": self.coefficients.round(7).tolist()}


def solve(blocks, ridge):
    x = np.vstack([b[0] for b in blocks])
    y = np.concatenate([b[1] for b in blocks])
    scale = np.maximum(np.std(x, axis=0), 1e-4)
    scale[0] = 1.0
    xs = x / scale
    penalty = np.eye(x.shape[1]) * ridge * len(x)
    penalty[0, 0] = 1e-9
    return np.linalg.solve(xs.T @ xs + penalty, xs.T @ y) / scale


def fit(obs, rep, validate=True):
    blocks = training_arrays(obs, rep)
    lambdas = [1e-5, 1e-3, 0.1]
    derivative_scores = []
    # Independent trajectories, rather than random time rows, define folds.
    for ridge in lambdas:
        errs = []
        if validate and len(obs) > 1:
            for j, (x, y) in enumerate(blocks):
                coef = solve([b for k, b in enumerate(blocks) if k != j], ridge)
                errs.append(float(np.mean((x @ coef - y)**2)))
        derivative_scores.append(float(np.mean(errs)) if errs else 0.0)
    ridge = lambdas[int(np.argmin(derivative_scores))]
    model = Model(rep, solve(blocks, ridge), ridge)
    if validate and len(obs) > 1:
        errors = []
        for j, o in enumerate(obs):
            m = Model(rep, solve([b for k, b in enumerate(blocks) if k != j], ridge), ridge)
            pred = m.rollout(o.t, o.u)
            errors.append(float(np.mean((pred - o.y)**2) / max(float(np.var(o.y)), 0.02)))
        model.cv_nmse = float(np.mean(errors))
    return model


def diagnostics(model, obs):
    errors, residuals = [], []
    for o in obs:
        pred = model.rollout(o.t, o.u)
        residual = o.y - pred
        residuals.append(residual)
        errors.append({"action": o.action, "nmse": round(float(np.mean(residual**2) / max(float(np.var(o.y)), 0.02)), 6)})
    residuals = np.concatenate(residuals)
    corr = float(np.corrcoef(residuals[1:], residuals[:-1])[0, 1]) if np.std(residuals) > 1e-9 else 0.0
    return {"representation": model.representation, "leave_trajectory_out_nmse": round(model.cv_nmse, 6), "residual_lag1_correlation": round(corr, 5), "fit_errors": errors}


def select_cv(obs, candidates=None):
    models = [fit(obs, rep) for rep in (candidates or list(DESCRIPTIONS))]
    return min(models, key=lambda m: m.cv_nmse), models


def disagreement_action(obs, models, actions, control_fn):
    if len(models) < 2:
        return actions[0]
    ordered = sorted(models, key=lambda m: m.cv_nmse)
    best = ordered[0].cv_nmse
    plausible = [m for m in ordered if m.cv_nmse <= max(best * 3, best + 0.03)][:4]
    if len(plausible) < 2:
        plausible = ordered[:2]
    scores = []
    t = obs[0].t
    for action in actions:
        u = control_fn(action, t)
        preds = np.array([m.rollout(t, u) for m in plausible])
        scores.append(float(np.mean(np.var(np.clip(preds, -5, 5), axis=0))))
    return actions[int(np.argmax(scores))]
