import json
DATA=json.loads('{"mobility_dev.json": [{"condition": "B", "n_tracks": 279, "median_final_squared_displacement_um2": 1.596246372681656, "median_n_frames": 98.0, "top_100_by_max_displacement_median_final_squared_displacement_um2": 123.04789558444844}, {"condition": "A", "n_tracks": 838, "median_final_squared_displacement_um2": 0.6357464296597586, "median_n_frames": 159.0, "top_100_by_max_displacement_median_final_squared_displacement_um2": 19.582408620947668}], "phase_measurements.json": [{"phase": "dilute", "tie_line_id": 0, "point_index_in_series": 0, "reference_RNA_ng_per_uL": 27.48, "variant_RNA_ng_per_uL": 0.0, "wt_error_lower_ng_per_uL": 9.0684, "wt_error_upper_ng_per_uL": 9.0684, "mut_error_lower_ng_per_uL": 0.0, "mut_error_upper_ng_per_uL": 0.0}, {"phase": "dilute", "tie_line_id": 1, "point_index_in_series": 1, "reference_RNA_ng_per_uL": 53.68, "variant_RNA_ng_per_uL": 0.53, "wt_error_lower_ng_per_uL": 17.7144, "wt_error_upper_ng_per_uL": 17.7144, "mut_error_lower_ng_per_uL": 0.1749, "mut_error_upper_ng_per_uL": 0.1749}, {"phase": "dilute", "tie_line_id": 2, "point_index_in_series": 2, "reference_RNA_ng_per_uL": 92.98, "variant_RNA_ng_per_uL": 115.63, "wt_error_lower_ng_per_uL": 30.6834, "wt_error_upper_ng_per_uL": 30.6834, "mut_error_lower_ng_per_uL": 38.1579, "mut_error_upper_ng_per_uL": 38.1579}, {"phase": "dense", "tie_line_id": 0, "point_index_in_series": 0, "reference_RNA_ng_per_uL": 12893.0, "variant_RNA_ng_per_uL": 0.0, "wt_error_lower_ng_per_uL": 6446.5, "wt_error_upper_ng_per_uL": 12893.0, "mut_error_lower_ng_per_uL": 0.0, "mut_error_upper_ng_per_uL": 0.0}, {"phase": "dense", "tie_line_id": 1, "point_index_in_series": 1, "reference_RNA_ng_per_uL": 12805.0, "variant_RNA_ng_per_uL": 4787.0, "wt_error_lower_ng_per_uL": 6402.5, "wt_error_upper_ng_per_uL": 12805.0, "mut_error_lower_ng_per_uL": 2393.5, "mut_error_upper_ng_per_uL": 4787.0}, {"phase": "dense", "tie_line_id": 2, "point_index_in_series": 2, "reference_RNA_ng_per_uL": 48826.0, "variant_RNA_ng_per_uL": 20352.0, "wt_error_lower_ng_per_uL": 24413.0, "wt_error_upper_ng_per_uL": 48826.0, "mut_error_lower_ng_per_uL": 10176.0, "mut_error_upper_ng_per_uL": 20352.0}], "initial_measurements.json": [{"condition": "A", "time_h": 0.0, "mean_empty_area_fraction": 0.0148724491091024, "sem_empty_area_fraction": 0.0002437652793328, "n_fields": 7, "n_objects": 3490}, {"condition": "A", "time_h": 4.0, "mean_empty_area_fraction": 0.0054389893768169, "sem_empty_area_fraction": 0.0004851399860374, "n_fields": 7, "n_objects": 1201}, {"condition": "A", "time_h": 8.0, "mean_empty_area_fraction": 0.0044390495790911, "sem_empty_area_fraction": 0.0004738057874311, "n_fields": 7, "n_objects": 998}, {"condition": "A", "time_h": 12.0, "mean_empty_area_fraction": 0.0040641907190291, "sem_empty_area_fraction": 0.0004533639169051, "n_fields": 7, "n_objects": 937}, {"condition": "A", "time_h": 24.0, "mean_empty_area_fraction": 0.0044581874447536, "sem_empty_area_fraction": 0.0005448059632589, "n_fields": 7, "n_objects": 859}, {"condition": "B", "time_h": 0.0, "mean_empty_area_fraction": 0.0138090880510916, "sem_empty_area_fraction": 0.0002264511197326, "n_fields": 7, "n_objects": 3158}, {"condition": "B", "time_h": 4.0, "mean_empty_area_fraction": 0.0159150610393171, "sem_empty_area_fraction": 0.0011019283039892, "n_fields": 7, "n_objects": 564}, {"condition": "B", "time_h": 8.0, "mean_empty_area_fraction": 0.0239331148418327, "sem_empty_area_fraction": 0.0016049805499992, "n_fields": 7, "n_objects": 545}, {"condition": "B", "time_h": 12.0, "mean_empty_area_fraction": 0.0402799733501556, "sem_empty_area_fraction": 0.0031537325464317, "n_fields": 7, "n_objects": 496}, {"condition": "B", "time_h": 24.0, "mean_empty_area_fraction": 0.0891834703945908, "sem_empty_area_fraction": 0.0078546202289423, "n_fields": 7, "n_objects": 349}], "sequence_measurements.json": {"reference_sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCC", "reference_read_fraction": 0.9466, "other_reads": [{"sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA", "length_nt": 378, "read_fraction": 0.0265}, {"sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCCGTGCACACTCATAGCACTGTGCCTATCTCCTTTCGCGATGGAGACAGGCACAATGCTACGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGT", "length_nt": 205, "read_fraction": 0.0125}, {"sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGTCGGGATCCACGCGAGCACACTAGAGCCGCTGTACGACCCTTTCGCGATGGGTCATACAGCGACTCTAATGTGCAGCACAGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA", "length_nt": 498, "read_fraction": 0.0075}, {"sequence": "GGGCATTCTAATACGACTCACTATAGGACCGTCAGAGGACACGGTTAAAAAGTCCTCATTCGTGGCCGCATCGCGAAAGCGGCCACGGGATTCTGTGCTGCACATTAGAGTCGCTGTATGACCCATCGCGAAAGGGTCGTACAGCGGCTCTAGTGTGCTCGCGTGGATCCCGACTGGCACCATCGCGAAAGGTGCCAGGTAACGAATGGATCCACGCGTCACTCGTAGCATTGTGCCTGTCTCCATCGCGAAAGGAGATAGGCACAGTGCTATGAGTGTGCACGGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGGGATTCCGTGCACACTCATCACGCTGTGCCTATCTCCTTTCGCGATGGAGACAGGCACAATGCTACGAGTGACGCGTGGATCCATTCGTTACCTGGCACCTTTCGCGATGGTGCCAGTCGGGATCCACGCGAGCACACTAGAGCCGCTGTACGACCCTTTCGCGATGGGTCATACAGCGACTCTAATGTGCAGCACAGAATCCCGTGGCCGCTTTCGCGATGCGGCCACGAATGAGGACTTTTTAACCGTGTCCTCTGACGGTCCTATAGTGAGTCGTATTAGAATGCCCA", "length_nt": 608, "read_fraction": 0.0035}]}, "fraction_dev.json": [{"template_fraction": "M", "n_fields": 3, "median_field_mean_empty_fraction": 2.7853291144878946e-05, "field_mean_empty_fractions": [2.7853291144878946e-05, 0.00016496983408747812, 0.0]}, {"template_fraction": "M+L", "n_fields": 5, "median_field_mean_empty_fraction": 0.04445828743121418, "field_mean_empty_fractions": [0.042889071607366366, 0.06561580579976005, 0.057610926734964554, 0.029657181595508317, 0.04445828743121418]}, {"template_fraction": "M+S", "n_fields": 2, "median_field_mean_empty_fraction": 0.09412483585099253, "field_mean_empty_fractions": [0.05459724838435311, 0.13365242331763194]}]}')
import itertools, json, math
rows = DATA['phase_measurements.json']
phases = {r['tie_line_id']: {} for r in rows}
for row in rows:
    phases[row['tie_line_id']][row['phase']] = row

