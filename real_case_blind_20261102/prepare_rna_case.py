"""Extract measured data only. Keep fitted theory and the answer in curator/."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
SRC = ROOT / 'curator/sources'
EVIDENCE = ROOT / 'curator/evidence'
PUBLIC = ROOT / 'agent_workspace'
EVIDENCE.mkdir(exist_ok=True)

def save(name, data, folder=EVIDENCE):
    (folder / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

time = pd.read_excel(SRC/'rna_source_11.xlsx', sheet_name='Fig1f_plotted')
rows = []
for old, new in [('WT','A'),('Mut','B')]:
    group = time[time.label == old]
    for target in [0,4,8,12,24,36,48]:
        row = group.loc[(group.timepoint-target).abs().idxmin()]
        rows.append({'condition':new, 'time_h':float(row.timepoint),
                     'mean_empty_area_fraction':float(row.mean_area_ratio),
                     'sem_empty_area_fraction':float(row.sem_area_ratio),
                     'n_fields':int(row.n_FOV),'n_objects':int(row.n_droplets)})
save('initial_measurements.json', rows, PUBLIC)

fractions = pd.read_excel(SRC/'rna_fig2.xlsx', sheet_name='Fig2c_per_object')
f = fractions[['label','replicate','image_ID','area_filled','hollow area','% hollow area','radius']].copy()
f.columns = ['template_fraction','replicate','field_id','droplet_area_um2','empty_area_um2','empty_fraction','radius_um']
# Retain source label, rather than the inconsistent abbreviations in condition.
f.field_id = pd.factorize(f.field_id)[0]
f.to_csv(EVIDENCE/'fraction_measurements.csv', index=False)
dev = f[f.replicate == 'Replicate 1'].copy()
held = f[f.replicate == 'Replicate 2'].copy()
if dev.empty or held.empty:
    raise ValueError('Expected two whole-replicate partitions')
def fraction_summary(frame):
    fields = frame.groupby(['template_fraction','field_id']).empty_fraction.mean().reset_index()
    return [{'template_fraction':label,'n_fields':len(g),
             'median_field_mean_empty_fraction':float(g.empty_fraction.median()),
             'field_mean_empty_fractions':g.empty_fraction.tolist()}
            for label,g in fields.groupby('template_fraction')]
save('fraction_dev.json', fraction_summary(dev))
save('fraction_heldout.json', fraction_summary(held))
size = []
for label,g in held.groupby('template_fraction'):
    for low, high in [(0,15),(15,25),(25,1e9)]:
        s=g[(g.radius_um>low)&(g.radius_um<=high)]
        size.append({'template_fraction':label,'radius_lower_exclusive_um':low,
                     'radius_upper_inclusive_um':None if high>1e8 else high,
                     'n':len(s),'median_empty_fraction':float(s.empty_fraction.median()) if len(s) else None})
save('size_heldout.json',size)

sequences = pd.read_excel(SRC/'rna_source_4.xlsx', sheet_name='Mut sequencing reads', header=3)
reference = pd.read_excel(SRC/'rna_source_4.xlsx', sheet_name='DNA templates', header=3)
save('sequence_measurements.json', {'reference_sequence':reference.iloc[0]['Full sequence (5\'→3\')'],
    'reference_read_fraction':0.9466,
    'other_reads': [{'sequence':str(r['Full sequence (5\'→3\')']),
                     'length_nt':int(r['Length (nt)']), 'read_fraction':float(r['% of reads'])}
                    for _,r in sequences.dropna(subset=['Length (nt)']).iterrows()]})

phase = pd.read_excel(SRC/'rna_source_13.xlsx', sheet_name='Fig4b_experiment')
phase=phase.rename(columns={'wt_rna_ng_per_uL':'reference_RNA_ng_per_uL','mut_rna_ng_per_uL':'variant_RNA_ng_per_uL'})
save('phase_measurements.json',phase.to_dict('records'))

motion = pd.read_excel(SRC/'rna_source.xlsx', sheet_name='Fig5c_per_object')
def mobility_summary(frame):
    output=[]
    for label,g in frame.groupby('label'):
        output.append({'condition': {'WT':'A','Mut':'B'}[label], 'n_tracks':len(g),
            'median_final_squared_displacement_um2':float(g.final_sd_um2.median()),
            'median_n_frames':float(g.n_timepoints.median()),
            'top_100_by_max_displacement_median_final_squared_displacement_um2':float(g.nlargest(100,'max_sd_um2').final_sd_um2.median())})
    return output
save('mobility_dev.json',mobility_summary(motion[motion.replicate=='rep1']))
save('mobility_heldout.json',mobility_summary(motion[motion.replicate=='rep2']))

angle = pd.read_excel(SRC/'rna_source.xlsx', sheet_name='Fig5d_per_object')
for rep, suffix in [('rep1','dev'),('rep2','heldout')]:
    a=angle[(angle.replicate==rep)&(angle.delta_roi_length>1.0)&(angle.delta_vector_length>0)&np.isfinite(angle.cos_angle)].copy()
    # Recompute angle from underlying vector components, do not consume author angles.
    dot=a.delta_roi_x*a.delta_vector_x+a.delta_roi_y*a.delta_vector_y
    cosine=dot/(a.delta_roi_length*a.delta_vector_length)
    deg=np.degrees(np.arccos(np.clip(cosine,-1,1)))
    result={'replicate':rep,'minimum_droplet_step_um_exclusive':1.0,'n_steps':len(a),
            'median_angle_deg':float(np.median(deg)),'fraction_angle_gt_90':float(np.mean(deg>90)),
            'n_tracks':int(a.track_uid.nunique()),'n_fields':int(a.field_of_view.nunique()),
            'definition':'angle between droplet-centre displacement and change of cavity-centre position relative to droplet centre',
            'histogram_30deg_counts':np.histogram(deg,bins=np.arange(0,181,30))[0].tolist()}
    save('angles_'+suffix+'.json',result)
    a[['track_uid','field_of_view','time','delta_roi_x','delta_roi_y','delta_vector_x','delta_vector_y']].to_csv(EVIDENCE/('angle_vectors_'+suffix+'.csv'),index=False)

manifest=[]
for p in sorted(EVIDENCE.glob('*')):
    manifest.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
save('EVIDENCE_MANIFEST.json',manifest,ROOT/'curator')
print(json.dumps({'initial_rows':len(rows),'fractions_dev':fraction_summary(dev),'fractions_heldout':fraction_summary(held)},ensure_ascii=False))
