"""Requested source-schema check; inspect supplied measurement definitions at t=0."""
import json
import sys
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from coordinator import save,event
SRC=ROOT.parent/'real_case_blind_20261102/curator/sources'

def main():
    schemas={}
    for filename,sheets in [('rna_source_11.xlsx',['Fig1f_per_object','Fig1f_plotted']),('rna_source.xlsx',['Fig5c_per_object','Fig5d_per_object'])]:
        for sheet in sheets:
            schemas[sheet]=list(pd.read_excel(SRC/filename,sheet_name=sheet,nrows=0).columns)
    df=pd.read_excel(SRC/'rna_source_11.xlsx',sheet_name='Fig1f_per_object')
    df=df[df.timepoint==0]
    summary=[]
    for source,condition in [('WT','A'),('Mut','B')]:
        g=df[df.label==source]
        summary.append(dict(condition=condition,time_h=0,n_objects=len(g),arithmetic_mean_object_ratios=float(g['area ratios'].mean()),total_empty_over_total_filled=float(g['hollow area'].sum()/g.area_filled.sum())))
    out=dict(compute_id='C03',request_source='transcripts/researcher_03.md',availability='Per-object snapshots have area and timepoint but no persistent per-droplet trajectory ID or merge/split/exit flags. Fig5 tracks lack area/state. Requested longitudinal cavity-state decomposition unavailable.',schemas=schemas,definition_check=summary,definition_note='The supplied initial mean_area_ratio agrees with the arithmetic mean of individual object ratios, not the ratio of summed areas. Do not replace it by an area-weighted statistic. Only t=0 values used in this check; no reserved late-time measurements returned.')
    save(ROOT/'computations/C03_result.json',out)
    event('computation_completed',dict(compute_id='C03',request='transcripts/researcher_03.md',script='computations/c03_tracking_availability.py',result='computations/C03_result.json',budget_unit=1))
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
