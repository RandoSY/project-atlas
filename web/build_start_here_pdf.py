"""Render the printable Atlas guide from the same catalog used by the web edition.

Requires ReportLab and the Liberation and DejaVu fonts shipped on Debian/Ubuntu.
"""
from pathlib import Path
import json
from urllib.parse import urljoin
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

WEB = Path(__file__).resolve().parent
data = json.loads((WEB / "start-here.json").read_text(encoding="utf-8"))
out = WEB / "atlas/start-here/Project-Atlas-Start-Here.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
fonts = Path("/usr/share/fonts/truetype")
for name, file in {
    "Body": "dejavu/DejaVuSans.ttf", "Strong": "dejavu/DejaVuSans-Bold.ttf",
    "Display": "liberation/LiberationSerif-Bold.ttf"
}.items():
    pdfmetrics.registerFont(TTFont(name, fonts / file))

W, H = letter
C = {
    "ink": "#183334", "paper": "#FAF8EF", "deep": "#102F32", "tea": "#075B51",
    "muted": "#47635D", "aqua": "#AADBC9", "gold": "#EDC479", "border": "#C2D1C5",
    "wash": "#ECF1E7", "cream": "#F2E8D3", "white": "#FFFFFF",
}
pdf = canvas.Canvas(str(out), pagesize=letter, pageCompression=1, invariant=1)
pdf.setTitle("Project Atlas | Start Here")
pdf.setAuthor("Randall Young | Project Atlas")
pdf.setSubject("A getting-started guide, exhibit index, and source route for Project Atlas")

def col(name):
    return HexColor(C.get(name, name))

def t(x, y, text, size=10, face="Body", ink="ink"):
    pdf.setFillColor(col(ink))
    pdf.setFont(face, size)
    pdf.drawString(x, H-y-size*.8, text)

def align_right(x, y, text, size=10, face="Body", ink="ink"):
    return t(x-pdfmetrics.stringWidth(text, face, size), y, text, size, face, ink)

def wrap(x, y, text, width, size=10, leading=14, face="Body", ink="ink", max_lines=None):
    lines = simpleSplit(text, face, size, width)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError(f"Too many lines at {x}, {y}: {text} -> {lines}")
    for i, row in enumerate(lines):
        t(x, y+i*leading, row, size, face, ink)
    return y + len(lines) * leading

def bg(x, y, w, h, fill="wash", stroke=None, radius=10):
    pdf.setFillColor(col(fill))
    if stroke:
        pdf.setStrokeColor(col(stroke))
        pdf.setLineWidth(.7)
    if radius:
        pdf.roundRect(x,H-y-h,w,h,radius,stroke=bool(stroke),fill=1)
    else:
        pdf.rect(x,H-y-h,w,h,stroke=bool(stroke),fill=1)

def rule(x1,x2,y,ink="border"):
    pdf.setStrokeColor(col(ink))
    pdf.setLineWidth(.7)
    pdf.line(x1,H-y,x2,H-y)

def a(x, y, label, url, size=9, ink="tea"):
    w = pdfmetrics.stringWidth(label,"Strong",size)
    t(x,y,label,size,"Strong",ink)
    rule(x,x+w,y+size+1,ink)
    pdf.linkURL(urljoin(data["origin"],url),(x,H-y-size-5,x+w,H-y+3),relative=0,thickness=0)

def kicker(x,y,text,ink="tea"):
    t(x,y,text.upper(),8.6,"Strong",ink)

def compass():
    cx,cy=527,H-79
    pdf.setLineWidth(.8)
    pdf.setStrokeColor(col("aqua"))
    for r in (25,33):
        pdf.circle(cx,cy,r,stroke=1,fill=0)
    pdf.setFillColor(col("gold"))
    q=pdf.beginPath()
    q.moveTo(cx+12,cy+18)
    q.lineTo(cx+6,cy-7)
    q.lineTo(cx-12,cy-18)
    q.lineTo(cx-6,cy+7)
    q.close()
    pdf.drawPath(q,stroke=0,fill=1)

