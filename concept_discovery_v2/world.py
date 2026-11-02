"""Private demonstration environment. Never serialized into model prompts."""
import numpy as np
from engine import GRID, control, digest

INITIAL = [
    dict(points=[[0,0],[.5,1.0],[3.0,0]]),
    dict(points=[[0,0],[1.0,-1.0],[4.0,0]]),
    dict(points=[[0,0],[.5,.6],[7.0,0]]),
]
SEALED = [
    dict(points=[[0,0],[.5,1.4],[2.0,0],[5.0,-.7],[8.0,0]]),
    dict(points=[[0,0],[1.0,.3],[3.0,1.2],[6.0,-1.0],[9.0,0]]),
    dict(points=[[0,-.5],[2.0,.8],[5.0,-.8],[9.0,.5]]),
    dict(points=[[0,0],[.5,-1.4],[2.5,0],[6.0,1.4],[8.0,0]]),
    dict(points=[[0,.5],[2.5,1.0],[5.0,.5],[7.5,-.5],[10.0,0]]),
    dict(points=[[0,0],[1.0,1.5],[2.0,0],[4.0,1.5],[5.0,0],[8.0,-1.0],[9.0,0]]),
]


def truth(action):
    # One hidden relaxing quantity with saturating influence; known to the
    # experiment designer, not given as a candidate/equation to Luna.
    u = control(action)
    x = np.zeros(len(GRID))
    z = 0.0
    for k in range(len(GRID)-1):
        visible = x[k]
        for _ in range(10):
            dx = -.85*visible + u[k] + .65*np.tanh(1.8*z)
            dz = .45*(visible-z)
            visible, z = visible+.01*dx, z+.01*dz
        x[k+1] = visible
    return x


def observe(action, identifier):
    clean = truth(action)
    seed = int(digest(dict(action=action, id=identifier))[:8],16)
    measured = clean + np.random.default_rng(seed).normal(0,.005,len(GRID))
    return dict(id=identifier, action=action, t=GRID.tolist(),
                u=control(action).tolist(), x=measured.tolist())
