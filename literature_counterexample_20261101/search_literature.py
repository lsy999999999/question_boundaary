import urllib.request,urllib.parse,json,concurrent.futures,re
from pathlib import Path
root=Path(__file__).parent
queries=['BoxingGym','Automated Hypothesis Validation with Agentic Sequential Falsification','Hypothesis Generation with Large Language Models','LLM scientific hypothesis refinement counterexamples','large language models scientific experiment design model discovery','AI Newton scientific discovery','DiscoveryWorld','DiscoveryBench','Learning programs by learning from failures','Discrimination among mechanistic models','Strong inference Platt','Automating scientific discovery language models symbolic regression','From Hypotheses to Data-Driven Hypotheses Discovery','A Method for Automating Scientific Discovery','AI co-scientist','The automation of science King','FunSearch mathematical discoveries']
def abstract(inv):
 if not inv:return ''
 v={i:w for w,ii in inv.items() for i in ii};return ' '.join(v.get(i,'') for i in range(max(v)+1))
def one(q):
 u='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'per-page':5})
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'ResearchReview/1.0'})
  with urllib.request.urlopen(req,timeout=35) as r:d=json.load(r)
  slug=re.sub('[^a-z0-9]+','_',q.lower()).strip('_');(root/'raw'/(slug+'.json')).write_text(json.dumps(d))
  out=[]
  for x in d['results']:
   out.append(dict(title=x['title'],year=x['publication_year'],doi=x['doi'],id=x['id'],locations=[dict(url=y.get('landing_page_url'),pdf=y.get('pdf_url'),venue=(y.get('source') or {}).get('display_name')) for y in x['locations'][:5]],abstract=abstract(x.get('abstract_inverted_index'))))
  return dict(query=q,total=d['meta']['count'],results=out)
 except Exception as e:return dict(query=q,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:out=list(ex.map(one,queries))
(root/'SEARCH_RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for row in out:
 print('\nQUERY',row['query'],row.get('error',''))
 for x in row.get('results',[])[:4]:print(json.dumps({k:v for k,v in x.items() if k!='abstract'},ensure_ascii=False))
