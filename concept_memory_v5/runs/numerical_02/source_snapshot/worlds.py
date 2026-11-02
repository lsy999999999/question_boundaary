"""Designer-known synthetic systems. Never include this module in model prompts."""
import numpy as np
from engine import GRID, control, digest

ACTIVATION = '((abs(u)-0.8+abs(abs(u)-0.8))/2)**2'


def configuration(family, seed):
    if family not in ('linear_memory', 'saturated_memory', 'local_symmetry_only'):
        raise ValueError('Unknown fixture family')
    rng = np.random.default_rng(seed)
    return dict(family=family, seed=seed, decay=float(rng.uniform(.75,1.1)),
                drive=float(rng.uniform(.8,1.1)), memory=float(rng.uniform(.2,.4)),
                relaxation=float(rng.uniform(.4,.8)), even=float(rng.uniform(.8,1.3)))


def truth(config, action):
    u = control(action); x = np.zeros(len(GRID)); z = 0.
    for k in range(len(GRID)-1):
        memory = np.tanh(z) if config['family']=='saturated_memory' else z
        even = config['even'] * max(abs(u[k])-.8,0.)**2 if config['family']=='local_symmetry_only' else 0.
        x[k+1] = x[k] + .1*(-config['decay']*x[k]+config['drive']*u[k]+config['memory']*memory+even)
        z += .1*(u[k]-config['relaxation']*z)
    return x


def observe(config, action, identifier):
    y = truth(config, action)
    seed = int(digest(dict(world=config, action=action, id=identifier))[:16],16)
    return dict(id=identifier, action=action, t=GRID.tolist(), u=control(action).tolist(),
        x=(y+np.random.default_rng(seed).normal(0,.005,len(GRID))).tolist(), noise_std=.005,
        origin='new_synthetic_system')


def designer_model(config, include_even=True):
    """Oracle fixture used ONLY to test infrastructure; never an agent proposal."""
    terms=['x','u','tanh(z0)' if config['family']=='saturated_memory' else 'z0']
    coefficients=[-config['decay'],config['drive'],config['memory']]
    if config['family']=='local_symmetry_only' and include_even:
        terms.append(ACTIVATION);coefficients.append(config['even'])
    return dict(spec=dict(parameters=[dict(name='p0',lower=.02,initial=.5,upper=4.)],
        states=[dict(name='z0',meaning='Designer fixture input trace',rate='u-p0*z0')],terms=terms),
        fit=dict(parameters=[config['relaxation']],coefficients=coefficients),
        origin='designer_oracle_fixture')


def mirror_pair(amplitude, end=3.5):
    return [dict(points=[[0,0],[.5,float(s*amplitude)],[float(end),0]]) for s in (1,-1)]