def endpoints(tid, corner=None):
    out = {}
    for phase, suffix in [('dense', 'd'), ('dilute', 'l')]:
        row = phases[tid][phase]
        for species, key, lo_key, hi_key in [('ref', 'reference_RNA_ng_per_uL', 'wt_error_lower_ng_per_uL', 'wt_error_upper_ng_per_uL'), ('var', 'variant_RNA_ng_per_uL', 'mut_error_lower_ng_per_uL', 'mut_error_upper_ng_per_uL')]:
            val = row[key]
            if corner is not None:
                bit = corner[(phase, species)]
                val = val - row[lo_key] if bit == 0 else val + row[hi_key]
            out[species + '_' + suffix] = val
    return out

def kval(c_dense, c_dilute):
    return None if c_dilute == 0 else c_dense / c_dilute

def lever(e, x):
    if x == 1.0:
        # Variant-only mass balance: phi_l*C_var,l+(1-phi_l)*C_var,d is unconstrained by a reference species.
        return {'phi_l': None, 'status': 'variant-only endpoint underdetermined without total concentration'}
    if x == 0.0:
        # Reference-only mass balance cannot determine the absent variant partition.
        return {'phi_l': None, 'status': 'reference-only endpoint underdetermined without total concentration'}
    r = x/(1.0-x)
    delta_ref = e['ref_l']-e['ref_d']
    delta_var = e['var_l']-e['var_d']
    den = r*delta_ref-delta_var
    num = e['var_d']-r*e['ref_d']
    if abs(den) < 1e-15:
        return {'phi_l': None, 'status': 'degenerate denominator'}
    phi = num/den
    if not (0.0 <= phi <= 1.0):
        return {'phi_l': phi, 'status': 'incompatible with this fixed tie-line'}
    # Normalize total mass to one; concentrations are then scaled by a common factor.
    total = e['ref_d']+phi*delta_ref + e['var_d']+phi*delta_var
    mref = (e['ref_d']+phi*delta_ref)/total
    mvar = (e['var_d']+phi*delta_var)/total
    return {'phi_l': phi, 'status': 'valid', 'mass_fraction_residual': max(abs(mref-(1-x)), abs(mvar-x))}

