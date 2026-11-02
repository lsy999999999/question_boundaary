from pathlib import Path
import urllib.parse
source=Path(__file__).with_name('fetch_sources.py').read_text().split('with concurrent.futures.ThreadPoolExecutor')[0]
exec(compile(source,'fetch_sources.py','exec'))
urls={
'pmlr_icml2024':'https://proceedings.mlr.press/v235/',
'pmlr_icml2025':'https://proceedings.mlr.press/v267/',
'popper_openreview':'https://api2.openreview.net/notes/search?term='+urllib.parse.quote('Automated Hypothesis Validation')+'&limit=10',
'discoverybench_openreview':'https://api2.openreview.net/notes/search?term=DiscoveryBench&limit=5',
'discoveryworld_openreview':'https://api2.openreview.net/notes/search?term=DiscoveryWorld&limit=5',
'critic_openreview':'https://api2.openreview.net/notes/search?term='+urllib.parse.quote('Critic Automation')+'&limit=5',
'latest_bayesian_full':'https://arxiv.org/html/2610.25747',
'latest_model_discovery_full':'https://arxiv.org/html/2608.09696',
'latest_evobelief_full':'https://arxiv.org/html/2610.12789',
'newton_full':'https://arxiv.org/html/2504.01538',
'co_scientist_nature':'https://www.nature.com/articles/s41586-026-10644-y',
'concept_counterexamples_full':'https://arxiv.org/html/2502.10454',
'hypogenic_full':'https://arxiv.org/html/2404.04326',
'sciencegym_springer':'https://link.springer.com/article/10.1007/s10994-025-06914-x',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(get,urls.items()))
(root/'FETCH_LOG2.json').write_text(json.dumps(results,indent=2))
