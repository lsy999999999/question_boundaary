"""Checks of causal access, predictive fitting and pre-observation logging."""
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from discovery.llm import CARDS, cards_for, make_prompt, parse_decision
from discovery.models import fit
from discovery.runner import State
from discovery.world import INITIAL_ACTIONS, World, make_task


class ProtocolTests(unittest.TestCase):
    def test_cards_content_control_preserves_ids_and_changes_relations(self):
        correct, shuffled = cards_for("structured"), cards_for("shuffled")
        self.assertEqual([c["id"] for c in correct], [c["id"] for c in shuffled])
        self.assertEqual(sorted(c["structure"] for c in correct), sorted(c["structure"] for c in shuffled))
        self.assertTrue(all(a["structure"] != b["structure"] for a,b in zip(correct,shuffled)))
        self.assertEqual(correct, CARDS)

    def test_candidate_evidence_shared_and_uses_only_observed_training(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = State(make_task("dev", "memory", 201), Path(tmp))
            def forbid_test(*args, **kwargs):
                raise AssertionError("Independent evaluation accessed while preparing prompt")
            state.world.evaluate = forbid_test
            a = json.loads(make_prompt(state,"plain")[1]["content"])
            b = json.loads(make_prompt(state,"structured")[1]["content"])
            self.assertEqual(a["candidate_models_training_only"],b["candidate_models_training_only"])
            self.assertEqual(a["experiment_prediction_disagreement"],b["experiment_prediction_disagreement"])
            self.assertEqual(len(a["candidate_models_training_only"]),11)
            self.assertNotIn("cross_domain_notes",a)
            self.assertEqual(b["cross_domain_notes"],CARDS)
            self.assertNotIn('"family"', json.dumps(b))
            self.assertNotIn('"params"', json.dumps(b))

    def test_no_truth_in_public_observations_and_no_test_query(self):
        w = World(make_task("dev", "memory", 19))
        obs = w.experiment("positive_pulse")
        self.assertEqual(set(obs.public_summary()), {"action", "repeat", "samples_t_u_x", "observed_range"})
        np.testing.assert_array_equal(obs.y, w.experiment("positive_pulse").y)
        self.assertFalse(np.array_equal(obs.y, w.experiment("positive_pulse", 1).y))
        with self.assertRaises(ValueError):
            w.experiment("test_chirp")

    def test_memoryless_model_predicts_independent_controls(self):
        w = World(make_task("dev", "linear", 17), noise=0)
        model = fit([w.experiment(a) for a in INITIAL_ACTIONS], "state")
        self.assertLess(w.evaluate(model)["test_nmse"], 0.015)

    def test_history_can_resolve_current_state_failure(self):
        task = make_task("dev", "memory", 23)
        task = replace(task, params={**task.params, "a": 1.0, "c": 0.5, "gain": 0.65})
        w = World(task, noise=0.005)
        obs = [w.experiment(a) for a in INITIAL_ACTIONS]
        state_error = w.evaluate(fit(obs, "state"))["test_nmse"]
        history_error = w.evaluate(fit(obs, "memory_multiscale"))["test_nmse"]
        self.assertLess(history_error, state_error * 0.5)

    def test_forecast_is_saved_before_observation_and_resume_preserves_state(self):
        task = make_task("dev", "linear", 3)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = State(task, root)
            prompt = json.dumps(make_prompt(state, "structured"))
            self.assertNotIn('"params"', prompt)
            self.assertNotIn('"family"', prompt)
            state.step({"representation": "state", "experiment": "double_pulse", "reason": "test", "prediction": "test", "accept": False})
            forecast = json.loads((root / "round_00/forecast_before_observation.json").read_text())
            observation = json.loads((root / "round_00/observation.json").read_text())
            self.assertLess(forecast["time_ns"], observation["time_ns"])
            digest = forecast.pop("sha256")
            self.assertEqual(digest, hashlib.sha256(json.dumps(forecast, sort_keys=True).encode()).hexdigest())
            self.assertEqual(digest, observation["forecast_sha256"])
            resumed = State(task, root)
            self.assertEqual(resumed.round_index, 1)
            self.assertEqual(len(resumed.observations), 4)
            np.testing.assert_array_equal(resumed.model.coefficients, state.model.coefficients)

    def test_invalid_generation_has_explicit_fallback_and_error_record(self):
        choice, errors = parse_decision('not json', ["prbs"], "state", True)
        self.assertEqual(choice["representation"], "state")
        self.assertEqual(choice["experiment"], "prbs")
        self.assertIn("unparseable_json", errors)
        self.assertIn("missing_structural_mapping", errors)

    def test_source_reference_must_resolve_to_available_material(self):
        text = json.dumps({"representation": "memory_slow", "experiment": "prbs", "mapping": {"source_id": "a_task_id", "target_relation": "history", "condition_to_check": "persistence"}})
        choice, errors = parse_decision(text, ["prbs"], "state", True)
        self.assertEqual(choice["representation"], "memory_slow")
        self.assertIn("invalid_mapping_source_id", errors)


if __name__ == "__main__":
    unittest.main()
