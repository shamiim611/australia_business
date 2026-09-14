"""Integrity, edge-case rendering, offline navigation and responsive UI checks."""
import json
from pathlib import Path
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'research/part-2-ai-adoption/results.json').read_text(encoding='utf-8'))
obs=d['observations'];ai=[o for o in obs if o['year']=='2024-25' and o['variable']=='ai']
assert len(ai)==35 and len(d['audit'])==7
assert len({(o['year'],o['variable'],o['group'],o['category']) for o in obs})==len(obs)
assert [g['gap_pp'] for g in d['gaps']]==[24.0,22.4]
assert [r['range_pp'] for r in d['dispersion']]==[37.1,37.1]
assert [o['category'] for o in ai if o['status']=='caution']==['Northern Territory']
for o in obs:
 assert (ROOT/o['workbook']).exists()
 assert o['temporal_gate'] in ['C','D']
 assert o['value'] is None or 0<=o['value']<=100
for g in d['gaps']:assert abs(g['large_percent']-g['comparison_percent']-g['gap_pp'])<1e-8
for b in d['industry_benchmarks']:
 if b['gap_pp'] is not None:assert abs(b['ai_percent']-b['national_percent']-b['gap_pp'])<1e-8
errors=[];network=[]
with sync_playwright() as p:
 browser=p.chromium.launch(channel='msedge',headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1000})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:network.append(r.url) if r.url.startswith('http') else None)
 page.goto((ROOT/'research-ai.html').as_uri());page.wait_for_selector('#aiCards .kpi')
 assert page.locator('#sizeBars .bar-row').count()==4
 assert page.locator('#industryBars .bar-row').count()==17
 assert page.locator('#historyCards article').count()==3
 assert page.locator('#historyCards svg, #historyCards canvas').count()==0
 for href in page.locator('a[href]').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
  if not href.startswith(('http','#')):assert (ROOT/unquote(href)).exists(),href
 for order in ['rank','source']:
  page.select_option('#industryOrder',order)
  for flag in ['usable','strict']:
   page.select_option('#industryFlags',flag);assert page.locator('#industryBars .bar-row').count()==17
 for group,count in [('State/Territory',8),('Location',5)]:
  page.select_option('#geoGroup',group);assert page.locator('#geoBars .bar-row').count()==count
 for group in ['Overall','Employment size','Industry']:
  page.select_option('#contextGroup',group)
  for cat in page.locator('#contextCategory option').evaluate_all('(xs)=>xs.map(x=>x.value)'):
   page.select_option('#contextCategory',cat);assert page.locator('#contextBars .bar-row').count()==5
 # Inject adverse statuses to verify exclusion paths, not just the published happy path.
 page.evaluate("""() => {
 const rows=window.AI_RESEARCH.observations.filter(o=>o.year==='2024-25'&&o.variable==='ai'&&o.group==='Industry');
 rows[0].status='unreliable';rows[1].status='suppressed';rows[2].status='missing';rows[2].value=null;rows[3].status='caution';
 }""")
 page.select_option('#industryFlags','usable');assert page.locator('#industryBars .bar-row').count()==14
 page.select_option('#industryFlags','strict');assert page.locator('#industryBars .bar-row').count()==13
 page.select_option('#contextGroup','Industry')
 first=page.locator('#contextCategory option').first.get_attribute('value')
 page.locator('#contextCategory').select_option(index=0)
 assert '!!' in page.locator('#contextBars').inner_text()
 assert page.locator('#contextBars .bar-row').first.locator('.fill').evaluate('(e)=>e.style.width')=='0%'
 page.reload();page.wait_for_selector('#aiCards .kpi')
 (ROOT/'artifacts').mkdir(exist_ok=True)
 page.screenshot(path=str(ROOT/'artifacts/research-ai-desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844})
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 page.select_option('#geoGroup','Location');page.select_option('#contextGroup','Industry')
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 page.screenshot(path=str(ROOT/'artifacts/research-ai-mobile.png'),full_page=True)
 page.locator('.series-nav a[href="research.html"]').click();page.wait_for_selector('#headlineCards .kpi')
 page.locator('nav[aria-label="Research series"] a[href="research-ai.html"]').click();page.wait_for_selector('#aiCards .kpi')
 assert not errors,errors
 assert not network,network
 browser.close()
print(f'PASS: {len(obs)} observations, source links, gap/range arithmetic, status exclusions, all controls, series navigation and mobile layout.')
