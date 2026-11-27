import sys, pypdf, pathlib
for p in sys.argv[1:]:
    p = pathlib.Path(p)
    try:
        r = pypdf.PdfReader(str(p))
        t = "\n".join((pg.extract_text() or "") for pg in r.pages)
        (p.parent/"text"/(p.stem+".txt")).write_text(t)
        print(p.name, len(r.pages), len(t))
    except Exception as e: print("ERR", p, e)
