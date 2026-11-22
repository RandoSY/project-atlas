"""Offline browser smoke test. Uses Chromium + in-process PDP8 Bridge.
Run from project directory: python tests/browser_smoke.py
No HTTP network access or hardware is required.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard_bridge import Bridge

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'dashboard'/'index.html').read_text()
css=(ROOT/'dashboard'/'style.css').read_text()
js=(ROOT/'dashboard'/'app.js').read_text().replace("document.addEventListener('DOMContentLoaded',boot);", 'boot();')
html=html.replace('<link rel="stylesheet" href="/style.css">',f'<style>{css}</style>')
html=html.replace('<script src="/app.js" defer></script>', '')
network_stub='''<script>
window.fetch=async(url, options)=>{
 if(url==='/api/info')return {ok:true,status:200,json:async()=>({mode:'sim',protocol:'ATLAS-PDP8/1'})};
 let result=await window.pyBridge(JSON.parse(options.body));
 return {ok:true,status:200,json:async()=>result};
};
</script>'''
html=html.replace('</head>',network_stub+'</head>')
html=html.replace('</body>',f'<script>{js}</script></body>')
bridge=Bridge()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.expose_function('pyBridge',lambda data:bridge.handle(data))
    page.set_content(html,wait_until='load')
    page.wait_for_timeout(300)
    print('TITLE:',page.title())
    print('PAGE OVERFLOW:',page.evaluate('document.documentElement.scrollHeight > window.innerHeight'))
    assert not page.evaluate('document.documentElement.scrollHeight > window.innerHeight')
    print('BADGE:',page.locator('#connectionBadge').inner_text())
    page.screenshot(path='/mnt/data/ATLAS8_dashboard_desktop.png',full_page=True)
    page.locator('#btnCalcLoad').click()
    page.locator('#btnCalcFinish').click()
    page.wait_for_timeout(400)
    print('CALC RESULT:',page.locator('#calcResult').inner_text())
    print('CALC DETAIL:',page.locator('#calcResultDetail').inner_text())
    assert page.locator('#calcResult').inner_text().strip()=='13'
    page.locator('#calcOperation').select_option('multiply')
    page.locator('#btnCalcLoad').click()
    page.locator('#btnCalcFinish').click()
    page.wait_for_timeout(400)
    print('MULT RESULT:',page.locator('#calcResult').inner_text())
    assert page.locator('#calcResult').inner_text().strip()=='42'
    page.locator('[data-tab="programs"]').click()
    page.locator('[data-demo="hello"]').click()
    page.locator('[data-tab="panel"]').click()
    page.locator('[data-panel-section="control"]').click()
    page.locator('#btnRun').click()
    page.wait_for_timeout(400)
    page.locator('[data-tab="terminal"]').click()
    print('TTY:',page.locator('#ttyScreen').inner_text()[-120:])
    assert 'HELLO PDP-8' in page.locator('#ttyScreen').inner_text()
    page.screenshot(path='/mnt/data/ATLAS8_dashboard_terminal.png',full_page=True)
    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    mobile.expose_function('pyBridge',lambda data:Bridge().handle(data))
    mobile.set_content(html,wait_until='load')
    mobile.wait_for_timeout(200)
    mobile.screenshot(path='/mnt/data/ATLAS8_dashboard_mobile.png',full_page=True)
    print('JS ERRORS:',errors)
    assert not errors
    browser.close()
