#!/usr/bin/env python3
"""Deploy C2G portal 1.1 from a local Git checkout, preserving other Atlas pages."""
import argparse, hashlib, os, re, shutil, tempfile, urllib.request
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--site',default=os.environ.get('ATLAS_SITE','/var/www/html/atlas'))
parser.add_argument('--url',default=os.environ.get('ATLAS_URL','https://project-atlas-lab.duckdns.org/atlas'))
parser.add_argument('--local-only',action='store_true',help='Skip live HTTP checks (local test only)')
args=parser.parse_args()
src=Path(__file__).resolve().parent/'atlas'
site=Path(args.site).resolve()
if not (site/'index.html').is_file() or not (site/'exhibits/index.html').is_file():
    raise SystemExit('Atlas site not found: '+str(site))
portal='circuits-to-genomes/'
cat='catalase-fem/'
targets=[portal+'media/research.css',portal+'media/peroxide-continuity.svg',
         cat+'media/open-lab-cover-v1.1.svg',cat+'media/research-cover-v1.1.svg',
         cat+'media/open-lab-apparatus.svg',cat+'media/open-lab-balloon.svg',
         portal+'index.html',cat+'index.html',cat+'open-lab/index.html','exhibits/index.html']
payload={f:(src/f).read_bytes() for f in targets[:-1]}
source=(src/'exhibits/index.html').read_text(encoding='utf-8')
live=(site/'exhibits/index.html').read_text(encoding='utf-8')

# Only replace the specific marked Open Lab and CAT-FEM entries, plus the C2G card.
# Never overwrite the entire live gallery from the checkout.
def marked(doc,start,end):
    matches=list(re.finditer(re.escape(start)+r'.*?'+re.escape(end),doc,re.S))
    if len(matches)>1: raise ValueError('Duplicate gallery markers: '+start)
    return matches[0] if matches else None
def merge(doc,start,end,anchor):
    new=marked(source,start,end)
    if new is None: raise ValueError('Source marker missing: '+start)
    old=marked(doc,start,end)
    if old: return doc[:old.start()]+new.group()+doc[old.end():]
    if doc.count(anchor)!=1: raise ValueError('Unexpected gallery structure')
    return doc.replace(anchor,anchor+new.group(),1)
# Refuse duplicate unmarked Open Lab cards; preserve any manually added unrelated card.
start='<!-- C2G-OPEN-LAB start -->'; end='<!-- C2G-OPEN-LAB end -->'
if not marked(live,start,end) and re.search(r'<article\b[^>]*>[^<]*<a[^>]*href=["\']\.\./catalase-fem/open-lab/',live,re.S):
    raise SystemExit('An unmarked Open Lab card exists; review before replacing.')
live=merge(live,start,end,'<div class="atlas-exhibits">')
live=merge(live,'<!-- CAT-FEM exhibit start -->','<!-- CAT-FEM exhibit end -->','<!-- C2G-OPEN-LAB end -->')
def c2g_card(doc):
    matches=[m for m in re.finditer(r'<article\b[^>]*>.*?</article>',doc,re.S)
             if re.search(r'<h2>\s*<a\s+href=["\']\.\./circuits-to-genomes/["\']',m.group())]
    if len(matches)!=1: raise ValueError('Expected exactly one C2G gallery card')
    return matches[0]
old=c2g_card(live); new=c2g_card(source)
live=live[:old.start()]+new.group()+live[old.end():]
payload['exhibits/index.html']=live.encode('utf-8')

