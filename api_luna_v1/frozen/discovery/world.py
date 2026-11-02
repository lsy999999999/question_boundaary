"""Private evaluator. The language model receives only public observations."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

TRAIN_ACTIONS = (
    "positive_pulse", "negative_pulse", "step_rest", "double_pulse",
    "alternating", "ramp_reverse", "slow_wave", "prbs",
)
INITIAL_ACTIONS = TRAIN_ACTIONS[:3]
TEST_ACTIONS = (
    "test_chirp", "test_three_step", "test_short_pulses",
    "test_biased_wave", "test_prbs", "test_relaxation",
)
FAMILIES = (
    "linear", "cubic", "memory", "two_memory", "delay", "clock",
    "saturated_memory", "memory_clock",
)
DEV_FAMILIES = ("linear", "cubic", "memory", "clock")


def seed_for(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:4], "big")


@dataclass(frozen=True)
class Task:
    task_id: str
    split: str
    family: str
    seed: int
    params: dict


@dataclass
class Observation:
    action: str
    t: np.ndarray
    u: np.ndarray
    y: np.ndarray
    repeat: int = 0

    def public_summary(self) -> dict:
        ix = np.linspace(0, len(self.t) - 1, 13, dtype=int)
        return {
            "action": self.action, "repeat": self.repeat,
            "samples_t_u_x": np.round(np.column_stack((self.t[ix], self.u[ix], self.y[ix])), 4).tolist(),
            "observed_range": [round(float(self.y.min()), 4), round(float(self.y.max()), 4)],
        }


def make_task(split: str, family: str, seed: int) -> Task:
    if family not in FAMILIES:
        raise ValueError(family)
    rng = np.random.default_rng(seed_for("task-v1", split, family, seed))
    a = float(rng.uniform(0.65, 1.35))
    c = float(rng.uniform(0.25, 1.1))
    p = {
        "a": a, "c": c, "gain": float(rng.uniform(0.25, 0.65)),
        "c_fast": float(rng.uniform(1.4, 2.6)),
        "c_slow": float(rng.uniform(0.16, 0.35)),
        "delay": float(rng.uniform(0.45, 1.7)),
        "cubic": float(rng.uniform(0.35, 0.85)),
        "clock_amp": float(rng.uniform(0.18, 0.4)),
        "clock_freq": float(rng.choice([0.4, 0.8, 1.6])),
        "clock_phase": float(rng.uniform(-np.pi, np.pi)),
    }
    task_id = hashlib.sha256(f"{split}:{family}:{seed}:v1".encode()).hexdigest()[:12]
    return Task(task_id, split, family, seed, p)


def catalog(split: str, seeds: list[int]) -> list[Task]:
    families = DEV_FAMILIES if split == "dev" else FAMILIES
    return [make_task(split, family, seed) for family in families for seed in seeds]


def control(action: str, t: np.ndarray) -> np.ndarray:
    u = np.zeros_like(t)
    if action == "positive_pulse":
        u[(t >= 0.5) & (t < 3.5)] = 1.0
    elif action == "negative_pulse":
        u[(t >= 1) & (t < 4)] = -1.0
    elif action == "step_rest":
        u[(t >= 0.5) & (t < 7)] = 0.65
    elif action == "double_pulse":
        u[(t >= 0.5) & (t < 2.0)] = 1.2
        u[(t >= 5) & (t < 6.5)] = 1.2
    elif action == "alternating":
        u = np.where((t >= 0.5) & (t < 10), np.sign(np.sin(2.1 * t)), 0.0)
    elif action == "ramp_reverse":
        u = np.interp(t, [0, 1, 4, 7, 10, 12], [0, 0, 1.2, -1.2, 0, 0])
    elif action == "slow_wave":
        u = 0.9 * np.sin(0.7 * t) * (t >= 0.5)
    elif action in ("prbs", "test_prbs"):
        rng = np.random.default_rng(seed_for("input", action))
        period = 0.8 if action == "prbs" else 1.1
        values = rng.choice([-1.1, -0.4, 0.4, 1.1], int(t[-1] / period) + 2)
        u = values[np.minimum((t / period).astype(int), len(values) - 1)] * (t >= 0.5)
    elif action == "test_chirp":
        u = 0.85 * np.sin(0.35 * t + 0.16 * t * t)
    elif action == "test_three_step":
        u = np.select([t < 1, t < 4, t < 8, t < 10], [0, 1.35, -0.75, 0.45], 0)
    elif action == "test_short_pulses":
        u = np.where(((t > 1) & (t < 1.6)) | ((t > 4) & (t < 4.6)) | ((t > 8) & (t < 8.6)), 1.5, 0.0)
    elif action == "test_biased_wave":
        u = 0.3 + 0.7 * np.sin(1.15 * t + 0.3)
    elif action == "test_relaxation":
        u = np.where((t > 0.5) & (t < 2.5), -1.4, 0.0)
    else:
        raise ValueError(action)
    return np.asarray(u, dtype=float)


class World:
    def __init__(self, task: Task, noise: float = 0.01, horizon: float = 12.0, dt: float = 0.05):
        self._task = task
        self.noise, self.horizon, self.dt = noise, horizon, dt

    @property
    def public_id(self):
        return self._task.task_id

    def _truth(self, action: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Internal integration is finer than the sampling interval. Inputs are
        # held constant within each observed interval, matching model rollouts.
        t = np.arange(round(self.horizon / self.dt) + 1) * self.dt
        u = control(action, t)
        subdivisions = 5
        h = self.dt / subdivisions
        internal_t = np.arange((len(t) - 1) * subdivisions + 1) * h
        hist = np.zeros(len(internal_t))
        state = np.zeros(3)
        p, family = self._task.params, self._task.family

        def rhs(s, now, force, delayed):
            x, z1, z2 = s
            dx = -p["a"] * x + force
            dz1 = dz2 = 0.0
            if family == "cubic":
                dx -= p["cubic"] * x**3
            if family in ("memory", "memory_clock"):
                dx += p["gain"] * p["a"] * p["c"] * z1
                dz1 = -p["c"] * z1 + x
            elif family == "two_memory":
                dx += 0.5 * p["gain"] * p["a"] * (p["c_fast"] * z1 + p["c_slow"] * z2)
                dz1, dz2 = -p["c_fast"] * z1 + x, -p["c_slow"] * z2 + x
            elif family == "delay":
                dx += p["gain"] * p["a"] * delayed
            elif family == "saturated_memory":
                dx += p["gain"] * p["a"] * p["c"] * np.tanh(z1)
                dx -= 0.15 * p["cubic"] * x**3
                dz1 = -p["c"] * z1 + x
            if family in ("clock", "memory_clock"):
                dx += p["clock_amp"] * np.sin(p["clock_freq"] * now + p["clock_phase"])
            return np.array([dx, dz1, dz2])

        for k in range(len(internal_t) - 1):
            now = internal_t[k]
            force = u[k // subdivisions]
            delayed = float(np.interp(now - p["delay"], internal_t[:k + 1], hist[:k + 1], left=0.0))
            # RK4 with the past-delay value fixed over a 0.01 s step.
            k1 = rhs(state, now, force, delayed)
            k2 = rhs(state + h * k1 / 2, now + h / 2, force, delayed)
            k3 = rhs(state + h * k2 / 2, now + h / 2, force, delayed)
            k4 = rhs(state + h * k3, now + h, force, delayed)
            state += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            hist[k + 1] = state[0]
        return t, u, hist[::subdivisions]

    def experiment(self, action: str, repeat: int = 0) -> Observation:
        if action not in TRAIN_ACTIONS:
            raise ValueError("Only training experiments are available to the agent")
        t, u, truth = self._truth(action)
        rng = np.random.default_rng(seed_for(self.public_id, action, repeat, "noise-v1"))
        return Observation(action, t, u, truth + rng.normal(0, self.noise, len(t)), repeat)

    def evaluate(self, model) -> dict:
        # This routine is called only after the final model is committed.
        rows = []
        for action in TEST_ACTIONS:
            t, u, truth = self._truth(action)
            prediction = model.rollout(t, u)
            mse = float(np.mean((prediction - truth)**2))
            scale = max(float(np.var(truth)), 0.02)
            rows.append({"action": action, "mse": mse, "nmse": mse / scale})
        return {"test_nmse": float(np.mean([r["nmse"] for r in rows])), "test_mse": float(np.mean([r["mse"] for r in rows])), "per_intervention": rows}
