"""Bounded input-history predicates. No arbitrary Python execution."""
import ast,operator
import numpy as np
from engine import GRID

FUNCTIONS={'value':1,'area':2,'abs_area':2,'peak':2,'gap':1,'jump':1}
BIN={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
CMP={ast.Gt:operator.gt,ast.GtE:operator.ge,ast.Lt:operator.lt,ast.LtE:operator.le,ast.Eq:operator.eq,ast.NotEq:operator.ne}


def parse(text):
    if not isinstance(text,str) or len(text)>240:raise ValueError('Predicate <=240 characters')
    tree=ast.parse(text,mode='eval');nodes=list(ast.walk(tree))
    if len(nodes)>90:raise ValueError('Predicate too complex')
    for n in nodes:
        if not isinstance(n,(ast.Expression,ast.Constant,ast.Call,ast.Name,ast.Load,ast.BinOp,ast.UnaryOp,ast.BoolOp,ast.Compare,ast.And,ast.Or,ast.Not,ast.USub,ast.UAdd,*BIN,*CMP)):
            raise ValueError('Unsupported predicate syntax')
        if isinstance(n,ast.Constant) and (type(n.value) not in (int,float) or not np.isfinite(n.value) or abs(n.value)>20):raise ValueError('Finite constants within [-20,20]')
        if isinstance(n,ast.Name) and n.id not in FUNCTIONS:raise ValueError('Unknown history primitive')
        if isinstance(n,ast.Call):
            if not isinstance(n.func,ast.Name) or n.func.id not in FUNCTIONS or n.keywords or len(n.args)!=FUNCTIONS[n.func.id]:raise ValueError('Invalid history call')
            if any(any(isinstance(q,(ast.Call,ast.Name)) for q in ast.walk(a)) for a in n.args):raise ValueError('Use constant time endpoints and event indices')
    return tree.body


def reversals(u):
    last_sign=0;last_value=0.;last_active=-1;out=[]
    for i,v in enumerate(u[:-1]):
        if abs(v)<=.1:continue
        sign=int(np.sign(v))
        if last_sign and sign!=last_sign:out.append(dict(gap=(i-last_active-1)*.1,jump=abs(float(v)-last_value)))
        last_sign=sign;last_value=float(v);last_active=i
    return out


def evaluate(text,u):
    u=np.asarray(u,float);events=reversals(u)
    def invoke(name,args):
        if name in ('gap','jump'):
            i=args[0]
            if int(i)!=i or not 0<=i<=5:raise ValueError('Reversal index integer0..5')
            return events[int(i)][name] if int(i)<len(events) else 0.
        if name=='value':
            t=args[0]
            if not 0<=t<=12:raise ValueError('Time within [0,12]')
            return float(u[int(round(t/.1))])
        a,b=args
        if not 0<=a<b<=12:raise ValueError('Window 0<=a<b<=12')
        # Integrate the piecewise constant sampled input exactly over arbitrary endpoints.
        w=np.maximum(0,np.minimum(GRID[1:],b)-np.maximum(GRID[:-1],a));values=u[:-1]
        if name=='area':return float(w@values)
        if name=='abs_area':return float(w@abs(values))
        return float(max(abs(values[w>0]),default=0.))
    def walk(n):
        if isinstance(n,ast.Constant):return float(n.value)
        if isinstance(n,ast.Call):return invoke(n.func.id,[walk(a) for a in n.args])
        if isinstance(n,ast.BinOp):return BIN[type(n.op)](walk(n.left),walk(n.right))
        if isinstance(n,ast.UnaryOp):
            v=walk(n.operand)
            if isinstance(n.op,ast.Not):return not v
            return -v if isinstance(n.op,ast.USub) else v
        if isinstance(n,ast.BoolOp):
            vals=[bool(walk(x)) for x in n.values];return all(vals) if isinstance(n.op,ast.And) else any(vals)
        if isinstance(n,ast.Compare):
            vals=[walk(n.left)]+[walk(c) for c in n.comparators]
            return all(CMP[type(op)](a,b) for op,a,b in zip(n.ops,vals,vals[1:]))
        raise ValueError('Invalid executable predicate')
    result=walk(parse(text))
    if type(result) is not bool:raise ValueError('Predicate must return a boolean comparison')
    return result


def label(boundary,u):
    return None if boundary['status']=='abstain' else evaluate(boundary['expression'],u)