# Earlier published photographs and figure crops are server assets; preserve them.
required=[portal+'media/'+n for n in ['pdp8.jpg','reciprocal.svg','dependencies.svg','continuity.png','networks.png','equivalence.png','precision.png','framework.png']]
required += ['catalase-fem/media/cover.svg']
required += ['catalase-fem/downloads/v1.1/'+n for n in ['Catalase_Open_Lab_v1.1.zip','01_Teacher_Guide.pdf','02_Student_Guide.pdf','03_Theory_and_Research.pdf']]
missing=[f for f in required if not (site/f).is_file() or not (site/f).stat().st_size]
if missing: raise SystemExit('Missing existing assets (no changes made): '+', '.join(missing))
manifest=src/'catalase-fem/downloads/v1.1/SHA256SUMS.txt'
for line in manifest.read_text(encoding='utf-8').splitlines():
    digest,name=line.split('  ',1)
    rel='catalase-fem/downloads/v1.1/'+name
    f=site/rel
    if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:
        raise SystemExit('Lab release missing or checksum mismatch (no changes made): '+rel)
    if rel not in required: required.append(rel)
print('Verified existing Open Lab archive and all seven members.')
a=cat+'media/open-lab-cover-v1.1.svg'
b=cat+'media/research-cover-v1.1.svg'
if payload[a]==payload[b]:
    raise SystemExit('Duplicate cover content (no changes made)')
for rel,expected_cover in [(cat+'index.html',b),(cat+'open-lab/index.html',a)]:
    if Path(expected_cover).name.encode() not in payload[rel]:
        raise SystemExit('Missing intended cover: '+rel)
if not all(Path(x).name.encode() in payload['exhibits/index.html'] for x in (a,b)):
    raise SystemExit('Gallery does not reference both covers')

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.panels=[];self.tabs=[];self.duplicates=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids:self.duplicates.append(a['id'])
            self.ids.add(a['id'])
        if 'data-panel' in a:self.panels.append(a.get('id'))
        if 'data-tab' in a:self.tabs.append(a['data-tab'])
p=Inspect();p.feed(payload[portal+'index.html'].decode())
expected=['overview','architecture','peroxide','investigator','open-lab','archive','review']
if p.duplicates or p.panels!=expected or p.tabs!=expected:
    raise SystemExit('Portal structure check failed: '+str((p.duplicates,p.panels,p.tabs)))

backup=Path(tempfile.mkdtemp(prefix='atlas-c2g-portal-backup-',dir=str(Path.home())))
for f in targets:
    if (site/f).exists():
        (backup/f).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(site/f,backup/f)

def atomic_write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.atlas-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as h:h.write(data)
        os.chmod(tmp,0o644);os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

changed=[]
try:
    for f in targets:
        atomic_write(site/f,payload[f]);changed.append(f)
        if (site/f).read_bytes()!=payload[f]:raise IOError('Local verification failed: '+f)
    if not args.local_only:
        stamp=str(int(datetime.now(timezone.utc).timestamp()))
        for f in targets:
            u=args.url.rstrip('/')+'/'+f+'?portal='+stamp
            with urllib.request.urlopen(u,timeout=25) as response:
                if response.status!=200 or response.read()!=payload[f]:
                    raise IOError('Live byte verification failed: '+u)
            print('HTTP VERIFIED:',f)
        # Verify existing downloadable files and Open Lab endpoint without altering them.
        for f in required:
            if not f.startswith('catalase-fem/'):continue
            u=args.url.rstrip('/')+'/'+f
            with urllib.request.urlopen(u,timeout=25) as response:
                if response.status!=200 or response.read()!=(site/f).read_bytes():
                    raise IOError('Live existing resource differs: '+u)
            print('HTTP VERIFIED:',f)
except BaseException as e:
    for f in reversed(changed):
        if (backup/f).is_file():atomic_write(site/f,(backup/f).read_bytes())
        else:(site/f).unlink(missing_ok=True)
    raise SystemExit('Deployment rolled back: '+str(e)+' | Backup: '+str(backup))
print('C2G PORTAL v1.1 DEPLOYED' if not args.local_only else 'C2G PORTAL v1.1 LOCAL TEST INSTALLED')
print('Backup:',backup)
print(args.url.rstrip('/')+'/circuits-to-genomes/')
