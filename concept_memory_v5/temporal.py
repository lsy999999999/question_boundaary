"""Bounded JSON temporal expressions over known input schedules, without eval."""
import numpy as np
from engine import GRID

SCHEMA = {
    'signals': ['u', 't'],
    'unary': ['abs', 'neg', 'not', 'integral', 'duration', 'run'],
    'binary': ['add', 'sub', 'mul', 'div', 'gt', 'lt', 'ge', 'le', 'and', 'or'],
    'history': ['lag', 'mean', 'max', 'min'],
    'reducers': ['any', 'all', 'last'],
    'limits': {'nodes': 80, 'depth': 12, 'steps': [1, 120], 'constant_abs': 120},
    'semantics': 'dt=.1; lag pads with first sample; windows include present; '
                 'integral/duration sum completed intervals, excluding present; '
                 'run counts consecutive true samples ending now times dt. '
                 'Only u and t, no measured x. Boolean final expression required.'}


def validate(tree):
    count = 0
    def visit(n, depth):
        nonlocal count
        count += 1
        if count > 80 or depth > 12:
            raise ValueError('Temporal expression too complex')
        if type(n) in (int, float):
            if not np.isfinite(n) or abs(n) > 120:
                raise ValueError('Finite constant within [-120,120] required')
            return 'number'
        if not isinstance(n, dict):
            raise ValueError('Expression must be JSON tree')
        if set(n) == {'signal'}:
            if n['signal'] not in SCHEMA['signals']:
                raise ValueError('Only planned u and t signals are available')
            return 'number'
        op = n.get('op')
        keys = {'op', 'args', 'steps'} if op in SCHEMA['history'] else {'op', 'args'}
        if set(n) != keys or not isinstance(n['args'], list):
            raise ValueError('Exact operator fields required')
        arity = 2 if op in SCHEMA['binary'] else 1
        if op not in SCHEMA['unary'] + SCHEMA['binary'] + SCHEMA['history']:
            raise ValueError('Unknown temporal operation')
        if len(n['args']) != arity:
            raise ValueError('Wrong arity')
        types = [visit(a, depth + 1) for a in n['args']]
        boolean_ops = ('not', 'and', 'or', 'duration', 'run')
        expected = 'bool' if op in boolean_ops else 'number'
        if op == 'lag':
            expected = types[0]
        if any(t != expected for t in types):
            raise ValueError('Temporal type mismatch')
        if op in SCHEMA['history']:
            if type(n['steps']) is not int or not 1 <= n['steps'] <= 120:
                raise ValueError('Only positive bounded history steps')
        if op in ('gt', 'lt', 'ge', 'le', 'and', 'or', 'not'):
            return 'bool'
        return types[0] if op == 'lag' else 'number'
    return visit(tree, 0)


def series(tree, u):
    validate(tree)
    u = np.asarray(u, float)
    if u.ndim != 1 or not 1 <= len(u) <= len(GRID) or not np.isfinite(u).all():
        raise ValueError('Finite input prefix required')
    def go(n):
        if type(n) in (int, float):
            return np.full(len(u), float(n))
        if 'signal' in n:
            return u.copy() if n['signal'] == 'u' else GRID[:len(u)].copy()
        op = n['op']; a = [go(v) for v in n['args']]
        binary = {'add': np.add, 'sub': np.subtract, 'mul': np.multiply,
                  'gt': np.greater, 'lt': np.less, 'ge': np.greater_equal,
                  'le': np.less_equal, 'and': np.logical_and, 'or': np.logical_or}
        if op in binary:
            return binary[op](*a)
        if op == 'div':
            if np.any(np.abs(a[1]) < 1e-10):
                raise ValueError('Temporal division by zero')
            return a[0] / a[1]
        if op in ('abs', 'neg', 'not'):
            return {'abs': np.abs, 'neg': np.negative, 'not': np.logical_not}[op](a[0])
        if op in ('integral', 'duration'):
            return np.r_[0., np.cumsum(a[0][:-1].astype(float)) * .1]
        if op == 'run':
            result = np.zeros(len(u)); current = 0
            for i, v in enumerate(a[0]):
                current = current + 1 if v else 0; result[i] = current * .1
            return result
        steps = n['steps']
        if op == 'lag':
            return a[0][np.maximum(np.arange(len(u)) - steps, 0)]
        fn = {'mean': np.mean, 'max': np.max, 'min': np.min}[op]
        return np.asarray([fn(a[0][max(0, i-steps+1):i+1]) for i in range(len(u))])
    with np.errstate(over='raise', invalid='raise', divide='raise'):
        try:
            result = go(tree)
        except FloatingPointError as exc:
            raise ValueError('Nonfinite temporal expression') from exc
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite temporal expression')
    return result


def validate_scope(scope):
    if set(scope) != {'expression', 'reduce'} or scope['reduce'] not in SCHEMA['reducers']:
        raise ValueError('Scope requires expression and any/all/last reduce')
    if validate(scope['expression']) != 'bool':
        raise ValueError('Scope must be Boolean')


def label(scope, u):
    validate_scope(scope)
    values = series(scope['expression'], u)
    return bool({'any': np.any, 'all': np.all, 'last': lambda x:x[-1]}[scope['reduce']](values))


def op(name, *args, **kwargs):
    """Convenience for tests and protocol fixtures, not a learned expression."""
    return dict(op=name, args=list(args), **kwargs)
