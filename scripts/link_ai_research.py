from pathlib import Path
p=Path('research.html');s=p.read_text(encoding='utf-8-sig');nav='<nav class="chapter-nav" aria-label="Research series"><a href="research.html" aria-current="page">Part 1 · Digital capability</a><a href="research-ai.html">Part 2 · AI adoption</a></nav>'
if 'href="research-ai.html"' not in s:s=s.replace('<main>','<main>'+nav,1)
p.write_text(s,encoding='utf-8')
p=Path('research/part-2-ai-adoption/protocol.md');s=p.read_text(encoding='utf-8');s=s.replace('Status: public-data-only research scope and verified local data inventory. No microdata received. Dashboard implementation and the full comparability review are subsequent outputs, not completed by this document.','Status: implemented as a descriptive public-data study in research-ai.html. Reproduce with scripts/build_ai_research.py. Temporal comparisons and the AI-by-innovation gap remain unapproved where source evidence is insufficient; see comparability_decisions.csv and evidence_decisions.json. No microdata is used.');s=s.replace('No page has been created at this scoping stage.','The page is implemented and linked from Part 1.');s=s.replace('The current scoped work provides the protocol and a source-checked local AI inventory only.','The implementation provides the research page, findings paper, reproducible tables, item decisions and source/browser tests.');s=s.replace('2024?25','2024-25').replace('0?4','0-4').replace('5?19','5-19').replace('20?199','20-199').replace('section ?Use of information and communication technology?','section "Use of information and communication technology"');p.write_text(s,encoding='utf-8')
p=Path('README.md');s=p.read_text(encoding='utf-8');s+='''

## Research series - Part 2: AI adoption

Open [research-ai.html](research-ai.html), also linked from Part 1. The offline story presents 2024-25 AI adoption by size, industry and geography, source-linked digital context, earlier snapshots, and explicit evidence limits. Source numeric checks, comparability decisions, gap calculations and flag sensitivity are reproducible:

```powershell
python scripts/build_ai_research.py
python scripts/test_ai_research.py
```

The builder uses openpyxl and the supplied workbooks; no network or microdata is required. Browser tests use Playwright and Edge. Outputs and the findings paper are in `research/part-2-ai-adoption/`. The AI-by-innovation gap is withheld because the public source's denominator descriptions conflict. No temporal AI change or causal effect is asserted.
''';p.write_text(s,encoding='utf-8')
