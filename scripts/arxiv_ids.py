import arxiv, sys
c = arxiv.Client(delay_seconds=3)
for r in c.results(arxiv.Search(id_list=sys.argv[1:])):
    print(r.get_short_id(), r.published.year, r.title, '|', ', '.join(a.name for a in r.authors[:5]))
    print('  ', r.summary.replace('\n',' ')[:900]); print()
