"""Meaningful expression-safety and numerical-forecast checks; no model simulation."""
import unittest
import numpy as np
from engine import Spec, GRID, expression, control, fit_model, predict, nmse, collisions


class EngineChecks(unittest.TestCase):
    def test_only_math_expressions(self):
        for source in ("__import__('os')", 'x.__class__', '[x for x in u]',
                       'open(1)', 'x**99', 'lambda: x', 'sin(x, u)'):
            with self.assertRaises((ValueError,SyntaxError)):
                expression(source, {'x','u','t'})
        f = expression('tanh(x) + u*x**2', {'x','u','t'})
        self.assertAlmostEqual(f(dict(x=.3,u=.4,t=0)),np.tanh(.3)+.4*.3**2)

    def test_unstable_state_is_rejected(self):
        spec = Spec(dict(parameters=[],states=[dict(name='z0',meaning='test',rate='10*z0+u')],terms=['x','u','z0']))
        with self.assertRaises(ValueError):
            spec.rollout([],[-1,1,.1],np.ones(len(GRID)))

    def test_generated_expression_fits_and_forecasts_new_input(self):
        spec = dict(parameters=[],states=[],terms=['x','u'])
        def observed(action, identifier):
            u=control(action)
            x=np.zeros(len(GRID))
            for i in range(len(GRID)-1):
                x[i+1]=x[i]+.1*(-.7*x[i]+.8*u[i])
            return dict(id=identifier,action=action,t=GRID.tolist(),u=u.tolist(),x=x.tolist())
        actions=[dict(points=[[0,0],[1,1],[5,0]]),dict(points=[[0,0],[2,-.7],[7,0]]),
                 dict(points=[[0,0],[1,.5],[8,0]])]
        obs=[observed(a,str(i)) for i,a in enumerate(actions)]
        model=fit_model(spec,obs)
        novel=observed(dict(points=[[0,0],[1,-1],[3,.4],[6,0]]),'heldout')
        self.assertLess(nmse(predict(model,novel['u']),np.asarray(novel['x'])),.004)
        self.assertTrue(np.isfinite(model['trajectory_cv_nmse']))

    def test_action_limits(self):
        for a in (dict(points=[[1,0],[2,1]]),dict(points=[[0,0],[.1,1]]),
                  dict(points=[[0,0],[2,5]])):
            with self.assertRaises(ValueError):
                control(a)

    def test_no_collision_proof_from_identical_trace(self):
        u=control(dict(points=[[0,0],[1,1],[5,0]]))
        x=np.zeros(len(GRID))
        for i in range(len(GRID)-1):
            x[i+1]=x[i]+.1*(-x[i]+u[i])
        obs=[dict(id=str(i),u=u.tolist(),x=x.tolist()) for i in range(2)]
        self.assertEqual(collisions(obs),[])


if __name__=='__main__':
    unittest.main()
