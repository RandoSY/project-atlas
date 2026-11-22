"""Browser-level virtual-tape test; requires Playwright and Chromium.

Run separately: python tests/browser_tape_smoke.py. Tests REAL CPU bridge and
DOM interactions, no Pico. Screenshots are release preview artifacts.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard_bridge import Bridge

html = (ROOT/'dashboard/index.html').read_text()
css = (ROOT/'dashboard/style.css').read_text()
js = (ROOT/'dashboard/app.js').read_text().replace("document.addEventListener('DOMContentLoaded',boot);",'boot();')
html = html.replace('<link rel="stylesheet" href="/style.css">', '<style>'+css+'</style>')
html = html.replace('<script src="/app.js" defer></script>', '')
html = html.replace('</head>', '''<script>window.fetch=async(url,opt)=>{
 if(url==='/api/info')return {ok:true,status:200,json:async()=>({mode:'sim',protocol:'ATLAS-PDP8/1',app_id:'ATLAS8-PDP8'})};
 const r=await window.pyBridge(JSON.parse(opt.body));
 return {ok:true,status:200,json:async()=>r};
};</script></head>''').replace('</body>', '<script>'+js+'</script></body>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium')
    for w,h in ((1440,900),(1280,720)):
        page=browser.new_page(viewport={'width':w,'height':h})
        cpu=Bridge()
        page.expose_function('pyBridge', lambda data:cpu.handle(data))
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(html, wait_until='load')
        page.locator('[data-tab="programs"]').click()
        page.locator('[data-program-view="tape"]').click()
        page.wait_for_timeout(90)
        page.locator('#btnRimInstall').click()
        page.locator('#btnTapeDemo').click()
        page.wait_for_timeout(120)
        assert cpu.cpu.reader_status()['size'] == 64
        assert page.locator('#tapeReadout').inner_text().find('10 cps') > -1
        page.locator('#btnTapeStart').click()
        page.wait_for_timeout(420)
        at_10=cpu.cpu.ptr_pos
        assert 1 <= at_10 < 64, ('10 cps progress',at_10)
        page.locator('#btnTapePause').click()
        page.wait_for_timeout(180)
        paused=cpu.cpu.ptr_pos
        page.wait_for_timeout(170)
        assert cpu.cpu.ptr_pos == paused, ('Pause failed', paused, cpu.cpu.ptr_pos)
        page.locator('#btnTapePlay').click()
        page.locator('#tapeSpeed').select_option('high')
        page.wait_for_timeout(260)
        at_300=cpu.cpu.ptr_pos
        assert at_300 > paused, ('300 cps progress', paused, at_300)
        page.locator('#tapeSpeed').select_option('turbo')
        page.wait_for_timeout(450)
        assert cpu.cpu.ptr_pos == 64, ('Turbo did not finish',cpu.cpu.ptr_pos)
        assert [cpu.cpu.peek(0o200+i) for i in range(4)]==[0o7301,0o7001,0o7001,0o7402]
        assert 'TURBO' in page.locator('#tapeReadout').inner_text()
        layout=page.evaluate('''()=>({pageScroll:document.documentElement.scrollHeight>innerHeight, bodyScroll:document.body.scrollHeight>innerHeight, tapeScroll:document.querySelector('.tape-grid').scrollHeight>document.querySelector('.tape-grid').clientHeight})''')
        screenshot=ROOT/'assets'/f'ATLAS8_v060_tape_{w}x{h}.png'
        page.screenshot(path=str(screenshot))
        print(f'{w}x{h}: 10cps={at_10}, pause={paused}, 300cps={at_300}, turbo=64, {layout}, JS errors={errors}; {screenshot}')
        assert not errors
        assert not layout['pageScroll'] and not layout['bodyScroll']
        page.close()
    browser.close()
