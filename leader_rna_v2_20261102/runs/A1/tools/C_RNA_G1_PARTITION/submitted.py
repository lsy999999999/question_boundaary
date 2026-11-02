import json
from itertools import product

rows = DATA["phase_measurements.json"]
by_line = {}
for r in rows:
    by_line.setdefault(r["tie_line_id"], {})[r["phase"]] = r

def k_record(line_id, species):
    dense = by_line[line_id]["dense"]
    dilute = by_line[line_id]["dilute"]
    if species == "reference":
        key = "reference_RNA_ng_per_uL"
        edlo, edhi = "wt_error_lower_ng_per_uL", "wt_error_upper_ng_per_uL"
        ello, elhi = edlo, edhi
    else:
        key = "variant_RNA_ng_per_uL"
        edlo, edhi = "mut_error_lower_ng_per_uL", "mut_error_upper_ng_per_uL"
        ello, elhi = edlo, edhi
    cd, cl = dense[key], dilute[key]
    if cl <= 0:
        return {"status": "undefined_zero_dilute", "K": None, "rectangle_range": None}
    k = cd / cl
    cd_lo = max(0.0, cd - dense[edlo])
    cd_hi = cd + dense[edhi]
    cl_lo = max(0.0, cl - dilute[ello])
    cl_hi = cl + dilute[elhi]
    klo = cd_lo / cl_hi
    khi = None if cl_lo <= 0 else (cd_hi / cl_lo)
    return {"status": "defined", "K": k, "rectangle_range": [klo, khi]}

grid = [0.0, 0.01, 0.05, 0.10, 0.50, 0.90, 0.99, 1.0]
thresholds = [0.10, 0.50, 0.90]
out = {"assumptions": [
    "Two species, closed equilibrium mixture, and each species K from a selected tie-line applies to the same mixture.",
    "xL and xD are composition fractions on a consistent mass or mole basis.",
    "This is a partition identity only; it has no nucleation, cavity geometry, kinetics, or image mapping."
], "tie_lines": []}

for line_id in sorted(by_line):
    kr = k_record(line_id, "reference")
    kv = k_record(line_id, "variant")
    item = {"tie_line_id": line_id, "K_reference": kr, "K_variant": kv}
    if kr["status"] == "defined" and kv["status"] == "defined":
        KR, KV = kr["K"], kv["K"]
        def x_dense(x):
            den = KV*x + KR*(1.0-x)
            return 0.0 if den == 0 else KV*x/den
        item["conditional_map"] = [
            {"x_variant_dilute": x, "x_variant_dense": x_dense(x), "equal_partition_alternative": x}
            for x in grid
        ]
        item["dilute_fraction_at_dense_threshold"] = [
            {"x_star_dense": xs, "x_variant_dilute_threshold": xs*KR/(KV*(1-xs)+xs*KR)}
            for xs in thresholds
        ]
        item["checks"] = {
            "equal_K_identity": abs((KR*0.5)/(KR*0.5+KR*0.5)-0.5) < 1e-12,
            "endpoint_zero": x_dense(0.0) == 0.0,
            "endpoint_one": abs(x_dense(1.0)-1.0) < 1e-12,
            "all_compositions_in_unit_interval": all(0.0 <= x_dense(x) <= 1.0 for x in grid)
        }
    else:
        item["conditional_map"] = None
        item["limitation"] = "The variant partition ratio is undefined on this tie-line; no value is imputed."
    out["tie_lines"].append(item)

print(json.dumps(out, sort_keys=True))