"""Save public method literature and exact retrieval records. No model calls."""
import concurrent.futures
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOIS = {
    "platt": "10.1126/science.146.3642.347",
    "gentner": "10.1207/s15516709cog0702_3",
    "buckingham": "10.1103/PhysRev.4.345",
    "sindy": "10.1073/pnas.1517384113",
    "feynman": "10.1126/sciadv.aay2631",
    "identifiability": "10.1093/bioinformatics/btp358",
    "design": "10.1214/ss/1177009939",
    "causal": "10.1214/09-SS057",
    "pdefind": "10.1126/sciadv.1602614",
    "box": "10.1080/01621459.1976.10480949",
    "reduction": "10.1137/130932715",
}
HTML = {
    "sindy_full": "https://arxiv.org/html/1509.03580v1",
    "feynman_full": "https://arxiv.org/html/1905.11481v2",
    "pdefind_full": "https://arxiv.org/html/1609.06401v1",
    "moose_full": "https://arxiv.org/html/2410.07076v1",
    "identifiability_pubmed": "https://pubmed.ncbi.nlm.nih.gov/19505944/",
}
QUERIES = [
    "Bayesian experimental design a review Chaloner Verdinelli",
    "Structure mapping a theoretical framework for analogy Gentner",
    "Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood",
    "AI Feynman a physics inspired method for symbolic regression",
    "Discovering governing equations from data by sparse identification of nonlinear dynamical systems",
    "Data driven discovery of partial differential equations",
]

class Plain(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"): self.skip += 1
        if not self.skip and tag in ("p", "div", "section", "h1", "h2", "h3", "li", "br"):
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def fetch(job):
    name, url, kind = job
    rec = dict(name=name, url=url, kind=kind, retrieved_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ScientificMethodsReview/1.0"})
        with urllib.request.urlopen(req, timeout=35) as res:
            body = res.read(); rec.update(status=res.status, final_url=res.url)
        suffix = ".json" if kind != "html" else ".html"
        path = ROOT / "sources" / (name + suffix)
        if path.exists(): raise RuntimeError("Refusing to overwrite saved source")
        path.write_bytes(body)
        rec.update(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
        if kind == "crossref":
            m = json.loads(body)["message"]
            rec["metadata"] = {k: m.get(k) for k in ("title", "author", "container-title", "published", "published-online", "abstract", "DOI")}
        elif kind == "html":
            parser = Plain(); parser.feed(body.decode(errors="replace"))
            text = re.sub(r"\n\s*\n", "\n\n", re.sub(r"[ \t]+", " ", "".join(parser.parts)))
            (ROOT / "sources" / (name + ".txt")).write_text(text)
    except Exception as exc:
        rec["error"] = str(exc)
    print(json.dumps({k: rec.get(k) for k in ("name", "status", "bytes", "error")}), flush=True)
    return rec

def main():
    jobs = [(name, "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""), "crossref") for name, doi in DOIS.items()]
    jobs += [(name, url, "html") for name, url in HTML.items()]
    for i, q in enumerate(QUERIES, 1):
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({"search": q, "per-page": 3})
        jobs.append(("search_%02d" % i, url, "openalex"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(fetch, jobs))
    path = ROOT / "RETRIEVAL_LOG.json"
    with path.open("x") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__": main()
