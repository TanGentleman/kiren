#!/usr/bin/env bash
# Re-record the E-utilities responses the fake server in tests/conftest.py replays.
# efetch.xml has <PubmedData> (references, history) removed to keep it small.
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
