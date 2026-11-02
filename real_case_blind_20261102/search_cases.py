import concurrent.futures
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
QUERIES = [
    'Mpemba effect experiment',
    'memory hysteresis experiment',
    'anomalous relaxation experiment',
    'collective behavior bacteria mechanism',
    'cell adaptation unexpected mechanism',
    'oscillation chemical reaction experiment',
    'granular material memory experiment',
    'fluid droplet unexpected motion experiment',
    'ecological microbial community coexistence experiment',
    'behavior learning reversal mechanism experiment',
    'negative thermal expansion mechanism experiment',
    'active matter nonreciprocal experiment',
]

def abstract(inv):
    if not inv:
        return ''
    tokens = {i: word for word, positions in inv.items() for i in positions}
    return ' '.join(tokens.get(i, '') for i in range(max(tokens) + 1))

def search(q):
    url = 'https://api.openalex.org/works?' + urllib.parse.urlencode({
        'search': q,
        'filter': 'from_publication_date:2026-01-01,to_publication_date:2026-11-02,type:article',
        'per-page': 7,
    })
    rec = {'query': q, 'url': url, 'retrieved_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ScientificCaseReview/1.0'})
        with urllib.request.urlopen(req, timeout=40) as res:
            data = json.load(res)
        slug = re.sub('[^a-z0-9]+', '_', q.lower())
        (ROOT / 'curator/sources' / (slug + '.json')).write_text(json.dumps(data))
        rec['total'] = data['meta']['count']
        rec['results'] = [{
            'title': x['title'], 'date': x['publication_date'], 'doi': x.get('doi'),
            'id': x['id'], 'abstract': abstract(x.get('abstract_inverted_index')),
            'locations': [{'url': loc.get('landing_page_url'), 'pdf': loc.get('pdf_url'),
                           'venue': (loc.get('source') or {}).get('display_name')}
                          for loc in x['locations'][:4]],
        } for x in data['results']]
    except Exception as e:
        rec['error'] = str(e)
    print(json.dumps({'query': q, 'error': rec.get('error'),
                      'results': [{'title': x['title'], 'date': x['date'], 'doi': x['doi'],
                                   'venue': x['locations'][0].get('venue') if x['locations'] else None}
                                  for x in rec.get('results', [])]}, ensure_ascii=False), flush=True)
    return rec

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(search, QUERIES))
(ROOT / 'curator/SEARCH_RESULTS.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
