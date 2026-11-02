import concurrent.futures
import json
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent / 'curator'
URLS = {
    'granular_nhess': 'https://nhess.copernicus.org/articles/26/5315/2026/',
    'droplet_natcomm': 'https://www.nature.com/articles/s41467-026-69481-2',
    'zebrafish_natcomm': 'https://www.nature.com/articles/s41467-026-74872-6',
    'microalgae_sciadv': 'https://www.science.org/doi/10.1126/sciadv.aea5313',
    'membrane_advscience': 'https://advanced.onlinelibrary.wiley.com/doi/10.1002/advs.77877',
    'ecology_natcomm': 'https://www.nature.com/articles/s41467-026-69151-3',
    'belief_scirep': 'https://www.nature.com/articles/s41598-026-48064-7',
    'cooling_rsc': 'https://pubs.rsc.org/en/content/articlehtml/2026/lf/d5lf00296f',
}

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'): self.skip += 1
        if not self.skip and tag in ('p','div','section','h1','h2','h3','h4','li','tr','br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript') and self.skip: self.skip -= 1
        if not self.skip and tag in ('p','div','section','h1','h2','h3','h4','li','tr'): self.parts.append('\n')
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def get(item):
    name, url = item
    rec = {'name': name, 'requested_url': url, 'retrieved_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (ScientificCaseReview)'})
        with urllib.request.urlopen(req, timeout=45) as response:
            body = response.read(); rec.update(status=response.status, final_url=response.url)
        (ROOT/'sources'/(name+'.html')).write_bytes(body)
        parser = Text(); parser.feed(body.decode(errors='replace'))
        plain = re.sub(r'\n\s*\n', '\n\n', re.sub(r'[ \t]+', ' ', ''.join(parser.parts)))
        (ROOT/'sources'/(name+'.txt')).write_text(plain)
        rec['bytes'] = len(body)
        relevant = [line.strip()[:900] for line in plain.splitlines() if re.search(r'data availab|code availab|zenodo|figshare|dryad|github|received:|published:|preprint', line, re.I)]
        rec['availability_snippets'] = relevant[:20]
    except Exception as e:
        rec['error'] = str(e)
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    return rec

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(get, URLS.items()))
(ROOT/'FETCH_CANDIDATES.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
