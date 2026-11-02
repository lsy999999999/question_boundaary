import itertools, json, math

qmax_values = [0.1, 0.5]
xc_values = [0.05, 0.5]
kf_values = [0.1, 10.0]  # h^-1
kc_values = [0.001, 0.1]  # h^-1
x_values = [0.0, 0.1, 0.25, 0.5, 1.0]

def evaluate(x, xc, kf, kc, qmax):
    r = kf * max(x - xc, 0.0)
    qss = 0.0 if r + kc == 0 else qmax * r / (r + kc)
    tau_h = 1.0 / (r + kc) if r + kc > 0 else None
    half_life_h = math.log(2.0) / kc if r == 0 and kc > 0 else None
    return {"r_per_h": r, "qss": qss, "tau_h": tau_h, "decay_half_life_h": half_life_h}

rows = []
for x in x_values:
    vals = []
    for qmax, xc, kf, kc in itertools.product(qmax_values, xc_values, kf_values, kc_values):
        vals.append(evaluate(x, xc, kf, kc, qmax))
    rows.append({
        "x": x,
        "qss_min": min(v["qss"] for v in vals),
        "qss_max": max(v["qss"] for v in vals),
        "all_bounded_0_qmax": all(0 <= v["qss"] <= max(qmax_values) for v in vals)
    })

# Carryover model: replace x, xc, kf by c, cc, kg.
# For each sample, choose c-cc=(kf/kg)*(x-xc); then its rate r is identical.
equivalence = []
for x, xc, kf, kg in [(0.25, 0.05, 0.1, 10.0), (1.0, 0.5, 10.0, 0.1)]:
    cc = 0.4
    c = cc + (kf / kg) * max(x - xc, 0.0)
    r_mix = kf * max(x - xc, 0.0)
    r_carry = kg * max(c - cc, 0.0)
    equivalence.append({"x": x, "xc": xc, "kf_per_h": kf, "carryover_cc": cc,
                        "carryover_c": c, "r_mix_per_h": r_mix,
                        "r_carryover_per_h": r_carry,
                        "identical_rate": abs(r_mix-r_carry) < 1e-12})

checks = {
    "units": "r,kf,kc are h^-1; x,xc,q,qmax are dimensionless; dq/dt is h^-1",
    "threshold": "x<=xc implies r=0 and qss=0 for kc>0",
    "formation_limit": "kc->0 with r>0 gives qss->qmax",
    "no_formation_limit": "kf=0 gives r=0 and q decays with half-life ln(2)/kc",
    "bounds": "qss stays in [0,qmax] for nonnegative rates",
    "alternative": "A carryover-driven model has identical q dynamics under a matching effective rate; A/B alone cannot identify the driver"
}
print(json.dumps({"assumptions":"Illustrative parameter grid only; not fitted to DATA and not a physical estimate.",
                  "ranges":{"qmax":qmax_values,"xc":xc_values,"kf_per_h":kf_values,
                            "kc_per_h":kc_values,"x":x_values},
                  "equilibrium_ranges_by_x":rows,
                  "carryover_equivalence_examples":equivalence,
                  "checks":checks}, sort_keys=True))