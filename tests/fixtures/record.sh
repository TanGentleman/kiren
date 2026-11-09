#!/usr/bin/env bash
# Re-record the NCBI and OpenAlex responses the fake servers in tests/conftest.py replay.
# efetch.xml has <PubmedData> (references, history) removed to keep it small.
# Also records the OpenAlex work used by the DOI lookup tests.
set -euo pipefail
cd "$(dirname "$0")"
E=https://eutils.ncbi.nlm.nih.gov/entrez/eutils
ids=38860195,38798998,42344625
curl -sf "$E/esearch.fcgi?db=pubmed&retmode=xml&retmax=100&usehistory=y&term=38860195%5Buid%5D+OR+38798998%5Buid%5D+OR+42344625%5Buid%5D" -o esearch.xml
sleep 1
curl -sf "$E/esearch.fcgi?db=pubmed&retmode=xml&retmax=100&usehistory=n&term=zzxqvnonexistentterm123" -o esearch-empty.xml
sleep 1
curl -sf "$E/efetch.fcgi?db=pubmed&retmode=xml&id=$ids" | python3 -c '
import re, sys
sys.stdout.write(re.sub(r"<PubmedData>.*?</PubmedData>", "", sys.stdin.read(), flags=re.S))
' > efetch.xml
sleep 1
curl -sf "$E/efetch.fcgi?db=pubmed&retmode=xml&id=99999999999" -o efetch-empty.xml
sleep 1
# OpenAlex work for the DOI lookup, trimmed to the fields pubmed_tools/openalex.py reads.
curl -sf "https://api.openalex.org/works/https://doi.org/10.1093/scan/nsq093" | python3 -c '
import json, sys
work = json.load(sys.stdin)
keep = ["id", "doi", "title", "display_name", "publication_year", "publication_date",
        "keywords", "concepts", "cited_by_count", "abstract_inverted_index"]
out = {k: work[k] for k in keep if k in work}
out["authorships"] = [{"author": {"id": a["author"].get("id"),
                                  "display_name": a["author"].get("display_name")}}
                      for a in work["authorships"]]
sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
' > openalex-work.json
