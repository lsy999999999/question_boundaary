import json
DATA=json.loads('{"initial_measurements.json": [{"condition": "A", "time_h": 0.0, "mean_empty_area_fraction": 0.0148724491091024, "sem_empty_area_fraction": 0.0002437652793328, "n_fields": 7, "n_objects": 3490}, {"condition": "A", "time_h": 4.0, "mean_empty_area_fraction": 0.0054389893768169, "sem_empty_area_fraction": 0.0004851399860374, "n_fields": 7, "n_objects": 1201}, {"condition": "A", "time_h": 8.0, "mean_empty_area_fraction": 0.0044390495790911, "sem_empty_area_fraction": 0.0004738057874311, "n_fields": 7, "n_objects": 998}, {"condition": "A", "time_h": 12.0, "mean_empty_area_fraction": 0.0040641907190291, "sem_empty_area_fraction": 0.0004533639169051, "n_fields": 7, "n_objects": 937}, {"condition": "A", "time_h": 24.0, "mean_empty_area_fraction": 0.0044581874447536, "sem_empty_area_fraction": 0.0005448059632589, "n_fields": 7, "n_objects": 859}, {"condition": "B", "time_h": 0.0, "mean_empty_area_fraction": 0.0138090880510916, "sem_empty_area_fraction": 0.0002264511197326, "n_fields": 7, "n_objects": 3158}, {"condition": "B", "time_h": 4.0, "mean_empty_area_fraction": 0.0159150610393171, "sem_empty_area_fraction": 0.0011019283039892, "n_fields": 7, "n_objects": 564}, {"condition": "B", "time_h": 8.0, "mean_empty_area_fraction": 0.0239331148418327, "sem_empty_area_fraction": 0.0016049805499992, "n_fields": 7, "n_objects": 545}, {"condition": "B", "time_h": 12.0, "mean_empty_area_fraction": 0.0402799733501556, "sem_empty_area_fraction": 0.0031537325464317, "n_fields": 7, "n_objects": 496}, {"condition": "B", "time_h": 24.0, "mean_empty_area_fraction": 0.0891834703945908, "sem_empty_area_fraction": 0.0078546202289423, "n_fields": 7, "n_objects": 349}]}')
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
