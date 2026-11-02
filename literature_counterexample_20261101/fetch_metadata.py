from pathlib import Path
source=Path(__file__).with_name('fetch_sources.py').read_text().split('with concurrent.futures.ThreadPoolExecutor')[0]
exec(compile(source,'fetch_sources.py','exec'))
urls={
'llmsr_official':'https://api2.openreview.net/notes?id=m2nmp8P5in',
'moose_official':'https://api2.openreview.net/notes?id=X9OfMNNepI',
'cegis_crossref':'https://api.crossref.org/works?query.title=Combinatorial%20sketching%20for%20finite%20programs&rows=1',
'moose_abs':'https://arxiv.org/abs/2410.07076',
'mda_official':'https://api2.openreview.net/notes?id=yAUf6aSeyA',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(get,urls.items()))
(root/'FETCH_LOG4.json').write_text(json.dumps(results,indent=2))
