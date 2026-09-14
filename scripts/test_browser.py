"""Browser smoke test. Requires optional pip install playwright and Microsoft Edge."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1100},accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'index.html').as_uri())
    page.wait_for_selector('.bar-row')
    assert page.locator('.kpi').count()==4
    assert '?' not in page.locator('body').inner_text(), 'Unexpected encoding replacement'
    assert page.evaluate("window.BUSINESS_DATA.period")== '2005\u201306'
    assert page.locator('#heatmap tbody tr').count()==14
    for group,n in [('Employment size',4),('State/territory',8),('Industry',14)]:
        page.select_option('#overviewGroup',group)
        assert page.locator('#heatmap tbody tr').count()==n
    tables=page.evaluate('window.BUSINESS_DATA.tables.map(t=>({id:t.id,topic:t.topic}))')
    checked=0
    for topic in [4,6,2,3,1,5]:
        page.locator(f'[data-topic="{topic}"]').click()
        for t in [x for x in tables if x['topic']==topic]:
            page.select_option('#table',t['id'])
            for mode in ['groups','measures','heat']:
                page.select_option('#mode',mode)
                assert page.locator('#chart').inner_text().strip(),(t,mode)
                assert page.locator('#values tbody tr').count()>0
            page.select_option('#mode','groups')
            for order in ['desc','asc','source']: page.select_option('#sort',order)
            checked+=1
    page.locator('[data-topic="6"]').click()
    with page.expect_download() as dl: page.locator('#download').click()
    downloaded=Path(dl.value.path()).read_text(encoding='utf-8-sig')
    assert 'Status' in downloaded and '2005' in downloaded and 'Cell' in downloaded
    page.locator('[data-topic="4"]').click()
    (ROOT/'artifacts').mkdir(exist_ok=True)
    page.screenshot(path=str(ROOT/'artifacts/dashboard-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile page overflow'
    page.screenshot(path=str(ROOT/'artifacts/dashboard-mobile.png'),full_page=True)
    assert not errors,errors
    browser.close()
    print(f'PASS: {checked} tables in all 3 chart modes, overview filters, sorting, CSV download, offline loading and mobile width; no JavaScript errors')
