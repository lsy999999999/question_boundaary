"""Freeze a new, curator-informed development replay without changing earlier runs."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'real_case_blind_20261102'
METHOD=ROOT.parent/'leader_methods_v1_20261102'

def save(path,data):
    with path.open('x') as f:
        if isinstance(data,str): f.write(data)
        else: json.dump(data,f,ensure_ascii=False,indent=2)

def main():
    for name in ['agent_visible','frozen_prompts','curator','transcripts','computations','literature']:
        (ROOT/name).mkdir(exist_ok=True)
    for name in ['LEADER_SYSTEM_PROMPT.md','RESEARCHER_SYSTEM_PROMPT.md','METHOD_INDEX.md','METHOD_LIBRARY.json','COMPOSITION_PLAYBOOK.md']:
        dest=ROOT/'frozen_prompts'/name
        if dest.exists(): raise RuntimeError('Refusing overwrite')
        shutil.copyfile(METHOD/name,dest)
    initial=json.loads((OLD/'agent_workspace/initial_measurements.json').read_text())
    train=[x for x in initial if x['time_h']<=24]
    future=[x for x in initial if x['time_h']>24]
    save(ROOT/'agent_visible/initial_measurements.json',train)
    save(ROOT/'curator/withheld_late_timepoints.json',future)
    brief=(OLD/'agent_workspace/BRIEF.md').read_text()
    # Keep the scientific construction; replace the original task/permissions with this run's protocol.
    brief=brief.split('The supplied empty-area fraction')[0]
    brief+='''The supplied empty-area fraction is segmented internal dark area divided by total filled droplet area. These are image-derived area fractions, not direct concentrations or free energy. Measurements pool seven fields per condition across two independent preparations. SEM and object counts do not represent independent preparation-level replication. You initially see only t=0,4,8,12,24 h. Measurements at 36 and 48 h are reserved for a within-run time-extrapolation commitment.

Only background works first published on or before 2025-05-12 may be returned by the coordinator. Do not search the target identity or later accounts. Disclose any specific study recognition. You may request raw DNA sequences/read frequencies, template-fraction endpoint measurements, measured coexisting-phase concentrations, or preparation-1 tracking. Availability does not establish support. No new physical experiments can be performed in this run. Source recognition and time-filtered retrieval do not erase pretraining knowledge.
'''
    save(ROOT/'agent_visible/case_brief.md',brief)
    budget=dict(leader_turns=6,researcher_turns=6,literature_queries=6,compute_requests=10,evidence_releases=4,final_commitments=1)
    runtime='''
CAPABILITIES:
- The coordinator mediates literature queries, checks dates, and returns source cards. No direct network/search by the actors.
- The coordinator can run Python (numpy/scipy/pandas/sympy available) on already-opened data. Submit an exact algorithm, equations, parameter ranges, objective, training IDs and desired outputs; code is optional. The coordinator implements that request without inventing missing scientific assumptions. Missing specifications may be returned as an error. Computations must not read hidden data or target theory.
- Observed evidence can be requested from the four measurement categories in the case brief. Each category's first release costs one evidence release. Extra unavailable physical measurements return unavailable, not fabricated values.
- Method cards are provided on explicit ID request: choose 1–3 in the decision. You may specify the intended task together with the request; the coordinator attaches the cards before the researcher executes it.
- The two actor contexts are fresh, both gpt-6-luna. Protocol-level file/network restrictions are not OS isolation.
BUDGET: six leader replies, six researcher replies, six literature queries, ten computational requests, four measured-evidence releases, one final commitment. Maximum active execution wall time 90 minutes; no user API credential or paid external API is used. No billing/token totals are available from this agent tool. Unused budget need not be spent.
FINAL DELIVERABLE: a model/explanation, actual derivations and computations, an evidence-linked revision record, and numerical predictions or explicit abstentions for A and B at 36 h and 48 h. The final researcher reply must freeze a model choice and parameter values before later timepoints are disclosed. These are development data already known to the curator; no independent confirmation claim.
FIRST ACTION: disclose source recognition; identify the main bottleneck; select up to three method IDs; assign one specific researcher task. Do not spend your first turn merely restating the workflow.
'''
    save(ROOT/'agent_visible/leader_initial.md',brief+'\nOBSERVATIONS:\n'+json.dumps(train,ensure_ascii=False,indent=2)+'\n'+runtime)
    protocol=dict(run_id=ROOT.name,date='2026-11-02',kind='curator_informed_development_replay',model='gpt-6-luna',budgets=budget,
        initial_times_h=[0,4,8,12,24],withheld_times_h=[36,48],
        baseline='Earlier four-turn investigator record, descriptive reference only; different budget and numerical interfaces prevent causal/equal-compute attribution.',
        success_milestones=[
            'M1: evidence-linked knowledge/assumption separation and two experimentally distinguishable explanations',
            'M2: closed executable mechanistic model with state units, dynamics, observation mapping and initial/boundary conditions; a fitted time curve alone does not qualify',
            'M3: at least one actually executed actor-requested numerical calculation on permitted measured data',
            'M4: actor-specified parameter fitting or identifiable-parameter analysis, distinct from arbitrary-parameter illustration',
            'M5: explicit derived relation, stability/threshold condition, or limiting-case calculation with stated assumptions',
            'M6: evidence-driven structural/parameter/scope revision with old commitment retained; no forced failure',
            'M7: frozen within-run late-time predictions scored after commitment; development forecast, not independently new data',
            'M8: curator-only comparison with published mechanism, scored component by component without supplementing actor gaps'],
        exclusions=['target title/author/DOI/abstract/discussion','fitted theory sheets and parameters','prior actor conclusions and prediction scores','late timepoints before commitment'],
        limitations=['prompt/broker restrictions, no OS isolation proof','pretraining contamination unknown','curator has seen all data and target mechanism','no agent-count or equal-budget causal experiment','no new wet-lab measurements'])
    save(ROOT/'curator/FROZEN_PROTOCOL.json',protocol)
    frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file()}
    save(ROOT/'curator/PRE_RUN_MANIFEST.json',frozen)
    save(ROOT/'STATUS.md','# 状态：已冻结，等待首轮模型回复\n\n2026-11-02。gpt-6-luna负责人＋执行者，已有RNA案例开发回放。最多6+6次回复；原运行不修改。\n')
    print(json.dumps(dict(run=str(ROOT),train_points=len(train),reserved_points=len(future),budget=budget),ensure_ascii=False))

if __name__=='__main__':main()