out = {'equation': 'r=[C_var,d+phi_l*(C_var,l-C_var,d)]/[C_ref,d+phi_l*(C_ref,l-C_ref,d)]; r=x_var/(1-x_var)', 'units_check': 'uL*ng/uL=ng; r, x_var, phi_l dimensionless', 'tie_lines': []}
for tid in sorted(phases):
    e = endpoints(tid)
    kr = kval(e['ref_d'], e['ref_l'])
    kv = kval(e['var_d'], e['var_l'])
    record = {'tie_line_id': tid, 'central_endpoints_ng_per_uL': e, 'K_ref_dense_over_dilute': kr, 'K_var_dense_over_dilute': kv, 'K_var_over_K_ref': None if kr is None or kv is None or kr == 0 else kv/kr, 'central_curve': [], 'corner_valid_phi_ranges': {}, 'corner_invalid_count': {}, 'corner_count': 16}
    for j in range(11):
        x = j/10
        record['central_curve'].append({'x_var_mass_fraction': x, **lever(e, x)})
    for j in range(1,10):
        x = j/10
        valid, invalid = [], 0
        for bits in itertools.product((0,1), repeat=4):
            # bits order: dense-ref, dense-var, dilute-ref, dilute-var
            corner = {('dense','ref'):bits[0], ('dense','var'):bits[1], ('dilute','ref'):bits[2], ('dilute','var'):bits[3]}
            result = lever(endpoints(tid, corner), x)
            if result['status'] == 'valid': valid.append(result['phi_l'])
            else: invalid += 1
        record['corner_valid_phi_ranges'][str(x)] = None if not valid else [min(valid), max(valid)]
        record['corner_invalid_count'][str(x)] = invalid
    out['tie_lines'].append(record)
out['interpretation_checks'] = {'partition_preference_varies_across_tie_lines': True, 'cavity_mapping': 'not identifiable from these inputs; phi_l is not f'}
print(json.dumps(out, sort_keys=True))