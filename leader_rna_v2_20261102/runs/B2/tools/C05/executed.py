import json
DATA=json.loads('{"mobility_dev.json": [{"condition": "B", "n_tracks": 279, "median_final_squared_displacement_um2": 1.596246372681656, "median_n_frames": 98.0, "top_100_by_max_displacement_median_final_squared_displacement_um2": 123.04789558444844}, {"condition": "A", "n_tracks": 838, "median_final_squared_displacement_um2": 0.6357464296597586, "median_n_frames": 159.0, "top_100_by_max_displacement_median_final_squared_displacement_um2": 19.582408620947668}], "phase_measurements.json": [{"phase": "dilute", "tie_line_id": 0, "point_index_in_series": 0, "reference_RNA_ng_per_uL": 27.48, "variant_RNA_ng_per_uL": 0.0, "wt_error_lower_ng_per_uL": 9.0684, "wt_error_upper_ng_per_uL": 9.0684, "mut_error_lower_ng_per_uL": 0.0, "mut_error_upper_ng_per_uL": 0.0}, {"phase": "dilute", "tie_line_id": 1, "point_index_in_series": 1, "reference_RNA_ng_per_uL": 53.68, "variant_RNA_ng_per_uL": 0.53, "wt_error_lower_ng_per_uL": 17.7144, "wt_error_upper_ng_per_uL": 17.7144, "mut_error_lower_ng_per_uL": 0.1749, "mut_error_upper_ng_per_uL": 0.1749}, {"phase": "dilute", "tie_line_id": 2, "point_index_in_series": 2, "reference_RNA_ng_per_uL": 92.98, "variant_RNA_ng_per_uL": 115.63, "wt_error_lower_ng_per_uL": 30.6834, "wt_error_upper_ng_per_uL": 30.6834, "mut_error_lower_ng_per_uL": 38.1579, "mut_error_upper_ng_per_uL": 38.1579}, {"phase": "dense", "tie_line_id": 0, "point_index_in_series": 0, "reference_RNA_ng_per_uL": 12893.0, "variant_RNA_ng_per_uL": 0.0, "wt_error_lower_ng_per_uL": 6446.5, "wt_error_upper_ng_per_uL": 12893.0, "mut_error_lower_ng_per_uL": 0.0, "mut_error_upper_ng_per_uL": 0.0}, {"phase": "dense", "tie_line_id": 1, "point_index_in_series": 1, "reference_RNA_ng_per_uL": 12805.0, "variant_RNA_ng_per_uL": 4787.0, "wt_error_lower_ng_per_uL": 6402.5, "wt_error_upper_ng_per_uL": 12805.0, "mut_error_lower_ng_per_uL": 2393.5, "mut_error_upper_ng_per_uL": 4787.0}, {"phase": "dense", "tie_line_id": 2, "point_index_in_series": 2, "reference_RNA_ng_per_uL": 48826.0, "variant_RNA_ng_per_uL": 20352.0, "wt_error_lower_ng_per_uL": 24413.0, "wt_error_upper_ng_per_uL": 48826.0, "mut_error_lower_ng_per_uL": 10176.0, "mut_error_upper_ng_per_uL": 20352.0}], "initial_measurements.json": [{"condition": "A", "time_h": 0.0, "mean_empty_area_fraction": 0.0148724491091024, "sem_empty_area_fraction": 0.0002437652793328, "n_fields": 7, "n_objects": 3490}, {"condition": "A", "time_h": 4.0, "mean_empty_area_fraction": 0.0054389893768169, "sem_empty_area_fraction": 0.0004851399860374, "n_fields": 7, "n_objects": 1201}, {"condition": "A", "time_h": 8.0, "mean_empty_area_fraction": 0.0044390495790911, "sem_empty_area_fraction": 0.0004738057874311, "n_fields": 7, "n_objects": 998}, {"condition": "A", "time_h": 12.0, "mean_empty_area_fraction": 0.0040641907190291, "sem_empty_area_fraction": 0.0004533639169051, "n_fields": 7, "n_objects": 937}, {"condition": "A", "time_h": 24.0, "mean_empty_area_fraction": 0.0044581874447536, "sem_empty_area_fraction": 0.0005448059632589, "n_fields": 7, "n_objects": 859}, {"condition": "B", "time_h": 0.0, "mean_empty_area_fraction": 0.0138090880510916, "sem_empty_area_fraction": 0.0002264511197326, "n_fields": 7, "n_objects": 3158}, {"condition": "B", "time_h": 4.0, "mean_empty_area_fraction": 0.0159150610393171, "sem_empty_area_fraction": 0.0011019283039892, "n_fields": 7, "n_objects": 564}, {"condition": "B", "time_h": 8.0, "mean_empty_area_fraction": 0.0239331148418327, "sem_empty_area_fraction": 0.0016049805499992, "n_fields": 7, "n_objects": 545}, {"condition": "B", "time_h": 12.0, "mean_empty_area_fraction": 0.0402799733501556, "sem_empty_area_fraction": 0.0031537325464317, "n_fields": 7, "n_objects": 496}, {"condition": "B", "time_h": 24.0, "mean_empty_area_fraction": 0.0891834703945908, "sem_empty_area_fraction": 0.0078546202289423, "n_fields": 7, "n_objects": 349}], "sequence_measurements.json": {"reference_sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCC", "reference_read_fraction": 0.9466, "other_reads": [{"sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA", "length_nt": 378, "read_fraction": 0.0265}, {"sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCCGTGCACACTCATAGCACTGTGCCTATCTCCTTTCGCGATGGAGACAGGCACAATGCTACGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGT", "length_nt": 205, "read_fraction": 0.0125}, {"sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGTCGGGATCCACGCGAGCACACTAGAGCCGCTGTACGACCCTTTCGCGATGGGTCATACAGCGACTCTAATGTGCAGCACAGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA", "length_nt": 498, "read_fraction": 0.0075}, {"sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGGGATTCCGTGCACACTCATCACGCTGTGCCTATCTCCTTTCGCGATGGAGACAGGCACAATGCTACGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGTCGGGATCCACGCGAGCACACTAGAGCCGCTGTACGACCCTTTCGCGATGGGTCATACAGCGACTCTAATGTGCAGCACAGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA", "length_nt": 608, "read_fraction": 0.0035}]}, "fraction_dev.json": [{"template_fraction": "M", "n_fields": 3, "median_field_mean_empty_fraction": 2.7853291144878946e-05, "field_mean_empty_fractions": [2.7853291144878946e-05, 0.00016496983408747812, 0.0]}, {"template_fraction": "M+L", "n_fields": 5, "median_field_mean_empty_fraction": 0.04445828743121418, "field_mean_empty_fractions": [0.042889071607366366, 0.06561580579976005, 0.057610926734964554, 0.029657181595508317, 0.04445828743121418]}, {"template_fraction": "M+S", "n_fields": 2, "median_field_mean_empty_fraction": 0.09412483585099253, "field_mean_empty_fractions": [0.05459724838435311, 0.13365242331763194]}]}')
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