def header(section,title,subtitle):
    bg(0,0,W,H,"paper",radius=0)
    bg(0,0,W,142,"deep",radius=0)
    bg(0,139,W,3,"gold",radius=0)
    kicker(43,30,"Project Atlas  /  "+section,"aqua")
    t(43,52,title,41,"Display","paper")
    t(45,108,subtitle,11,"Body","paper")
    compass()

def foot(i):
    rule(42,570,746)
    t(42,758,"PROJECT ATLAS  /  RANDALL YOUNG",8.1,"Strong","muted")
    align_right(570,758,f"{i} / 2",8.1,"Strong","muted")

# 1 / Reader launchpad
header("Start here",data["title"],data["subtitle"])
wrap(43,162,data["intro"],526,10.2,15,max_lines=3)
t(43,219,"Choose your first stop",22,"Display")
for i, row in enumerate(data["routes"]):
    x=43+i*177
    bg(x,250,167,136,"wash" if i!=1 else "cream","border")
    kicker(x+12,263,f"0{i+1}  /  FIRST VISIT")
    title_end=wrap(x+12,284,row["title"],143,11.2,13,"Strong",max_lines=2)
    body_end=wrap(x+12,title_end+5,row["text"],143,9.1,12.1,ink="muted",max_lines=4)
    assert body_end <= 366
    a(x+12,369,row["label"],row["url"],size=8.0)
t(43,398,"Find your way around Atlas",22,"Display")
for i, row in enumerate(data["navigation"]):
    y=437+i*36
    if i%2==0: bg(42,y-4,528,35,"wash",radius=5)
    a(53,y+6,row["title"],row["url"],9.3)
    wrap(146,y+6,row["text"],411,9.05,12,max_lines=2)
bg(42,628,528,97,"deep",radius=10)
kicker(53,642,"A way to work with any exhibit","aqua")
for i,row in enumerate(data["workflow"]):
    x=53+i*176
    t(x,662,row["title"],11,"Strong","gold")
    wrap(x,682,row["text"],155,8.4,11.2,ink="paper",max_lines=3)
foot(1)
pdf.showPage()

# 2 / Match the question to the resource
header("Exhibit map","Six places to begin","Each card opens the exhibit. Try its first action before reading everything.")
for i,row in enumerate(data["exhibits"]):
    x=42+(i%2)*270
    y=161+(i//2)*152
    bg(x,y,258,140,"cream" if i<2 else "wash","border")
    kicker(x+13,y+12,row["topic"])
    ty=wrap(x+13,y+30,row["title"],232,16.8,17.2,"Display",max_lines=2)
    sy=wrap(x+13,ty+5,row["text"],230,9.05,11.0,ink="muted",max_lines=3)
    note_end=wrap(x+13,sy+4,row["start"],231,8.9,10.8,"Strong",max_lines=2)
    assert note_end <= y+120
    a(x+13,y+125,"Open exhibit",row["url"],8.3)
rule(42,570,621)
kicker(43,637,"Read the evidence")
wrap(43,656,data["evidence"],432,8.9,11.8,ink="muted",max_lines=3)
home="/atlas/"
a(43,701,"Open Project Atlas",home,9)
t(43,719,"project-atlas-lab.duckdns.org/atlas/",8.7,"Body","muted")
q=QrCodeWidget(urljoin(data["origin"],home),barLevel="M",barBorder=4)
bounds=q.getBounds()
ww,hh=bounds[2]-bounds[0],bounds[3]-bounds[1]
sz=73
qr=Drawing(sz,sz,transform=[sz/ww,0,0,sz/hh,-bounds[0]*sz/ww,-bounds[1]*sz/hh])
qr.add(q)
bg(497,646,73,73,"white",radius=0)
renderPDF.draw(qr,pdf,497,H-646-73)
foot(2)
pdf.showPage()
pdf.save()
print(out)
