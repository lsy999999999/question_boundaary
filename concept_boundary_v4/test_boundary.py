import unittest
import numpy as np
from engine import control,GRID
from test_tools import model
from boundaries import action,features,boundary_label,compile_question,evaluate
from run import fixed_inputs

class BoundaryTests(unittest.TestCase):
    def test_zero_gap_is_direct_reversal_and_grid_executable(self):
        for family,values in [('recovery_gap',(0.,1.,3.)),('dwell_time',(1.,2.5,4.)),('reversal_depth',(.2,.7,1.5))]:
            for v in values:
                a=action(family,1.,1,v);u=control(a)
                self.assertEqual(len(u),121);self.assertLessEqual(max(abs(u)),1.5)
        u=control(action('recovery_gap',1.,1,0.));self.assertEqual(u[34],1.);self.assertEqual(u[35],-1.)

    def test_boundary_probe_straddles_and_is_falsifiable(self):
        b=dict(model_id='a',feature='peak_abs',operator='gt',threshold=.8,error_threshold=.05)
        q=dict(family='reversal_depth',purpose='boundary_probe',target_ids=['a'],amplitude_range=[.4,.4],value_range=[.2,1.2])
        obs=[dict(u=np.zeros(len(GRID)).tolist())];m={'a':model()}
        c=compile_question(q,m,obs,b);self.assertTrue(c['passed']);self.assertEqual(set(c['guard']['boundary_labels']),{True,False})
        us=[control(a) for a in c['actions']];ys=[np.zeros(len(GRID)).tolist() for u in us]
        observations=[dict(u=u.tolist(),x=y) for u,y in zip(us,ys)]
        result=evaluate(q,c,b,observations,{'a':ys});self.assertTrue(result['actual_conditions_met']);self.assertFalse(all(result['boundary_label_correct']))
        observations[0]['u'][20]+=.1;self.assertFalse(evaluate(q,c,b,observations,{'a':ys})['actual_conditions_met'])

    def test_equivalent_targets_do_not_fake_discrimination(self):
        b=dict(model_id='a',feature='peak_abs',operator='gt',threshold=.8,error_threshold=.05)
        q=dict(family='reversal_depth',purpose='discriminate',target_ids=['a','b'],amplitude_range=[.4,.4],value_range=[.2,1.2])
        c=compile_question(q,{'a':model(),'b':model(True)},[dict(u=np.zeros(len(GRID)).tolist())],b)
        self.assertFalse(c['passed'])

    def test_new_sealed_inputs_distinct_and_valid(self):
        actions=fixed_inputs();self.assertEqual(len(actions),8)
        us=[tuple(control(a)) for a in actions];self.assertEqual(len(set(us)),8)

if __name__=='__main__':unittest.main()
