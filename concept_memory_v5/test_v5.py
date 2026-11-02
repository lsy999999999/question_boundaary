import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from engine import control, digest
from memory import (relation, check, discover, fit_version, validate_resolutions,
                    extension_record)
from temporal import op, series, label, validate_scope
from protocol import commit, execute, audit_pair
from worlds import configuration, designer_model, mirror_pair, observe


class TemporalTests(unittest.TestCase):
    def test_causal_prefix_and_lag(self):
        u=np.r_[np.zeros(10),np.ones(20),np.zeros(91)]
        expressions=[op('lag',{'signal':'u'},steps=5),op('mean',{'signal':'u'},steps=8),
                     op('run',op('lt',{'signal':'u'},.5)),op('integral',{'signal':'u'})]
        for expr in expressions:
            np.testing.assert_allclose(series(expr,u)[:20],series(expr,u[:20]))
        self.assertEqual(series(expressions[0],u)[14],0.)
        self.assertEqual(series(expressions[0],u)[15],1.)

    def test_temporal_composition_distinguishes_gap(self):
        from boundaries import action,features
        us=[control(action('recovery_gap',1.,1,float(g))) for g in (0,1)]
        self.assertEqual(features(us[0]),features(us[1]))
        expr=op('and',op('lt',op('abs',{'signal':'u'}),.1),
                op('and',op('ge',{'signal':'t'},3.5),op('lt',{'signal':'t'},4.5)))
        scope=dict(expression=op('gt',op('duration',expr),.5),reduce='last')
        self.assertEqual([label(scope,u) for u in us],[False,True])

    def test_reject_code_future_measurement_and_untyped_scopes(self):
        bad=[{'signal':'x'},op('lag',{'signal':'u'},steps=-1),
             {'op':'__import__','args':['os']},op('not',{'signal':'u'}),
             op('add',{'signal':'u'},True),float('nan')]
        for expr in bad:
            with self.assertRaises(ValueError):series(expr,np.zeros(121))
        with self.assertRaises(ValueError):validate_scope(dict(expression=1,reduce='last'))
        with self.assertRaises(ValueError):series(op('div',1,0),np.zeros(121))

    def test_complexity_limit(self):
        expr={'signal':'u'}
        for _ in range(20):expr=op('neg',expr)
        with self.assertRaises(ValueError):series(expr,np.zeros(121))

    def test_scope_version_and_invalid_search_points(self):
        from boundaries import validate_boundary,compile_question
        cfg=configuration('linear_memory',110101);m=designer_model(cfg)
        b=dict(model_id='m',fit_version=fit_version(m),scope=dict(
            expression=op('gt',op('duration',op('lt',op('abs',{'signal':'u'}),.1)),8.),reduce='last'),
            error_threshold=.05,reason='test scope')
        validate_boundary(b,{'m':m})
        b['fit_version']='old'
        with self.assertRaises(ValueError):validate_boundary(b,{'m':m})
        b['fit_version']=fit_version(m)
        q=dict(family='recovery_gap',purpose='boundary_probe',target_ids=['m'],
               amplitude_range=[1.,1.],value_range=[.2,1.])
        compiled=compile_question(q,{'m':m},[],b)
        self.assertTrue(any('Invalid input schedule' in k for k in compiled['reasons']))


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.cfg=configuration('local_symmetry_only',110101)
        self.model=designer_model(self.cfg)
        self.obs=[observe(self.cfg,a,'local'+str(i)) for i,a in enumerate(mirror_pair(.4))]
        self.rel=relation(*self.obs)

    def test_canonical_unicode_fit(self):
        self.model['spec']['states'][0]['meaning']='历史状态'
        escaped=json.loads(json.dumps(self.model,ensure_ascii=True))
        native=json.loads(json.dumps(self.model,ensure_ascii=False))
        self.assertEqual(fit_version(escaped),fit_version(native))
        native['fit']['coefficients'][0]+=.01
        self.assertNotEqual(fit_version(escaped),fit_version(native))

    def test_mutated_observation_rejected(self):
        byid={o['id']:o for o in copy.deepcopy(self.obs)};byid['local0']['x'][5]+=.1
        with self.assertRaises(ValueError):check('m',self.model,self.rel,byid)

    def test_local_success_does_not_impose_global_symmetry(self):
        self.assertEqual(self.rel['claim_status'],'observed_local_support')
        c=check('m',self.model,self.rel,{o['id']:o for o in self.obs})
        self.assertFalse(c['conflict'])
        new=[observe(self.cfg,a,'new'+str(i)) for i,a in enumerate(mirror_pair(1.3))]
        other=relation(*new);before=digest(self.rel)
        update=extension_record(self.rel,other,'committed_fixture')
        self.assertEqual(update['extension_status'],'counterexample_to_extension')
        self.assertEqual(digest(self.rel),before)
        self.assertEqual(update['old_local_status'],'observed_local_support')

    def test_duplicate_inputs_not_independent_relationships(self):
        duplicates=copy.deepcopy(self.obs)
        for o in duplicates:o['id']+='repeat'
        self.assertEqual(len(discover(self.obs+duplicates)),1)

    def test_conflict_requires_current_fit_and_explicit_treatment(self):
        bad=copy.deepcopy(self.model);bad['spec']['terms'].append('u**2');bad['fit']['coefficients'].append(.7)
        c=check('m',bad,self.rel,{o['id']:o for o in self.obs})
        self.assertTrue(c['conflict'])
        args=('m',bad,[c],[self.rel],self.obs)
        with self.assertRaises(ValueError):validate_resolutions({'resolutions':[]},*args)
        item=dict(relation_id=self.rel['id'],fit_version='stale',action='withdraw_candidate',reason='regression')
        with self.assertRaises(ValueError):validate_resolutions({'resolutions':[item]},*args)
        item['fit_version']=fit_version(bad)
        self.assertTrue(validate_resolutions({'resolutions':[item]},*args))

    def test_forecast_order_and_prediction_binding(self):
        with tempfile.TemporaryDirectory() as d:
            packet=commit(d,'test',{'m':self.model},mirror_pair(1.3),['new0','new1'])
            result=execute(d,'test',packet,lambda a,i:observe(self.cfg,a,i))
            self.assertEqual(audit_pair(packet,result),[])
            bad=copy.deepcopy(result);bad['observations'][0]['time_ns']=packet['record']['time_ns']-1
            self.assertIn('forecast/observation order',audit_pair(packet,bad))
            changed=copy.deepcopy(packet);changed['record']['predictions']['m'][0][0]+=.5
            changed['sha256']=digest(changed['record']);bad=copy.deepcopy(result);bad['forecast_sha256']=changed['sha256']
            self.assertIn('prediction recomputation mismatch',audit_pair(changed,bad))


if __name__=='__main__':unittest.main()
