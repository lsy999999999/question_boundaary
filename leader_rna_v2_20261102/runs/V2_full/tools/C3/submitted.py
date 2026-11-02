import json, math
rows=[]
for tau in (1.0,5.0,20.0):
 for alpha in (0.5,1.0,2.0):
  for name,r,duration in (("fast",0.2,5.0),("slow",0.05,20.0)):
   x=alpha*r*tau*(1-math.exp(-duration/tau)); xs=alpha*r*tau; xc=0.5; tc=None
   if xs>xc:
    candidate=-tau*math.log(1-xc/xs)
    if candidate<=duration: tc=candidate
   rows.append({"tau_h":tau,"alpha":alpha,"schedule":name,"r_per_h":r,"duration_h":duration,"integrated_r":r*duration,"x_end":x,"steady_x":xs,"crossed":x>=xc,"crossing_time_h":tc,"units":"alpha*r and x/tau are h^-1"})
print(json.dumps({"assumptions":{"x0":0,"xc":0.5},"rows":rows,"all_integrals_equal_one":all(abs(z["integrated_r"]-1)<1e-12 for z in rows),"nonnegative_x":all(z["x_end"]>=0 for z in rows),"alternative":"equilibrium predicts no schedule effect after composition match and equilibration","status":"conditional hypothetical; not fitted or empirical"},sort_keys=True))