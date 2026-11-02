import json
D = DATA['phase_measurements.json']
by = {}
for row in D:
    by.setdefault(row['tie_line_id'], {})[row['phase']] = row
out = []
for tid in sorted(by):
    lo = by[tid]['dilute']; de = by[tid]['dense']
    item = {'tie_line_id': tid}
    ks = {}
    for name, key, elo, ehi in [('reference','reference_RNA_ng_per_uL','wt_error_lower_ng_per_uL','wt_error_upper_ng_per_uL'),('variant','variant_RNA_ng_per_uL','mut_error_lower_ng_per_uL','mut_error_upper_ng_per_uL')]:
        cl, cd = lo[key], de[key]
        dl, du = lo[elo], lo[ehi]
        Dl, Du = de[elo], de[ehi]
        item[name] = {'K': None, 'interval': None, 'status': 'undefined'}
        if cl > 0 and cd >= 0:
            klo_den = cl + du; khi_den = cl - dl
            K = cd/cl
            low = max(0.0, cd-Dl)/klo_den if klo_den > 0 else None
            high = (cd+Du)/khi_den if khi_den > 0 else None
            item[name] = {'K': K, 'interval': [low, high], 'status': 'defined' if high is not None else 'upper bound undefined: denominator interval reaches zero'}
            ks[name] = item[name]
        else:
            item[name]['status'] = 'undefined: zero/nonpositive dilute concentration'
    item['alpha'] = None
    if 'reference' in ks and 'variant' in ks:
        kr=ks['reference']['K']; kv=ks['variant']['K']
        krlo,krhi=ks['reference']['interval']; kvlo,kvhi=ks['variant']['interval']
        item['alpha']={'point':kv/kr,'interval':[kvlo/krhi,kvhi/krlo] if krlo>0 else None,'overlaps_one': (kvlo/krhi <= 1 <= kvhi/krlo) if krlo>0 else None}
    out.append(item)
print(json.dumps({'partition_selectivity':out,'checks':{'units':'K and alpha dimensionless','intervals':'rectangular propagation of supplied marginal bounds; not confidence intervals','tie_line_index':'not assumed to be composition order','cavity_mapping':'not available from phase concentrations alone'},'conditional_prediction':{'H1':'In an assay-matched mixture series at fixed reaction chemistry, alpha should decline with measured variant/reference RNA loading and cavity incidence/area should change with that loading if the proposed dilute-domain bridge is correct.','H0':'Carryover/reaction-state matching should explain cavity differences without requiring an alpha trend; composition variation alone need not reproduce the phenotype.'},'limits':['No phase volumes or cavity-local concentration mapping','No measured RNA mixture loading series','No time-resolved phase concentrations','No causal or statistical confidence claim']},sort_keys=True))