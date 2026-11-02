from pathlib import Path
import urllib.parse
source=Path(__file__).with_name('fetch_sources.py').read_text().split('with concurrent.futures.ThreadPoolExecutor')[0]
exec(compile(source,'fetch_sources.py','exec'))
urls={
'boxes_pmlr':'https://proceedings.mlr.press/v235/li24v.html',
'boxes_full':'https://arxiv.org/html/2402.17879',
'popper_pmlr':'https://proceedings.mlr.press/v267/huang25n.html',
'countermath_pmlr':'https://proceedings.mlr.press/v267/li25ax.html',
'llmsr_abs':'https://arxiv.org/abs/2404.18400',
'llmsr_full':'https://arxiv.org/html/2404.18400',
'llmsr_openreview':'https://api2.openreview.net/notes/search?term=LLM-SR&limit=5',
'scimon_acl':'https://aclanthology.org/2024.acl-long.18/',
'moose_openreview':'https://api2.openreview.net/notes/search?term=MOOSE-Chem&limit=5',
'researchagent_acl':'https://aclanthology.org/2025.naacl-long.342/',
'latest_bayesian_v1':'https://arxiv.org/html/2610.25747v1',
'latest_evobelief_v1':'https://arxiv.org/html/2610.12789v1',
'co_scientist_crossref':'https://api.crossref.org/works/10.1038/s41586-026-10644-y',
'co_scientist_nature_retry':'https://www.nature.com/articles/s41586-026-10644-y',
'sciencegym_crossref':'https://api.crossref.org/works/10.1007/s10994-025-06914-x',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(get,urls.items()))
(root/'FETCH_LOG3.json').write_text(json.dumps(results,indent=2))
