#!/usr/bin/env python3
"""Install exact v1.1 archive and a standalone exhibit; no network required."""
import hashlib, os, re, shutil, sys, tempfile, zipfile
from pathlib import Path
from datetime import datetime, timezone
from html import escape

HERE=Path(__file__).resolve().parent
SITE=Path(os.environ.get('ATLAS_SITE','/var/www/html/atlas')).resolve()
ZNAME='Catalase_Open_Lab_v1.1.zip'
EXPECTED='e2e0173c913f814d196a4c622f1ff1c8f0f8d471bb3c295bd0817e76537de84f'
NAMES=['01_Teacher_Guide.pdf','02_Student_Guide.pdf','03_Theory_and_Research.pdf','START_HERE.txt','analyze.py','measurements_template.csv','balloon_template.csv']
sha=lambda b: hashlib.sha256(b).hexdigest()
archive=(HERE/ZNAME).read_bytes()
if sha(archive)!=EXPECTED: sys.exit('Archive checksum mismatch; no changes made.')
if not (SITE/'exhibits/index.html').is_file(): sys.exit(f'Atlas gallery not found at {SITE}. Set ATLAS_SITE to your actual Atlas root.')
files={}
D='catalase-fem/downloads/v1.1/'
files[D+ZNAME]=archive
with zipfile.ZipFile(HERE/ZNAME) as z:
    if z.testzip(): sys.exit('Corrupt lab ZIP')
    for name in NAMES:
        info=z.getinfo('catalase_open_lab/'+name)
        if info.file_size>10_000_000: sys.exit('Unexpected member size')
        files[D+name]=z.read(info)
files[D+'SHA256SUMS.txt']=''.join(f'{sha(files[D+n])}  {n}\n' for n in [ZNAME,*NAMES]).encode()
files['catalase-fem/open-lab/index.html']=(HERE/'index.html').read_bytes()
# Do not overwrite an existing research exhibit; add a clearly marked link.
parent=SITE/'catalase-fem/index.html'
start='<!-- ATLAS-OPEN-LAB-OFFLINE -->'; end='<!-- /ATLAS-OPEN-LAB-OFFLINE -->'
link=start+'<section style="padding:1.25rem;margin:1rem 0;border:1px solid #8fb6a5;border-radius:10px"><h2>Catalase Open Lab v1.1</h2><p>Teacher and student guides, theory, gas collection, balloon calibration and the scientific connection to C2G.</p><p><a href="open-lab/">Open the complete laboratory exhibit and downloads</a></p></section>'+end
if parent.exists():
    page=parent.read_text(encoding='utf-8')
    pattern=re.escape(start)+r'.*?'+re.escape(end)
    matches=re.findall(pattern,page,re.S)
    if len(matches)>1: sys.exit('Duplicate open lab markers; no changes made')
    if matches: page=re.sub(pattern,lambda _:link,page,count=1,flags=re.S)
    else:
        if '</nav>' not in page: sys.exit('Unexpected catalase page structure; no changes made')
        page=page.replace('</nav>','</nav>'+link,1)
else:
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Catalase Open Lab</title><body><main><h1>Catalase: one reaction, many implementations</h1>'+link+'<p><a href="../exhibits/">Atlas exhibits</a></p></main></body></html>'
files['catalase-fem/index.html']=page.encode()
gallery=(SITE/'exhibits/index.html').read_text(encoding='utf-8')
if '../catalase-fem/' not in gallery:
    marker='<div class="atlas-exhibits">'
    if gallery.count(marker)!=1: sys.exit('Unexpected gallery structure; no changes made')
    card='<article class="atlas-exhibit"><div class="atlas-exhibit-body"><p class="atlas-kicker">Kitchen Inquiry Lab · C2G</p><h2><a href="../catalase-fem/open-lab/">Catalase Open Lab</a></h2><p>One reaction, many implementations: teacher/student guides, oxygen measurements, balloon calibration and evolutionary functional continuity.</p></div></article>'
    files['exhibits/index.html']=gallery.replace(marker,marker+card,1).encode()
# Preserve old files and track new paths; verify every installed byte.
backup=Path(tempfile.mkdtemp(prefix='atlas-openlab-backup-',dir=str(Path.home())))
changed=[]
try:
    for rel in files:
        target=SITE/rel
        if target.exists():
            dst=backup/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(target,dst)
    for rel,data in files.items():
        target=SITE/rel; target.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix='.openlab-',dir=str(target.parent))
        try:
            with os.fdopen(fd,'wb') as f: f.write(data)
            os.chmod(tmp,0o644); os.replace(tmp,target); changed.append(rel)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        if sha(target.read_bytes())!=sha(data): raise IOError('Verification failed: '+rel)
        print('VERIFIED:',rel)
except BaseException:
    for rel in reversed(changed):
        target=SITE/rel; src=backup/rel
        if src.exists(): shutil.copy2(src,target)
        else: target.unlink(missing_ok=True)
    print('Rolled back; backup:',backup,file=sys.stderr); raise
print('INSTALLED:',SITE/'catalase-fem/open-lab/index.html')
print('Backup:',backup)
print('Public page: https://project-atlas-lab.duckdns.org/atlas/catalase-fem/open-lab/')
print('Local byte verification passed. Check public HTTP separately.')
