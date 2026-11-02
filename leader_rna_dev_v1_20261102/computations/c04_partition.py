"""Actor-requested partition ratios and interval arithmetic, not statistical inference."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from coordinator import save,event

def main():
    data=json.loads((ROOT/'agent_visible/phase_measurements.json').read_text())
    grouped={(r['tie_line_id'],r['phase']):r for r in data};rows=[]
    for tie in [0,1,2]:
        for label,column,prefix in [('reference','reference_RNA_ng_per_uL','wt'),('variant','variant_RNA_ng_per_uL','mut')]:
            d=grouped[tie,'dense'];l=grouped[tie,'dilute'];num=d[column];den=l[column]
            nlo=num-d[prefix+'_error_lower_ng_per_uL'];nhi=num+d[prefix+'_error_upper_ng_per_uL']
            dlo=den-l[prefix+'_error_lower_ng_per_uL'];dhi=den+l[prefix+'_error_upper_ng_per_uL']
            if den==0:
                row=dict(tie_line_id=tie,species=label,partition_ratio=None,interval=None,status='undefined: zero dilute concentration (dense also zero)')
            else:
                row=dict(tie_line_id=tie,species=label,partition_ratio=num/den,interval=[max(nlo,0)/dhi,nhi/dlo] if dlo>0 else None,status='defined')
            rows.append(row)
    out=dict(compute_id='C04',request_source='transcripts/researcher_04.md',results=rows,interval_definition='Klo=(Cd−dense_lower_error)/(Cl+dilute_upper_error), Khi=(Cd+dense_upper_error)/(Cl−dilute_lower_error), provided positive denominator. These propagate the supplied marginal error ranges as a rectangle, not a statistical confidence interval. Correlations unknown; no joint coverage claim.',mechanism_limits='No phase volumes, matched concentrations inside cavities, time-resolved RNA yield or constitutive flux law supplied; ratios do not close dynamics or map to image area fractions.')
    save(ROOT/'computations/C04_result.json',out)
    event('computation_completed',dict(compute_id='C04',request='transcripts/researcher_04.md',script='computations/c04_partition.py',result='computations/C04_result.json',budget_unit=1))
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
