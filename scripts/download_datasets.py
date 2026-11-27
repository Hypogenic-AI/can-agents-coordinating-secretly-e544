from datasets import load_dataset
import json, os
os.makedirs("datasets", exist_ok=True)
specs = [("Salesforce/wikitext","wikitext-2-raw-v1","datasets/wikitext2"),
         ("databricks/databricks-dolly-15k",None,"datasets/dolly15k")]
for name, cfg, path in specs:
    ds = load_dataset(name, cfg) if cfg else load_dataset(name)
    ds.save_to_disk(path)
    print(name, ds)
    split = list(ds.keys())[0]
    os.makedirs(path+"/samples", exist_ok=True)
    rows = [r for r in ds[split].select(range(50)) if any(str(v).strip() for v in r.values())][:5]
    json.dump(rows, open(path+"/samples/samples.json","w"), indent=1)
