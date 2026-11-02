import json
def solve(e, r):
    dr=e['ref_l']-e['ref_d']; dv=e['var_l']-e['var_d']
    den=r*dr-dv; num=e['var_d']-r*e['ref_d']
    if abs(den)<1e-12:
        return {'phi_l':None,'status':'underdetermined 0/0' if abs(num)<1e-12 else 'no solution: zero denominator, nonzero numerator','numerator':num,'denominator':den}
    phi=num/den
    if not (0<=phi<=1): return {'phi_l':phi,'status':'incompatible'}
    ref=e['ref_d']+phi*dr; var=e['var_d']+phi*dv
    return {'phi_l':phi,'status':'identified by both-species balance','mass_ratio_reconstructed':var/ref,'mass_ratio_residual':abs(var/ref-r),'M_ref_ng_at_1uL':ref,'M_var_ng_at_1uL':var}
cases=[('equal_K_match',{'ref_d':10.,'ref_l':1.,'var_d':20.,'var_l':2.},2.),('equal_K_mismatch',{'ref_d':10.,'ref_l':1.,'var_d':20.,'var_l':2.},1.),('same_concentration_each_phase',{'ref_d':10.,'ref_l':10.,'var_d':2.,'var_l':2.},0.2)]
out=[]
for name,e,r in cases: out.append({'case':name,'endpoints_ng_per_uL':e,'r':r,**solve(e,r)})
out.append({'case':'units','statement':'1 uL * ng/uL = ng; ratios and phase fractions dimensionless'})
print(json.dumps(out,sort_keys=True))