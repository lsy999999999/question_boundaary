import urllib.request,json,concurrent.futures,time,re
from pathlib import Path
from html.parser import HTMLParser
root=Path(__file__).parent
urls={
'boxing_abs':'https://arxiv.org/abs/2501.01540',
'boxing_full':'https://arxiv.org/html/2501.01540',
'popper_abs':'https://arxiv.org/abs/2502.09858',
'popper_full':'https://arxiv.org/html/2502.09858',
'hypogenic_acl':'https://aclanthology.org/2024.nlp4science-1.10/',
'discoverybench_abs':'https://arxiv.org/abs/2407.01725',
'discoveryworld_abs':'https://arxiv.org/abs/2406.06769',
'newton_abs':'https://arxiv.org/abs/2504.01538',
'newton_aps':'https://journals.aps.org/prresearch/abstract/10.1103/dvvc-4rsr',
'newton_crossref':'https://api.crossref.org/works/10.1103/dvvc-4rsr',
'cegis_ml':'https://link.springer.com/article/10.1007/s10994-020-05934-z',
'co_scientist_abs':'https://arxiv.org/abs/2502.18864',
'funsearch_nature':'https://www.nature.com/articles/s41586-023-06924-6',
'ai_descartes_nature':'https://www.nature.com/articles/s41467-023-37236-y',
'latest_model_discovery':'https://arxiv.org/abs/2608.09696',
'latest_bayesian':'https://arxiv.org/abs/2610.25747',
'latest_evobelief':'https://arxiv.org/abs/2610.12789',
'concept_counterexamples':'https://arxiv.org/abs/2502.10454',
'platt_crossref':'https://api.crossref.org/works/10.1126/science.146.3642.347',
'box_hill_crossref':'https://api.crossref.org/works?query.title=Discrimination%20among%20mechanistic%20models&rows=2',
'robot_crossref':'https://api.crossref.org/works?query.title=The%20Automation%20of%20Science&filter=from-pub-date:2009-01-01,until-pub-date:2009-12-31&rows=2',
'boxing_openreview':'https://api2.openreview.net/notes/search?term=BoxingGym&limit=5',
'popper_dblp':'https://dblp.org/search/publ/api?q=Automated%20Hypothesis%20Validation&format=json&h=5',
'boxing_dblp':'https://dblp.org/search/publ/api?q=BoxingGym&format=json&h=5',
}
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ['script','style','noscript']:self.skip+=1
  if not self.skip and t in ['p','div','section','article','h1','h2','h3','h4','li','tr','br']:self.parts.append('\n')
 def handle_endtag(self,t):
  if t in ['script','style','noscript'] and self.skip:self.skip-=1
  if not self.skip and t in ['p','div','section','article','h1','h2','h3','h4','li','tr']:self.parts.append('\n')
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def get(item):
 k,u=item;record={'key':k,'requested_url':u,'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (compatible; AcademicLiteratureReview/1.0)'})
  with urllib.request.urlopen(req,timeout=40) as r:body=r.read();record.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'))
  suffix='.json' if ('json' in (record['content_type'] or '') or k.endswith('_crossref') or k.endswith('_dblp') or k.endswith('_openreview')) else '.html'
  (root/'raw'/(k+suffix)).write_bytes(body)
  if suffix=='.html':
   p=Text();p.feed(body.decode(errors='replace'));plain=re.sub(r'[ \t]+',' ',''.join(p.parts));plain=re.sub(r'\n\s*\n','\n\n',plain);(root/'raw'/(k+'.txt')).write_text(plain)
  record['bytes']=len(body)
 except Exception as e:record['error']=str(e)
 print(json.dumps(record),flush=True);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(get,urls.items()))
(root/'FETCH_LOG.json').write_text(json.dumps(results,indent=2))
