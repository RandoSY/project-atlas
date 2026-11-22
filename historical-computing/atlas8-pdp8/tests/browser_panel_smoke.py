"""Browser-level ATLAS-8 historical front-panel smoke test.

Requires Playwright/Chromium, no network, Pico or web server.
Run: python tests/browser_panel_smoke.py
Screenshots written to assets/ATLAS8_panel_smoke_*.png and excluded by .gitignore.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from dashboard_bridge import Bridge
root=ROOT
html=(root/'dashboard/index.html').read_text()
css=(root/'dashboard/style.css').read_text()
js=(root/'dashboard/app.js').read_text().replace("document.addEventListener('DOMContentLoaded',boot);",'boot();')
html=html.replace('<link rel="stylesheet" href="/style.css">',f'<style>{css}</style>').replace('<script src="/app.js" defer></script>','')
html=html.replace('</head>', '''<script>window.fetch=async(url,opt)=>{
 if(url==='/api/info')return {ok:true,status:200,json:async()=>({mode:'sim',protocol:'ATLAS-PDP8/1',app_id:'ATLAS8-PDP8'})};
 const r=await window.pyBridge(JSON.parse(opt.body));
 return {ok:true,status:200,json:async()=>r};
};</script></head>''').replace('</body>',f'<script>{js}</script></body>')
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,**({'executable_path':'/usr/bin/chromium'} if Path('/usr/bin/chromium').exists() else {}))
 for w,h in [(1440,900),(1366,768),(1280,720)]:
  page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
  bridge=Bridge()
  page.expose_function('pyBridge',lambda data:bridge.handle(data))
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content(html,wait_until='load');page.wait_for_timeout(100)
  page.locator('[data-tab="panel"]').click();page.wait_for_timeout(100)
  report=page.evaluate('''()=>{const el=document.querySelector('.historic-console'),p=document.querySelector('#panelTab');return {pageScroll:document.documentElement.scrollHeight>innerHeight,consoleScroll:el.scrollHeight>el.clientHeight,upperScroll:el.querySelector('.historic-upper').scrollHeight>el.querySelector('.historic-upper').clientHeight,lowerScroll:el.querySelector('.historic-lower').scrollHeight>el.querySelector('.historic-lower').clientHeight,bodyScroll:p.scrollHeight>p.clientHeight,controls:el.querySelectorAll('button').length,disabledFieldSwitches:el.querySelectorAll('.field-switch-row button:disabled').length}}''')
  out=str(ROOT / 'assets' / f'ATLAS8_panel_smoke_{w}x{h}.png');page.screenshot(path=out)
  print(w,h,report,'errors',errors,'screenshot',out,flush=True)
  assert not errors
  assert not report['pageScroll']
  if w==1366:
   # follow lesson by setting prescribed switch words using assisted setup
   page.locator('#btnPanelPreset').click();page.wait_for_timeout(70)
   page.locator('#btnLoadAddress').click();page.wait_for_timeout(70)
   for _ in range(5):
    page.locator('#btnPanelPreset').click();page.wait_for_timeout(70)
    page.locator('#btnDeposit').click();page.wait_for_timeout(70)
   page.locator('#btnPanelPreset').click();page.wait_for_timeout(70)
   page.locator('#btnLoadAddress').click();page.wait_for_timeout(70)
   print('lesson:',page.locator('#lessonProgress').inner_text(),'memory:',[oct(bridge.cpu.peek(i)) for i in range(5)])
   assert [bridge.cpu.peek(i) for i in range(5)]==[0o7301,0o7001,0o7430,0o7402,0o5001]
   page.locator('#btnSingleInstruction').click()
   page.locator('#btnRun').click();page.wait_for_timeout(100)
   assert bridge.cpu.ac==1
   page.locator('#btnContinue').click();page.wait_for_timeout(100)
   assert bridge.cpu.ac==2
   page.screenshot(path=str(ROOT / 'assets' / 'ATLAS8_panel_programming_smoke.png'))
  page.close()
 browser.close()
