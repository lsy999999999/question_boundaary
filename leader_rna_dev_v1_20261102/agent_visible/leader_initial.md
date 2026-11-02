# Case R01: internal cavities in a transcribing RNA condensate

You are investigating a physical observation. You have not been given its published explanation.

The baseline DNA template encodes a four-arm RNA nanostructure. Terminal self-complementary loops can bind other copies, permitting assembly into RNA-rich droplets during transcription. RNA is produced from DNA using the same nominal transcription conditions. Fluorescent RNA imaging records the droplets over approximately two days.

Condition A uses the reference DNA template without the amplification treatment. Condition B uses DNA obtained after amplification of the same starting template. Initial images contain similar small dark-area fractions; later B droplets show persistent internal RNA-poor cavities, while A stays nearly homogeneous. The observation to explain is the emergence and persistence of these internal cavities, and any additional consequences your explanation predicts. The causal effects of amplification, product heterogeneity, and reaction carryover have not been established by this initial evidence.

The supplied empty-area fraction is segmented internal dark area divided by total filled droplet area. These are image-derived area fractions, not direct concentrations or free energy. Measurements pool seven fields per condition across two independent preparations. SEM and object counts do not represent independent preparation-level replication. You initially see only t=0,4,8,12,24 h. Measurements at 36 and 48 h are reserved for a within-run time-extrapolation commitment.

Only background works first published on or before 2025-05-12 may be returned by the coordinator. Do not search the target identity or later accounts. Disclose any specific study recognition. You may request raw DNA sequences/read frequencies, template-fraction endpoint measurements, measured coexisting-phase concentrations, or preparation-1 tracking. Availability does not establish support. No new physical experiments can be performed in this run. Source recognition and time-filtered retrieval do not erase pretraining knowledge.

OBSERVATIONS:
[
  {
    "condition": "A",
    "time_h": 0.0,
    "mean_empty_area_fraction": 0.0148724491091024,
    "sem_empty_area_fraction": 0.0002437652793328,
    "n_fields": 7,
    "n_objects": 3490
  },
  {
    "condition": "A",
    "time_h": 4.0,
    "mean_empty_area_fraction": 0.0054389893768169,
    "sem_empty_area_fraction": 0.0004851399860374,
    "n_fields": 7,
    "n_objects": 1201
  },
  {
    "condition": "A",
    "time_h": 8.0,
    "mean_empty_area_fraction": 0.0044390495790911,
    "sem_empty_area_fraction": 0.0004738057874311,
    "n_fields": 7,
    "n_objects": 998
  },
  {
    "condition": "A",
    "time_h": 12.0,
    "mean_empty_area_fraction": 0.0040641907190291,
    "sem_empty_area_fraction": 0.0004533639169051,
    "n_fields": 7,
    "n_objects": 937
  },
  {
    "condition": "A",
    "time_h": 24.0,
    "mean_empty_area_fraction": 0.0044581874447536,
    "sem_empty_area_fraction": 0.0005448059632589,
    "n_fields": 7,
    "n_objects": 859
  },
  {
    "condition": "B",
    "time_h": 0.0,
    "mean_empty_area_fraction": 0.0138090880510916,
    "sem_empty_area_fraction": 0.0002264511197326,
    "n_fields": 7,
    "n_objects": 3158
  },
  {
    "condition": "B",
    "time_h": 4.0,
    "mean_empty_area_fraction": 0.0159150610393171,
    "sem_empty_area_fraction": 0.0011019283039892,
    "n_fields": 7,
    "n_objects": 564
  },
  {
    "condition": "B",
    "time_h": 8.0,
    "mean_empty_area_fraction": 0.0239331148418327,
    "sem_empty_area_fraction": 0.0016049805499992,
    "n_fields": 7,
    "n_objects": 545
  },
  {
    "condition": "B",
    "time_h": 12.0,
    "mean_empty_area_fraction": 0.0402799733501556,
    "sem_empty_area_fraction": 0.0031537325464317,
    "n_fields": 7,
    "n_objects": 496
  },
  {
    "condition": "B",
    "time_h": 24.0,
    "mean_empty_area_fraction": 0.0891834703945908,
    "sem_empty_area_fraction": 0.0078546202289423,
    "n_fields": 7,
    "n_objects": 349
  }
]

CAPABILITIES:
- The coordinator mediates literature queries, checks dates, and returns source cards. No direct network/search by the actors.
- The coordinator can run Python (numpy/scipy/pandas/sympy available) on already-opened data. Submit an exact algorithm, equations, parameter ranges, objective, training IDs and desired outputs; code is optional. The coordinator implements that request without inventing missing scientific assumptions. Missing specifications may be returned as an error. Computations must not read hidden data or target theory.
- Observed evidence can be requested from the four measurement categories in the case brief. Each category's first release costs one evidence release. Extra unavailable physical measurements return unavailable, not fabricated values.
- Method cards are provided on explicit ID request: choose 1–3 in the decision. You may specify the intended task together with the request; the coordinator attaches the cards before the researcher executes it.
- The two actor contexts are fresh, both gpt-6-luna. Protocol-level file/network restrictions are not OS isolation.
BUDGET: six leader replies, six researcher replies, six literature queries, ten computational requests, four measured-evidence releases, one final commitment. Maximum active execution wall time 90 minutes; no user API credential or paid external API is used. No billing/token totals are available from this agent tool. Unused budget need not be spent.
FINAL DELIVERABLE: a model/explanation, actual derivations and computations, an evidence-linked revision record, and numerical predictions or explicit abstentions for A and B at 36 h and 48 h. The final researcher reply must freeze a model choice and parameter values before later timepoints are disclosed. These are development data already known to the curator; no independent confirmation claim.
FIRST ACTION: disclose source recognition; identify the main bottleneck; select up to three method IDs; assign one specific researcher task. Do not spend your first turn merely restating the workflow.
