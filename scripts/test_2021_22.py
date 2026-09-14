"""Offline browser and navigation tests for both annual pages; requires Playwright and Edge."""
from pathlib import Path
import csv,io
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1050},accept_downloads=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'index.html').as_uri());page.wait_for_selector('.bar-row')
    page.select_option('#yearNav','2021-22.html');page.wait_for_url('**/2021-22.html');page.wait_for_selector('.bar-row')
    assert '?' not in page.locator('body').inner_text()
    assert page.locator('#topics button').count()==8
    assert page.locator('#heatmap tbody tr').count()==17
    assert page.locator('#overviewGroup option').count()==2
    expected=page.evaluate("['5-1','6-1','6-2','7-6'].map((id,i)=>{const t=window.BUSINESS_DATA.tables.find(t=>t.id===id);return t.rows.find(r=>r.group==='Overall').cells[[0,0,4,0][i]].value.toFixed(1)+'%';})")
    assert page.locator('.kpi strong').all_text_contents()==expected
    page.select_option('#overviewGroup','Employment size');assert page.locator('#heatmap tbody tr').count()==4
    page.select_option('#overviewGroup','Industry')
    tables=page.evaluate('window.BUSINESS_DATA.tables.map(t=>({id:t.id,topic:t.topic}))')
    for topic in [5,6,7,8,4,1,2,3]:
        page.locator(f'[data-topic="{topic}"]').click()
        for t in [t for t in tables if t['topic']==topic]:
            page.select_option('#table',t['id'])
            pops=page.locator('#population option').evaluate_all('(xs)=>xs.map(x=>x.value)')
            for pop in pops:
                page.select_option('#mode','groups')
                page.select_option('#population',pop)
                for mode in ['groups','measures','heat','populations']:
                    page.select_option('#mode',mode)
                    assert page.locator('#values tbody tr').count()>0,(t,pop,mode)
                    assert page.locator('#chart').inner_text().strip()
            page.select_option('#mode','groups')
            for order in ['desc','asc','source']:page.select_option('#sort',order)
    page.locator('[data-topic="7"]').click();page.select_option('#table','7-6');page.select_option('#metric','2')
    assert 'used paid cloud' in page.locator('#denominator').inner_text()
    with page.expect_download() as dl:page.locator('#download').click()
    rows=list(csv.DictReader(io.StringIO(Path(dl.value.path()).read_text(encoding='utf-8-sig'))))
    assert rows and all(r['Period']=='2021\u201322' for r in rows)
    page.locator('[data-topic="5"]').click()
    page.select_option('#group','State/Territory')
    assert page.locator('.bar-row').count()==8
    page.select_option('#group','Location')
    assert page.locator('.bar-row').count()==5
    page.select_option('#group','Industry')
    (ROOT/'artifacts').mkdir(exist_ok=True)
    page.screenshot(path=str(ROOT/'artifacts/dashboard-2021-22-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(ROOT/'artifacts/dashboard-2021-22-mobile.png'),full_page=True)
    page.select_option('#yearNav','index.html');page.wait_for_url('**/index.html');page.wait_for_selector('.bar-row')
    assert page.locator('#topics button').count()==6
    assert '716k' in page.locator('#kpis').inner_text()
    assert not errors,errors
    browser.close()
    print('PASS: all 40 tables, populations and four modes; denominators, CSV, year navigation, overview, mobile width and no JS errors')
