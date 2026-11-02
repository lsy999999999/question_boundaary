import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import unittest,json
from pathlib import Path
import numpy as np
from engine import GRID,control,digest
from numerics import fit_model
from parallel_fit import Fitter
from scope import evaluate
from design import action
from ledger import fit_id,local_facts,retention,choose,check_citations

class Protocol(unittest.TestCase):
    def test_abstained_boundary_contract_and_actionable_feedback(self):
        from ledger import boundary_evidence_ids,check_boundary_citations
        outcome=dict(boundary_verdict='untested',boundary_metric_ids=['prospective:m:fit:obs'])
        self.assertEqual(boundary_evidence_ids(outcome),[])
        check_boundary_citations(dict(boundary_metric_ids=[]),outcome)
        with self.assertRaisesRegex(ValueError,r'must equal \[\]'):
            check_boundary_citations(dict(boundary_metric_ids=outcome['boundary_metric_ids']),outcome)
        outcome['boundary_verdict']='violated_on_pair'
        check_boundary_citations(dict(boundary_metric_ids=outcome['boundary_metric_ids']),outcome)
    def test_parallel_matches_serial_grouped_fit(self):
        raw=dict(parameters=[],states=[],terms=['x','u']);obs=[]
        for i,amp in enumerate((1.,1.,-.6)):
            a=dict(points=[[0,0],[1,amp],[4,0]]);u=control(a);x=np.zeros(len(u))
            for k in range(len(u)-1):x[k+1]=x[k]+.1*(-.7*x[k]+.8*u[k])
            obs.append(dict(id=str(i),action=a,t=GRID.tolist(),u=u.tolist(),x=x.tolist()))
        serial=fit_model(raw,obs);f=Fitter(2)
        try:parallel,errors=f.fit({'m':raw},obs)
        finally:f.close()
        self.assertFalse(errors);p=parallel['m'];self.assertEqual([r['ids'] for r in p['cv_folds']],[r['ids'] for r in serial['cv_folds']])
        np.testing.assert_allclose(p['fit']['coefficients'],serial['fit']['coefficients'],rtol=0,atol=1e-12)
        self.assertAlmostEqual(p['group_cv_nmse'],serial['group_cv_nmse'],places=14)
    def test_scope_distinguishes_recovery_gap_with_same_global_summaries(self):
        a=control(action('recovery_gap',1.,1,0.));b=control(action('recovery_gap',1.,1,1.))
        self.assertFalse(evaluate('gap(0) > 0.5 and jump(0) > 1.5',a));self.assertTrue(evaluate('gap(0) > 0.5 and jump(0) > 1.5',b))
        self.assertTrue(evaluate('area(0,3.5) > 2.9 and value(0.5) == 1',a))
    def test_scope_rejects_arbitrary_code_and_bad_windows(self):
        u=np.zeros(121)
        for s in ["__import__('os').system('x')",'area(3,1)>0','value(99)>0','jump(0.5)>0','area(value(1),2)>0','1/0>1']:
            with self.assertRaises((ValueError,SyntaxError,ArithmeticError)):evaluate(s,u)
    def test_unicode_identity_uses_one_canonical_encoder(self):
        spec={'meaning':'记忆变量'};fit={'parameters':[.3]}
        self.assertEqual(fit_id(spec,fit),digest(dict(spec=spec,fit=fit)))
        self.assertEqual(fit_id(spec,fit),fit_id(json.loads(json.dumps(spec)),fit))
    def test_final_rule_respects_old_properties_and_generates_same_id(self):
        seed=json.loads((Path(__file__).parent/'seed_public.json').read_text());facts=local_facts(seed['observations'])
        good=seed['old_frozen_model'];good['group_cv_nmse']=.02
        bad=json.loads(json.dumps(good));bad['spec']['terms'].append('1');bad['fit']['coefficients'].append(.2);bad['group_cv_nmse']=.001
        self.assertTrue(any(x['status']=='conflict' for x in retention(bad,facts)))
        decision=choose({'good':good,'bad':bad},set(),facts)
        self.assertEqual(decision['selected_id'],'good');self.assertIn('good',decision['explanation']);self.assertNotIn('bad',decision['explanation'])
        self.assertIsNone(choose({'good':good},{'good'},facts)['selected_id'])
    def test_all_fixed_new_inputs_are_valid_and_unseen(self):
        from run import sealed_inputs
        seed=json.loads((Path(__file__).parent/'seed_public.json').read_text())
        known={tuple(np.round(o['u'],12)) for o in seed['observations']}
        planned=[tuple(np.round(control(a),12)) for a in sealed_inputs()]
        self.assertEqual(len(set(planned)),8);self.assertFalse(set(planned)&known)

    def test_owner_cannot_be_swapped(self):
        ctx=dict(metrics=[dict(id='a',owner_model_id='m1')],facts=[],historical_refutation=dict(id='old',owner_model_id='old'))
        with self.assertRaises(ValueError):check_citations(['a'],ctx,'m2')
        check_citations(['a'],ctx,'m1')

if __name__=='__main__':unittest.main()
