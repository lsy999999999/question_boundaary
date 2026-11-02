import unittest
import numpy as np
from engine import Spec,GRID,control
from numerics import rollout,affine_signature,structural_key,fit_model,predict,groups
from experiments import model_guard,compile_question


def model(output=False):
    return dict(spec=dict(parameters=[dict(name='p0',lower=.1,initial=1.,upper=4.)],
        states=[dict(name='z0',meaning='test fixture',rate='x-p0*z0' if output else 'u-p0*z0')],
        terms=['1','x','u','z0']),fit=dict(parameters=[3. if output else 2.],coefficients=[0.,0.,1.,-2.] if output else [0.,-1.,1.,1.]),group_cv_nmse=.01)


class Tools(unittest.TestCase):
    def test_fast_solver_matches_explicit_euler(self):
        m=model();s=Spec(m['spec']);u=np.sin(GRID)
        np.testing.assert_allclose(predict(m,u),s.rollout(m['fit']['parameters'],m['fit']['coefficients'],u),atol=2e-12)

    def test_exact_affine_equivalence_includes_bias(self):
        self.assertEqual(affine_signature(model()),affine_signature(model(True)))
        changed=model(True);changed['fit']['coefficients'][0]=.1
        self.assertNotEqual(affine_signature(model()),affine_signature(changed))

    def test_duplicate_structure_ignores_prose_but_not_dynamics(self):
        a=model()['spec'];b=model()['spec'];b['states'][0]['meaning']='another story'
        self.assertEqual(structural_key(a),structural_key(b))
        self.assertNotEqual(structural_key(a),structural_key(model(True)['spec']))

    def test_failed_matching_is_not_admitted(self):
        q=dict(kind='matched_history',target_ids=['a','b'],tolerance_x=.04,purpose='discriminate')
        acts=[dict(points=[[0,0],[.5,s],[7,0]]) for s in (1,-1)]
        result=model_guard(q,acts,{'a':model(),'b':model(True)})
        self.assertFalse(result['passed'])

    def test_grouped_trajectory_fit_predicts_new_input(self):
        raw=dict(parameters=[],states=[],terms=['x','u']);obs=[]
        for identifier,amp in enumerate((1.,1.,-.6)):
            action=dict(points=[[0,0],[1,amp],[4,0]]);u=control(action);x=np.zeros(len(GRID))
            for i in range(len(GRID)-1): x[i+1]=x[i]+.1*(-.7*x[i]+.8*u[i])
            obs.append(dict(id=str(identifier),action=action,t=GRID.tolist(),u=u.tolist(),x=x.tolist()))
        self.assertEqual(len(groups(obs)),2)
        fit=fit_model(raw,obs)
        self.assertEqual(sorted(len(f['ids']) for f in fit['cv_folds']),[1,2])
        self.assertLess(fit['group_cv_nmse'],1e-7)
        self.assertAlmostEqual(fit['fit']['coefficients'][0],-.7,places=4)

    def test_relation_compiler_emits_executable_python_numeric_points(self):
        q=dict(kind='polarity',purpose='probe_relation',target_ids=['a'],amplitude_range=[.2,1.2],
               duration_range=[1.,4.],scale=1.5,tolerance_x=.04)
        u=np.zeros(len(GRID));obs=[dict(id='zero',u=u.tolist(),x=u.tolist())]
        result=compile_question(q,{'a':model()},obs,1)
        self.assertTrue(result['passed'])
        self.assertTrue(np.allclose(control(result['actions'][0]),-control(result['actions'][1])))


if __name__=='__main__': unittest.main()
