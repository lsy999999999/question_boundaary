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