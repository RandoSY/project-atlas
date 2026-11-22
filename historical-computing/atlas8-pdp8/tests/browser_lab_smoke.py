"""Headless Chrome acceptance for ATLAS-8 v0.7 lab-IOT screen (SIM only)."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from dashboard_bridge import Bridge
from lab_device import SimTransport
html=(root/'dashboard/index.html').read_text()
css=(root/'dashboard/style.css').read_text()
js=(root/'dashboard/app.js').read_text().replace("document.addEventListener('DOMContentLoaded',boot);", 'boot();')
html=html.replace('<link rel="stylesheet" href="/style.css">','<style>'+css+'</style>').replace('<script src="/app.js" defer></script>','')
html=html.replace('</head>', '''<script>window.fetch=async(url,opt)=>{
 if(url==='/api/info')return {ok:true,status:200,json:async()=>({mode:'sim',protocol:'ATLAS-PDP8/1',app_id:'ATLAS8-PDP8'})};
 const r=await window.pyBridge(JSON.parse(opt.body));
 return {ok:true,status:200,json:async()=>r};
};</script></head>''').replace('</body>','<script>'+js+'</script></body>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium')
    for w,h in ((1440,900),(1280,720)):
        page=browser.new_page(viewport={'width':w,'height':h})
        bridge=Bridge(lab_transport=SimTransport())
        page.expose_function('pyBridge',lambda msg:bridge.handle(msg))
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content(html,wait_until='load')
        page.locator('[data-tab="programs"]').click()
        page.locator('[data-program-view="lab"]').click()
        page.locator('#btnLabDemo').click()
        page.wait_for_timeout(100)
        assert bridge.cpu.peek(0o200)==0o7200
        page.locator('#btnLabRun').click()
        page.wait_for_timeout(400)
        assert bridge.cpu.halted and bridge.cpu.peek(0o210)==512, (bridge.cpu.state(),bridge.cpu.peek(0o210))
        assert 'SIMULATION' in page.locator('#labReadout').inner_text()
        page.locator('#btnLabTimerDemo').click()
        page.wait_for_timeout(100)
        page.locator('#btnLabRun').click()
        page.wait_for_timeout(350)
        assert bridge.cpu.halted and bridge.cpu.peek(0o210)==1000
        dims=page.evaluate('''()=>({doc:document.documentElement.scrollHeight,view:window.innerHeight,body:document.body.scrollHeight,errors:document.querySelectorAll('script:not([src])').length})''')
        assert not errors, errors
        assert dims['doc']<=h and dims['body']<=h, dims
        page.screenshot(path=str(root/'assets'/f'ATLAS8_v070_lab_{w}x{h}.png'))
        print(w,h,'ADC=512 TIMER=1000',dims,'JS errors=',errors,flush=True)
        page.close()
    browser.close()
