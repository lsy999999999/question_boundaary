import concurrent.futures
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
CUTOFF = '2025-05-12'
FORBIDDEN = ['s44286-026-00454-4', 'chemrxiv-2025-5ffnn', 'genetic encoding and mutagenesis of rna droplet phenotypes']
QUERIES = sys.argv[1:]

def abstract(inv):
    tokens={i:w for w,positions in (inv or {}).items() for i in positions}
    return ' '.join(tokens.get(i,'') for i in range(max(tokens)+1)) if tokens else ''

def search(q):
    url='https://api.openalex.org/works?'+urllib.parse.urlencode({
        'search':q,'filter':f'to_publication_date:{CUTOFF},type:article','per-page':6})
    record={'query':q,'cutoff':CUTOFF,'url':url,'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    with urllib.request.urlopen(url,timeout=40) as r:data=json.load(r)
    slug=re.sub('[^a-z0-9]+','_',q.lower()).strip('_')[:100]
    (ROOT/'curator/sources'/('historical_'+slug+'.json')).write_text(json.dumps(data))
    allowed=[]; rejected=[]
    for x in data['results']:
        entry={'title':x['title'],'publication_date':x['publication_date'],'doi':x.get('doi'),
               'venue':((x.get('primary_location') or {}).get('source') or {}).get('display_name'),
               'abstract':abstract(x.get('abstract_inverted_index'))}
        text=json.dumps(entry).lower()
        if x['publication_date']>CUTOFF or any(f in text for f in FORBIDDEN):
            rejected.append({'title':x['title'],'reason':'date or target-study exclusion'})
        else:allowed.append(entry)
    record.update(results=allowed[:4],rejected=rejected)
    return record

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    records=list(pool.map(search,QUERIES))
path=ROOT/'agent_workspace/historical_results_01.json'
if path.exists():raise SystemExit('Refuse to overwrite search responses')
path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(records,ensure_ascii=False,indent=2))
