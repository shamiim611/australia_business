"""Research integrity and offline browser checks. Requires Playwright + Edge."""
import csv, json, re
from pathlib import Path
from urllib.parse import unquote, urlparse
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/part-1-digital-capability'
d=json.loads((OUT/'results.json').read_text(encoding='utf-8'))
rows=d['observations']
assert len({(o['series'],o['year'],o['group'],o['category']) for o in rows})==len(rows)
assert len(d['dimensions'])==8
assert not any(o['year'] in ['2005-06','2020-21','2022-23','2023-24'] for o in rows)
assert not any(o['category']=='0-19 persons' for o in rows)
assert all(o['year'] in o['period'].replace('–','-') or o['period'].endswith(str(int(o['year'][:4])+1)) for o in rows)
for o in rows:
 assert (ROOT/o['workbook']).is_file()
 assert re.fullmatch(r'[A-Z]+[0-9]+',o['cell'])
 if o['value'] is not None:assert 0<=o['value']<=100
 if o['decision']=='A':assert o['year'] in ['2021-22','2024-25'] and o['series'] in ['social','received']
for c in d['changes']:
 assert abs(c['end_value']-c['start_value']-c['change_pp'])<1e-8
 assert abs(c['end_size_gap']-c['start_size_gap']-c['size_gap_change_pp'])<1e-8
assert {c['series']:c['change_pp'] for c in d['changes']}=={'social':4.2,'received':1.8}
for a in d['innovation']:
 if a['gap'] is not None:assert abs(a['active']-a['nonactive']-a['gap'])<1e-8
for p in d['persistence']:
 assert p['waves']==2 and p['below']==sum(p[k]<0 for k in ['gap_2021_22','gap_2024_25'])
with (OUT/'comparability_decisions.csv').open(encoding='utf-8-sig',newline='') as f:
 audit=list(csv.DictReader(f))
 assert len(audit)==129 and all(json.loads(r['source_headers']) for r in audit)
assert all('href="research.html"' in p.read_text(encoding='utf-8') for p in [ROOT/'index.html',*ROOT.glob('20??-??.html')])
errors=[];external=[]
with sync_playwright() as p:
 browser=p.chromium.launch(channel='msedge',headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1000})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:external.append(r.url) if r.url.startswith('http') else None)
 page.goto((ROOT/'research.html').as_uri());page.wait_for_selector('#headlineCards .kpi')
 assert page.locator('#headlineCards .kpi').count()==4
 for link in page.locator('a[href]').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
  if not link.startswith(('http','#')):assert (ROOT/unquote(link)).exists(),link
 for k in ['internet','web','social','placed','received']:
  page.select_option('#historyMetric',k)
  expected=2 if k in ['social','received'] else 0
  assert page.locator('#historyChart .approved-line').count()==(1 if expected else 0)
  assert page.locator('#historyChart .approved').count()==expected
  assert page.locator('#historyValues tbody tr').count()==len([o for o in rows if o['series']==k and o['group']=='Overall'])
 for dim in d['dimensions']:
  page.select_option('#dimension',dim)
  years=page.locator('#dimensionYear option').evaluate_all('(xs)=>xs.map(x=>x.value)')
  for year in years:
   page.select_option('#dimensionYear',year)
   count=len([o for o in rows if o['dimension']==dim and o['year']==year and o['group']=='Overall'])
   assert page.locator('#dimensionChart .bar-row').count()==count
 for k in ['social','received']:
  page.select_option('#sizeMetric',k);page.select_option('#industryMetric',k)
  assert page.locator('#sizeChart .bar-row').count()==8
  assert page.locator('#industryTable tbody tr').count()==len([a for a in d['persistence'] if a['series']==k])
 for k in ['internet','web','social','placed','received']:
  page.select_option('#innovationMetric',k)
  for group in ['Employment size','Industry']:
   page.select_option('#innovationGroup',group)
   assert page.locator('#innovationTable tbody tr').count()==len([a for a in d['innovation'] if a['series']==k and a['group']==group])
 page.select_option('#historyMetric','received');page.select_option('#dimension','Advanced technologies');page.select_option('#innovationGroup','Employment size')
 (ROOT/'artifacts').mkdir(exist_ok=True)
 page.screenshot(path=str(ROOT/'artifacts/research-desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844})
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Research page overflows mobile viewport'
 page.screenshot(path=str(ROOT/'artifacts/research-mobile.png'),full_page=True)
 # The added navigation must work on the existing annual dashboard too.
 page.goto((ROOT/'2024-25.html').as_uri());page.wait_for_selector('#kpis .kpi')
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Annual page navigation overflows mobile viewport'
 page.locator('.research-link').click();page.wait_for_selector('#headlineCards .kpi')
 assert not errors,errors
 assert not external,external
 browser.close()
print(f'PASS: {len(rows)} observations; comparison arithmetic, source links, all research controls, offline navigation and mobile layout. Screenshots in artifacts/.')
