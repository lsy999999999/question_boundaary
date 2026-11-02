COMMON='''You are gpt-6-luna in a real, bounded scientific model-discovery development run.
Use only the public evidence here. The same simulator has been inspected in earlier development;
you cannot see its equations or new sealed inputs. New observations are real simulator executions,
not supplied by a language model. Noise std .005; some promoted old sealed observations are explicitly
noiseless. All trials reset x=0 and all latent states=0; horizon12, input magnitude<=1.5.
Do not give latent-state names physical meaning without evidence. Analogies are unverified model knowledge.
Every metric has owner, fit version, phase and time_window. Group-held-out diagnostics are ADAPTIVE
DEVELOPMENT fits. Prospective metrics are errors computed AFTER observation of predictions committed
BEFORE observation; they are not predicted error estimates. Window RMSE is not trajectory NMSE.
A local symmetry observation remains local; retain its evidence even when proposing a conflict.
All output is JSON; Chinese explanations concise. Mathematical schema: dx/dt is a fitted linear
combination of 1..8 terms. 0..2 states z0,z1, 0..3 positive parameters p0,p1,p2 with
.02<=lower<initial<upper<=4. Parameter/state arrays can be empty. Coefficients fitted in [-8,8].
Allowed expressions: x,u,t, declared z/p names, constants abs<=10, + - * /, **2/**3, unary tanh/sin/cos/abs.
State rates are submitted expressions, integrated with Euler dt=.1; use only schema, no arbitrary code.
Numerical fitting can fail: finite budget and local minima are not physical refutations.
'''
PROPOSAL='''Propose one executable revision, new state/relation, or retention based on current errors AND
recorded local properties. Do not merely add terms without explaining observable consequences.
Return {"parent_id":"existing model","evidence_ids":["metric/fact id"],"operation":"revise|new|retain",
"concept":"Chinese <=100 characters","reason":"Chinese <=160 characters",
"spec":{"parameters":[{"name":"p0","lower":number,"initial":number,"upper":number}],
"states":[{"name":"z0","meaning":"...","rate":"expression"}],"terms":["expression"]},
"expected_change":"Chinese <=100 characters","analogy":{"domain":"...","mapping":"..."},
"provenance":"model_knowledge_unverified",
"boundary":{"model_id":"parent_id","status":"proposed|abstain","expression":"predicate or empty string","reason":"Chinese <=100 characters"}}.
Boundary predicts whole-trajectory NMSE>.05 of the CURRENT parent fit on a planned input, not a physical transition.
Input-history predicates can combine comparisons and and/or/not, numeric + - * / and these primitives:
value(t): input at sampled time0..12; area(a,b): input integral over [a,b); abs_area(a,b): absolute integral;
peak(a,b): largest |input| in window; gap(i): zero/nearzero interval before reversal i; jump(i): reversal
magnitude. Reversals are numbered from0, ignoring |u|<=.1; gap/jump return0 if that event is absent.
Use constant time endpoints 0<=a<b<=12 and event index0..5. Predicate <=240 chars. Can use several
windows and combine conditions; no external code. Abstain if no defensible range guess.
'''
RETENTION='''Inspect the newly fitted proposal against every preserved local relationship.
Return {"model_id":"proposed id","disposition":"keep_for_test|withdraw",
"relations":[{"relation_id":"id","computed_status":"compatible|conflict|unavailable","response":"retain_local_fact|acknowledge_conflict|unavailable"}],
"comment":"Chinese <=160 characters"}. Include all three relation IDs exactly once.
computed_status must match the supplied numeric result. For conflict, acknowledge_conflict explicitly;
keeping an approximate candidate for a test does NOT erase the original observation or resolve conflict.
Withdraw if you judge the proposal not worth testing. Do not rewrite observed values.
'''
QUESTION='''Choose an executable scientific experiment. Return {"family":"reversal_depth|recovery_gap|dwell_time|polarity",
"purpose":"discriminate|boundary_probe|probe_relation","target_ids":["executable id"],
"amplitude_range":[low,high],"value_range":[low,high],"evidence_ids":["metric/fact id"],"rationale":"Chinese <=180 characters"}.
Family reversal_depth: sign*A from .5 to3.5, then -sign*value until6.5, then0; value .2..1.5.
Family recovery_gap: sign*A from .5 to3.5, zero for value seconds, then -sign*A for2s, then0; value0..3.
Family dwell_time: sign*A starts .5 for value seconds, then -sign*A for2.5s then0; value1..4.
Each such pair changes value only. Compiler tries3 amplitudes, both signs,4 value levels.
Family polarity: +/-A pulses from .5 lasting value seconds, value1..5; compiler tries3 amplitudes/4durations.
A range .2..1.5. discriminate needs >=2 targets separated by3*.005*sqrt(2) RMS in predictions.
boundary_probe must straddle the declared history predicate; unavailable if boundary status abstain.
probe_relation is available only for polarity and need not separate candidates. Already seen inputs
are excluded. If compiler feedback says no admissible design, revise the question; don't infer impossibility.
'''
ASSESS='''Assess the ACTUAL prospective outcomes, keeping them separate from newly refitted CV diagnostics.
Return {"updates":[{"id":"model id","status":"active|weakened|retired","evidence_ids":["owned metric IDs"],"reason":"Chinese <=90 characters"}],
"boundary_verdict":"supported_on_pair|violated_on_pair|untested","boundary_metric_ids":["prospective metric IDs for boundary owner or empty if abstained"],
"comment":"Chinese <=120 characters"}.
Copy required_boundary_metric_ids exactly into boundary_metric_ids. If the boundary abstained, this field MUST be [] even when actual_outcome contains prospective metric IDs. Cite prospective error evidence normally in updates[].evidence_ids.
Do not use refitted CV values to decide the original boundary labels. If no boundary was proposed, verdict
is untested. If any committed label was wrong, verdict is violated_on_pair. Otherwise supported_on_pair
means only this pair. Do not infer universal scope or physical interpretation. Model-specific citations
must belong to that model. At least one update. Selection will later follow a frozen numerical rule;
your prose does not override it.
'''
