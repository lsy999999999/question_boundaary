import json
rows=DATA['phase_measurements.json']
g={(r['tie_line_id'],r['phase']):r for r in rows}
out=[]
for tie in range(3):
 for label,col,prefix in [('reference','reference_RNA_ng_per_uL','wt'),('variant','variant_RNA_ng_per_uL','mut')]:
  d,l=g[tie,'dense'],g[tie,'dilute']
  den=l[col]
  lo=(d[col]-d[prefix+'_error_lower_ng_per_uL'])/(den+l[prefix+'_error_upper_ng_per_uL']) if den else None
  hi=(d[col]+d[prefix+'_error_upper_ng_per_uL'])/(den-l[prefix+'_error_lower_ng_per_uL']) if den else None
  out.append(dict(tie_line_id=tie,species=label,partition_ratio=d[col]/den if den else None,interval=[lo,hi] if den else None))
print(json.dumps(out))
