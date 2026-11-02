"""Trajectory fitting, input-group holdouts, and affine realization comparison."""
import ast
import json
from collections import defaultdict
import numpy as np
from scipy.optimize import least_squares
from scipy.signal import ss2tf, lfilter
from engine import Spec, GRID, fit_core, nmse, digest


def input_key(o):
    return tuple(np.asarray(o['u'],float).round(12))


def groups(obs):
    result=defaultdict(list)
    for o in obs: result[input_key(o)].append(o)
    return list(result.values())


def structural_key(raw):
    def norm(s):
        class Constants(ast.NodeTransformer):
            def visit_Constant(self,node):
                return ast.copy_location(ast.Constant(float(node.value)),node)
        return ast.dump(Constants().visit(ast.parse(s,mode='eval')),include_attributes=False)
    return json.dumps(dict(terms=sorted(norm(t) for t in raw['terms']),
        states=[norm(s['rate']) for s in raw['states']],
        parameters=[{k:p[k] for k in ('name','lower','upper')} for p in raw['parameters']]),sort_keys=True)


def degree(node, variables):
    if isinstance(node,ast.Expression): return degree(node.body,variables)
    if isinstance(node,ast.Constant): return 0
    if isinstance(node,ast.Name): return int(node.id in variables)
    if isinstance(node,ast.UnaryOp): return degree(node.operand,variables)
    if isinstance(node,ast.Call): return 0 if degree(node.args[0],variables)==0 else 100
    a,b=degree(node.left,variables),degree(node.right,variables)
    if isinstance(node.op,(ast.Add,ast.Sub)): return max(a,b)
    if isinstance(node.op,ast.Mult): return a+b
    if isinstance(node.op,ast.Div): return a if b==0 else 100
    if isinstance(node.op,ast.Pow): return a*node.right.value
    return 100


def is_affine(spec):
    texts=spec.terms+[s['rate'] for s in spec.states]
    if any(any(isinstance(n,ast.Name) and n.id=='t' for n in ast.walk(ast.parse(t))) for t in texts): return False
    return all(degree(ast.parse(t,mode='eval'),{'x','u','z0','z1'})<=1 for t in texts)


def affine_arrays(spec,p,coef):
    n=1+len(spec.states)
    def rates(state,u):
        env=spec.env(state[0],u,0,state[1:],p)
        return np.array([np.array([f(env) for f in spec.features])@coef]+[f(env) for f in spec.rates],float)
    zero=np.zeros(n);offset=rates(zero,0)
    A=np.column_stack([rates(np.eye(n)[i],0)-offset for i in range(n)])
    B=rates(zero,1)-offset
    return A,B,offset


def rollout(spec,p,coef,u):
    if not hasattr(spec,'_affine'): spec._affine=is_affine(spec)
    if not spec._affine: return spec.rollout(p,coef,u)
    A,B,F=affine_arrays(spec,p,coef)
    n=len(A);C=np.zeros((1,n));C[0,0]=1
    Ad=np.eye(n)+.1*A;Bd=.1*np.column_stack([B,F]);Dd=np.zeros((1,2))
    b,den=ss2tf(Ad,Bd,C,Dd,input=0)
    bf,_=ss2tf(Ad,Bd,C,Dd,input=1)
    x=lfilter(b[0],den,np.asarray(u))+lfilter(bf[0],den,np.ones(len(u)))
    if not np.isfinite(x).all() or abs(x).max()>30: raise ValueError('Unstable trajectory')
    return x


def predict(model,u):
    return rollout(Spec(model['spec']),model['fit']['parameters'],model['fit']['coefficients'],u)


def fit_trajectory(raw,obs,warm=None):
    spec=Spec(raw);np_=len(spec.params);nc=len(spec.terms)
    lo=np.array([v['lower'] for v in spec.params]+[-8.]*nc)
    hi=np.array([v['upper'] for v in spec.params]+[8.]*nc)
    support={input_key(g[0]):len(g) for g in groups(obs)}
    scales=[np.sqrt(len(o['x'])*max(float(np.var(o['x'])),.02)*support[input_key(o)]) for o in obs]
    size=sum(len(o['x']) for o in obs)
    def residual(theta):
        try:
            return np.concatenate([(rollout(spec,theta[:np_],theta[np_:],o['u'])-o['x'])/s for o,s in zip(obs,scales)])
        except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError):
            return np.full(size,100.)
    if warm is None:
        try: warm=fit_core(spec,obs)
        except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError):
            warm=dict(parameters=[p['initial'] for p in spec.params],coefficients=[0.]*nc)
    first=np.array(warm['parameters']+warm['coefficients'])
    second=first.copy()
    if np_: second[:np_]=np.sqrt(lo[:np_]*hi[:np_])
    else: second[np_:]*=.6
    attempts=[]
    for x0 in (first,second):
        x0=np.clip(x0,lo+1e-7,hi-1e-7)
        opt=least_squares(residual,x0,bounds=(lo,hi),max_nfev=35,ftol=2e-5,xtol=2e-5,gtol=2e-5)
        attempts.append(dict(theta=opt.x.tolist(),objective=float(np.sum(residual(opt.x)**2)),
            success=bool(opt.success),nfev=int(opt.nfev)))
    chosen=min(attempts,key=lambda a:a['objective']);theta=chosen['theta']
    if chosen['objective']>=1e4: raise ValueError('No executable trajectory fit from either initialization')
    for o in obs: rollout(spec,theta[:np_],theta[np_:],o['u'])
    return dict(parameters=theta[:np_],coefficients=theta[np_:],objective=chosen['objective'],
        optimizer_attempts=attempts,objective_definition='group-balanced complete observed trajectory NMSE sum')


