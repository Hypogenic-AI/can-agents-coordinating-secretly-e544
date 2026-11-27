import arxiv, sys, json
client = arxiv.Client(page_size=15, delay_seconds=3, num_retries=3)
out = {}
for q in sys.argv[1:]:
    res = []
    try:
        for r in client.results(arxiv.Search(query=q, max_results=12, sort_by=arxiv.SortCriterion.Relevance)):
            res.append(dict(id=r.get_short_id(), title=r.title, year=r.published.year, authors=[a.name for a in r.authors][:4], abstract=r.summary[:400]))
    except Exception as e:
        res.append(dict(error=str(e)))
    out[q] = res
    for x in res: print(x.get('id'), x.get('year'), '|', x.get('title'))
    print('----')
json.dump(out, open('logs/arxiv_search.json','w'), indent=1)