def fit_model(raw,obs,warm=None):
    grouped=groups(obs);folds=[];failures=[]
    if len(grouped)<2: raise ValueError('Need at least two distinct input schedules')
    for group in grouped:
        train=[o for o in obs if input_key(o)!=input_key(group[0])]
        try:
            # Do not warm a holdout fit from all-data parameters: avoid carrying held-out information.
            fitted=fit_trajectory(raw,train)
            mm=dict(spec=raw,fit=fitted)
            ys=[predict(mm,o['u']) for o in group]
            scores=[nmse(y,np.array(o['x'])) for y,o in zip(ys,group)]
            folds.append(dict(ids=[o['id'] for o in group],nmse=float(np.mean(scores)),fit=fitted,
                              predictions=[y.tolist() for y in ys]))
        except (ValueError,ArithmeticError,TypeError,np.linalg.LinAlgError) as exc:
            failures.append(dict(ids=[o['id'] for o in group],error=str(exc)))
    fitted=fit_trajectory(raw,obs,warm)
    return dict(spec=raw,fit=fitted,group_cv_nmse=float(np.mean([f['nmse'] for f in folds])) if not failures else None,
        cv_folds=folds,cv_failures=failures,distinct_inputs=len(grouped))


def ranking(model):
    return model['group_cv_nmse'] if model['group_cv_nmse'] is not None else 1e9


def public(model):
    return {k:model[k] for k in ('spec','fit','group_cv_nmse','distinct_inputs','cv_failures')}


def affine_signature(model):
    """Exact rational transfer signature of the *stored decimal* affine model.

    Includes constant forcing and zero initial conditions. Nonlinear/time-dependent
    models return None, not an unproved equivalence claim.
    """
    import sympy as s
    spec=Spec(model['spec'])
    if not is_affine(spec): return None
    x,u,t=s.symbols('x u t');zs=s.symbols('z0:'+str(len(spec.states)))
    variables=[x,*zs];env={'x':x,'u':u,'t':t,'tanh':s.tanh,'sin':s.sin,'cos':s.cos,'abs':s.Abs}
    env.update({f'z{i}':z for i,z in enumerate(zs)})
    env.update({f'p{i}':s.Rational(str(v)) for i,v in enumerate(model['fit']['parameters'])})
    terms=[s.sympify(text,locals=env,rational=True) for text in spec.terms]
    dx=sum(s.Rational(str(c))*v for c,v in zip(model['fit']['coefficients'],terms))
    vector=s.Matrix([dx]+[s.sympify(q['rate'],locals=env,rational=True) for q in spec.states])
    A=vector.jacobian(variables);B=vector.diff(u);F=vector.subs({v:0 for v in variables+[u]})
    lap=s.Symbol('s');C=s.zeros(1,len(variables));C[0,0]=1
    inverse=(lap*s.eye(len(variables))-A).inv()
    return dict(input_transfer=str(s.cancel((C*inverse*B)[0])),
                constant_forcing_transfer=str(s.cancel((C*inverse*F)[0])),initial_state='zero')


def failures_for(model,obs,model_id):
    import hashlib
    fit_id=digest(dict(spec=model['spec'],fit=model['fit']))[:12]
    byid={o['id']:o for o in obs};found=[]
    for fold in model['cv_folds']:
        for identifier,pred in zip(fold['ids'],fold['predictions']):
            actual=np.array(byid[identifier]['x']);err=np.array(pred)-actual
            windows=np.convolve(err**2,np.ones(6)/6,mode='valid');start=int(np.argmax(windows))
            ix=list(range(start,start+6))
            found.append(dict(id='failure:'+model_id+':'+fit_id+':'+identifier,kind='group_held_out_trajectory',owner_model_id=model_id,fit_version=fit_id,observation=identifier,
                rmse=float(np.sqrt(windows[start])),samples_t_u_observed_predicted=[
                    [float(GRID[i]),byid[identifier]['u'][i],float(actual[i]),float(pred[i])] for i in ix]))
    return sorted(found,key=lambda a:a['rmse'],reverse=True)[:3]


def validate_evidence_ownership(update,evidence):
    by_id={e['id']:e for e in evidence}
    for identifier in update['evidence_ids']:
        if identifier not in by_id: raise ValueError('Unknown evidence identifier')
        owner=by_id[identifier].get('owner_model_id')
        if owner is not None and owner!=update['id']:
            raise ValueError('Evidence belongs to model '+owner+', not '+update['id'])
