"""Generate the ATLAS-8 operator and programmer manual from verified implementation.

Usage: python build_manual.py
Dependency: reportlab. No DOCX intermediary; diagrams and tables are vector PDF.
"""
from pathlib import Path
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, Preformatted, Flowable, NextPageTemplate
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parent
DEST=ROOT/'ATLAS8_Operators_and_Programmers_Manual_v0.5.2.pdf'
IMG=ROOT/'assets'/'ATLAS8_dashboard_desktop.png'
IMGT=ROOT/'assets'/'ATLAS8_dashboard_terminal.png'
IMGM=ROOT/'assets'/'ATLAS8_dashboard_mobile.png'
FONTS='/usr/share/fonts/truetype/dejavu'
# Font paths are Linux-centric. Windows users can use the bundled PDF
# directly; to rebuild, install DejaVu fonts and adjust FONTS above.
for key,file in [('AtlasSans','DejaVuSans.ttf'),('AtlasBold','DejaVuSans-Bold.ttf'),('AtlasMono','DejaVuSansMono.ttf'),('AtlasMonoBold','DejaVuSansMono-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(key, str(Path(FONTS)/file)))
pdfmetrics.registerFontFamily('AtlasSans', normal='AtlasSans', bold='AtlasBold', italic='AtlasSans', boldItalic='AtlasBold')
NAVY=HexColor('#142F40'); DEEP=HexColor('#0A2434'); TEAL=HexColor('#237A83')
RUST=HexColor('#B76C47'); WARM=HexColor('#F1EDE4'); BLUE=HexColor('#DCEBF0')
INK=HexColor('#263943'); GRAY=HexColor('#5E7078'); LT=HexColor('#E1E6E3'); GREEN=HexColor('#2C8066')
PAGE_W,PAGE_H=letter
MARGIN_X=50
CONTENT_W=PAGE_W-MARGIN_X*2

styles={
 'body': ParagraphStyle('body',fontName='AtlasSans',fontSize=9.25,leading=14.2,textColor=INK,spaceAfter=8),
 'lead': ParagraphStyle('lead',fontName='AtlasSans',fontSize=11.3,leading=17.8,textColor=GRAY,spaceAfter=12),
 'h1': ParagraphStyle('h1',fontName='AtlasBold',fontSize=19.2,leading=24,textColor=NAVY,spaceBefore=17,spaceAfter=9,keepWithNext=True),
 'h2': ParagraphStyle('h2',fontName='AtlasBold',fontSize=12.0,leading=16.5,textColor=TEAL,spaceBefore=13,spaceAfter=6,keepWithNext=True),
 'h3': ParagraphStyle('h3',fontName='AtlasBold',fontSize=10.2,leading=14,textColor=RUST,spaceBefore=9,spaceAfter=4,keepWithNext=True),
 'tiny': ParagraphStyle('tiny',fontName='AtlasSans',fontSize=7.5,leading=10.3,textColor=GRAY),
 'cell': ParagraphStyle('cell',fontName='AtlasSans',fontSize=7.7,leading=11.3,textColor=INK),
 'cell_head': ParagraphStyle('cell_head',fontName='AtlasBold',fontSize=8.0,leading=11.6,textColor=colors.white),
 'code': ParagraphStyle('code',fontName='AtlasMono',fontSize=8.25,leading=11.7,textColor=HexColor('#D9EDE8'),spaceBefore=0,spaceAfter=0),
 'bullet': ParagraphStyle('bullet',fontName='AtlasSans',fontSize=9.2,leading=14.0,textColor=INK,leftIndent=14,firstLineIndent=-11,spaceAfter=5),
 'caption': ParagraphStyle('caption',fontName='AtlasSans',fontSize=8.1,leading=11.5,textColor=GRAY,spaceBefore=5,spaceAfter=10),
 'cover_kicker': ParagraphStyle('cover_kicker',fontName='AtlasMonoBold',fontSize=10.0,leading=14,textColor=TEAL,spaceAfter=11),
 'cover_title': ParagraphStyle('cover_title',fontName='AtlasBold',fontSize=27,leading=32,textColor=DEEP,spaceAfter=10),
 'cover_sub': ParagraphStyle('cover_sub',fontName='AtlasSans',fontSize=12,leading=19,textColor=GRAY,spaceAfter=14),
 'toc_1': ParagraphStyle('toc_1',fontName='AtlasBold',fontSize=9.5,leftIndent=0,firstLineIndent=0,leading=16,spaceBefore=6),
 'toc_2': ParagraphStyle('toc_2',fontName='AtlasSans',fontSize=8.6,leftIndent=14,firstLineIndent=0,leading=14,spaceBefore=1,textColor=GRAY),
}

class ManualDoc(BaseDocTemplate):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.allowSplitting=1
        frame=Frame(MARGIN_X,52,CONTENT_W,PAGE_H-107,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates([PageTemplate(id='normal',frames=[frame],onPage=self.page_decor)])
    def page_decor(self,canv,doc):
        canv.saveState()
        page=doc.page
        if page==1:
            canv.setFillColor(DEEP);canv.rect(0,PAGE_H-11,PAGE_W,11,fill=1,stroke=0)
        else:
            canv.setFillColor(DEEP);canv.rect(0,PAGE_H-17,PAGE_W,17,fill=1,stroke=0)
            canv.setFont('AtlasMonoBold',7.6);canv.setFillColor(HexColor('#CEE8E8'))
            canv.drawString(MARGIN_X,PAGE_H-12,'PROJECT ATLAS / ATLAS-8')
            canv.drawRightString(PAGE_W-MARGIN_X,PAGE_H-12,'OPERATOR + PROGRAMMER MANUAL')
        canv.setStrokeColor(LT);canv.line(MARGIN_X,43,PAGE_W-MARGIN_X,43)
        canv.setFillColor(GRAY);canv.setFont('AtlasSans',7.8)
        canv.drawString(MARGIN_X,30,'0.5.2-alpha  |  22 November 2026  |  Educational PDP-8 reconstruction')
        canv.drawRightString(PAGE_W-MARGIN_X,30,str(page))
        canv.restoreState()
    def afterFlowable(self, flowable):
        if isinstance(flowable,Paragraph) and hasattr(flowable,'_toc_level'):
            txt=flowable.getPlainText()
            key='chapter_%s'%self.seq.nextf('h1') if flowable._toc_level==0 else 'sub_%s'%self.seq.nextf('h2')
            self.canv.bookmarkPage(key)
            if flowable._toc_level==0 and txt!='Contents':
                self.notify('TOCEntry',(0,txt,self.page,key))
            if flowable._toc_level==0:self.canv.addOutlineEntry(txt,key,0,False)

story=[]

def P(txt,style='body'):
    story.append(Paragraph(txt,styles[style]))
def H1(txt):
    q=Paragraph(escape(txt),styles['h1']);q._toc_level=0;story.append(q)
def H2(txt):
    q=Paragraph(escape(txt),styles['h2']);q._toc_level=1;story.append(q)
def H3(txt):story.append(Paragraph(escape(txt),styles['h3']))
def B(txt):P('<font color="#B76C47"><b>•</b></font>  '+txt,'bullet')
def CODE(source):
    text=source.strip('\n')
    box=Table([[Preformatted(text,styles['code'],maxLineLength=82,splitChars=' /-_=')]],colWidths=[CONTENT_W])
    box.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),DEEP),('BOX',(0,0),(-1,-1),.6,HexColor('#527F85')),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    story.append(box);story.append(Spacer(1,10))
def TB(headers,rows,widths=None):
    if widths is None:widths=[CONTENT_W/len(headers)]*len(headers)
    content=[[Paragraph(escape(str(h)),styles['cell_head']) for h in headers]]
    for row in rows:
        content.append([Paragraph(str(x),styles['cell']) for x in row])
    t=Table(content,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,WARM]),
        ('LINEBELOW',(0,0),(-1,0),1,TEAL),('LINEBELOW',(0,1),(-1,-1),.4,LT),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t);story.append(Spacer(1,10))
def NOTE(title,body):
    tab=Table([[Paragraph('<b>'+escape(title)+'</b>',ParagraphStyle('note_head',parent=styles['body'],textColor=TEAL,fontName='AtlasBold',spaceAfter=3))],
               [Paragraph(body,styles['body'])]],colWidths=[CONTENT_W-24])
    tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BLUE),('BOX',(0,0),(-1,-1),.7,HexColor('#9BC5CC')),
            ('LEFTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,0),10),('BOTTOMPADDING',(0,1),(-1,1),7)]))
    story.append(tab);story.append(Spacer(1,12))
def IMAGE(image_path, width=CONTENT_W,caption=None):
    from PIL import Image as PILImage
    img=PILImage.open(image_path)
    ratio=img.height/img.width
    story.append(Image(str(image_path),width=width,height=width*ratio,hAlign='CENTER'))
    if caption:P(caption,'caption')
def PAGE():story.append(PageBreak())

# COVER
story.append(Spacer(1,12))
P('HISTORICAL COMPUTING / OPERATING AND PROGRAMMING','cover_kicker')
P('ATLAS-8','cover_title')
P('PDP-8 Emulator + Programmable Calculator','cover_title')
P('Operator’s Guide and Programmer’s Reference<br/>For the dedicated Chrome PC and RP2040 MicroPython implementation','cover_sub')
NOTE('One console. Two execution targets.', 'SIMULATE runs the <b>same Python PDP-8 core</b> under CPython on the PC. LIVE PICO uses that core under MicroPython on the RP2040, reached through USB serial. Chrome renders the front panel; it is not a separate PDP-8 CPU implementation.')
IMAGE(IMG,width=430)
P('<b>Release 0.5.2-alpha</b>  |  22 November 2026<br/>Prepared for Project Atlas / Software-Defined Laboratory','tiny')
PAGE()

P('READ THIS FIRST','cover_kicker')
H1('What this release actually does')
P('ATLAS-8 is a <b>working educational PDP-8 core and browser dashboard</b>. Students load native 12-bit machine words, single-step them, inspect octal registers, and see Teletype output. The programmable calculator is the first lesson because its arithmetic is performed by PDP-8 instructions, not by a JavaScript expression evaluator.')
TB(['Verified today','Not yet verified'],[
 ('26 CPython unit/integration tests pass','Operation on the physical RP2040'),
 ('Calculator: 7+6 = 13 and 7×6 = 42','Booting original OS/8 or FOCAL'),
 ('Teletype outputs HELLO PDP-8','Original DEC hardware timing or all device IOTs'),
 ('Browser smoke: no page scrolling at tested sizes','All screen sizes; live serial USB interface'),
 ('PC SIM mode and failed-live-switch safety','MSP430 analog I/O, LINC/PDP-12 modes')],widths=[CONTENT_W/2]*2)
NOTE('Important compatibility boundary','This is <b>not yet a certified OS/8/FOCAL machine</b>. Original paper-tape loading is provisional; disk, DECtape, Extended Arithmetic Element (EAE), LINC mode and external instrument I/O are out of scope. Unsupported IOTs stop with explicit errors.')
H2('Minimum system requirements')
B('Dedicated PC: Python 3.9 or later, Chrome/Chromium or compatible browser; no internet required after setup.')
B('Optional live machine: Raspberry Pi Pico (RP2040) with MicroPython, a USB data cable and a free serial port.')
B('For LIVE PICO only: install <font face="AtlasMono">pyserial</font> on the PC. No special GUI toolkit or JavaScript build tools are required.')
H2('Thirty-second decision')
TB(['If you want to…','Use this'],[
 ('Teach or demonstrate today without a Pico','<b>SIMULATE</b> on the dedicated PC'),
 ('Show that embedded hardware executes the emulator','<b>LIVE PICO</b> after flashing and serial validation'),
 ('Write octal machine-language programs','<b>Programs</b> tab / octal loader'),
 ('Study accumulator, link, program counter','<b>Calculator</b> followed by <b>Front Panel</b>')],widths=[CONTENT_W*.58,CONTENT_W*.42])
PAGE()

H1('Contents')
toc=TableOfContents()
toc.levelStyles=[styles['toc_1'],styles['toc_2']]
story.append(toc)
PAGE()

H1('1 / The historical learning model')
P('The PDP-8 is a useful programmable-calculator analog: students encounter a machine with one 12-bit accumulator, a one-bit carry/link register, a program counter and core memory. It cannot directly evaluate “7 × 6” as a high-level expression; a program must implement the operation. This makes a small computer’s work visible.')
P('The historical line in Project Atlas is <b>LINC + PDP-8 → PDP-12 → Apollo Guidance Computer → graphical terminals</b>. ATLAS-8 currently covers the PDP-8 portion. It is intended to become the reference CPU and console component for later historical laboratory computing work.')
H2('First classroom demonstration')
B('Ask students for 7 + 6; they know the answer without a computer.')
B('Load a PDP-8 addition program; single-step and watch <b>AC</b> accumulate each operand.')
B('Repeat with 7 × 6: demonstrate repeated addition and an instruction-controlled loop.')
B('Show the physical-style lamps, switch register and octal addresses; ask why the result wraps at 12 bits.')
B('Compare this with a smartphone calculator: what architectural details are now concealed?')
H2('What is being emulated?')
P('The RP2040 runs MicroPython. The MicroPython program fetches and decodes <b>native PDP-8 instruction words</b> from emulated memory. The PDP-8 program is not compiled into ARM machine code. The dedicated PC exchanges control messages and displays state; it does not run the guest program when LIVE PICO is selected.')

H1('2 / System architecture')
TB(['Layer','Runs on','Responsibility'],[
 ('Chrome dashboard','Dedicated PC','Tabs, switches, lamps, calculator lesson, Teletype and diagnostic display'),
 ('Local HTTP server','Dedicated PC','Serves assets; selects execution engine; validates and forwards commands'),
 ('SIM target','Dedicated PC (CPython)','PDP-8 core, memory and virtual TTY; no hardware needed'),
 ('LIVE target','Pico (MicroPython)','Same PDP-8 core; USB CDC JSON lines to PC host'),
 ('Future lab I/O','MSP430G2553','Analog and digital experimental interfaces; not in this release')],widths=[113,128,CONTENT_W-241])
H2('Communication contracts')
P('Browser-to-host uses HTTP to <font face="AtlasMono">127.0.0.1:8878</font>. Host-to-Pico uses newline-delimited JSON over USB serial. A request has a numeric ID and an operation. The reply echoes the ID and includes CPU state, optional data and optional Teletype output. Processing is bounded: the browser issues repeated small <font face="AtlasMono">tick</font> requests instead of trapping the computer in a giant run loop.')
CODE('''Chrome  (five fixed-height tabs)
   |  HTTP JSON /api/command
Dedicated PC host (127.0.0.1)
   |-- SIMULATE -> CPython pdp8.py + Bridge
   `-- LIVE PICO -> USB CDC JSON lines -> MicroPython pdp8.py

Same PDP-8 machine code and instructions in either target.''')
NOTE('Mode switching and state','The two engines do <b>not</b> share RAM. Selecting another engine starts a fresh machine session. Save data or record program words before switching. A failed attempt to connect the Pico leaves the current simulator available.')

H1('3 / Installation: PC simulator')
H2('Step 1 — Unpack and test')
P('Unzip the ATLAS-8 source bundle on the dedicated PC. Open a terminal or PowerShell in the project folder containing <font face="AtlasMono">pc_dashboard_server.py</font>. Python 3.9+ is recommended. Run the desktop test suite first:')
CODE('''python -m unittest discover -s tests -v''')
P('At this release, the expected result is <b>26 tests passing</b>. This confirms local instruction behavior and the host-mode tests, not physical Pico operation.')
H2('Step 2 — Launch the dashboard')
CODE('''python pc_dashboard_server.py --mode sim --open''')
P('If the browser does not open, use the exact URL printed by the server (normally <font face="AtlasMono">http://127.0.0.1:8878/</font>). Port 8765 belongs to Active Independence, not ATLAS-8. If 8878 is busy, ATLAS-8 chooses a free port between 8879 and 8898. Browser launch requires a successful ATLAS-8 identity check. The host is accessible from the dedicated PC only.')
H2('Step 3 — First exercise')
B('The initial tab is <b>Calculator</b>. Enter A=7, operation=Add, B=6.')
B('Choose <b>LOAD NATIVE PROGRAM</b>. The instruction listing should appear.')
B('Choose <b>STEP ONE INSTRUCTION</b> to watch registers change; use <b>RUN TO HLT</b> to finish.')
B('Verify decimal 13 and octal 0015. Try 7 × 6 and verify 42 / 0052 octal.')
H2('No-scroll policy')
P('The page is viewport-fitted. Five top-level tabs replace a long scrolling page. Long instruction traces are paged, the memory inspector shows a bounded window, and front-panel subviews divide lamps, switches and controls. At unusually short viewports, reduce browser zoom or use full screen; page-level scroll is intentionally disabled.')

H1('4 / Installation: live RP2040 Pico')
H2('Flash MicroPython')
B('Confirm whether the board is Pico, Pico W or another RP2040 model; use firmware for that exact model.')
B('Hold BOOTSEL while connecting the Pico with a USB <b>data</b> cable.')
B('Copy the matching firmware UF2 from <font face="AtlasMono">micropython.org/download/</font> onto the detected RPI-RP2 drive.')
B('Wait for restart, then check the MicroPython REPL in Thonny or with <font face="AtlasMono">mpremote repl</font>. Close the REPL before using LIVE PICO.')
H2('Choose the correct Pico main.py — two mutually exclusive modes')
P('<b>MicroPython always runs Pico:/main.py when it boots.</b> The ATLAS-8 repository has two possible SOURCE files. For the Chrome LIVE PICO dashboard you must <b>copy main_dashboard.py to Pico as main.py</b>; it starts the USB JSON-lines service. The repository file named main.py instead starts a standalone text monitor with a pdp8&gt; prompt. <b>Do not install the repository main.py for Chrome mode; do not omit main.py on the Pico.</b>')
TB(['Operation','Source in checkout','Destination on Pico'],[
 ('Chrome LIVE PICO','<b>main_dashboard.py</b> — JSON bridge','<b>:main.py</b>'),
 ('Standalone text monitor','main.py — pdp8&gt; prompt',':main.py')],widths=[132,205,CONTENT_W-337])
H2('Recommended: automated Windows Pico installer')
P('On the dedicated Windows PC, install Python 3 and mpremote, close Thonny and any serial REPL, and run <b>INSTALL_PICO_WINDOWS.bat</b>. Dashboard is the default mode. It backs up existing Pico files, uploads supporting modules, installs the correct main.py last, then verifies every file by copying it back and comparing SHA-256. Select a particular Pico with <font face="AtlasMono">INSTALL_PICO_WINDOWS.bat -Port COM7</font>. For the optional text monitor use <font face="AtlasMono">-Mode Monitor</font>.')
CODE('''py -3 -m pip install mpremote pyserial
INSTALL_PICO_WINDOWS.bat -Port COM7
# Optional: standalone monitor instead of Chrome
INSTALL_PICO_WINDOWS.bat -Mode Monitor -Port COM7''')
H2('Manual dashboard installation (no backup or verification)')
P('If you must install without the script, copy these files in order. The last line is the critical mapping: dashboard source becomes Pico main.py.')
CODE('''py -3 -m mpremote fs cp pdp8.py :pdp8.py
py -3 -m mpremote fs cp programs.py :programs.py
py -3 -m mpremote fs cp tape.py :tape.py
py -3 -m mpremote fs cp monitor.py :monitor.py
py -3 -m mpremote fs cp dashboard_bridge.py :dashboard_bridge.py
py -3 -m mpremote fs cp main_dashboard.py :main.py
py -3 -m mpremote reset''')
P('Pico files and PC files are different. The <b>dashboard/</b> browser folder, <b>pc_dashboard_server.py</b>, tests and manual remain on your PC; do not upload them to RP2040. See docs/PICO_DEPLOYMENT.md for full recovery instructions. <b>Hardware installation is not yet validated on a physical Pico.</b>')
H2('Connect from the dedicated PC')
B('Start the local server with <font face="AtlasMono">python pc_dashboard_server.py --mode sim --open</font>.')
B('In the top bar, choose <b>LIVE PICO</b>, enter its serial port (for example COM7 or /dev/ttyACM0) and press <b>CONNECT</b>.')
B('The mode badge should change to LIVE RP2040 and the connection indicator should show the selected target.')
B('Repeat the calculator and Teletype demonstrations. The original PDP-8 words should produce identical results.')
NOTE('If the Pico fails to connect','A failed connection should not discard the PC simulator. Recheck the port name, cable, firmware and whether Thonny/mpremote already holds the serial port. For startup problems press Ctrl-C in a terminal to return to MicroPython REPL, then remove or replace <font face="AtlasMono">main.py</font>.')

H1('5 / A tour of the no-scroll dashboard')
TB(['Tab','Primary purpose','Operator exercise'],[
 ('01 · Calculator','Run a program that implements arithmetic','Load 7+6; step the AC and PC; compare octal/decimal'),
 ('02 · Front Panel','Read register lamps, set switches, manipulate PC and memory','Deposit an instruction and execute it'),
 ('03 · Programs','Select demos or load native octal words','Load ADD, COUNT, HELLO or SWITCH ADDER'),
 ('04 · Teletype','Observe guest TTY IOT output; queue keyboard input','Run HELLO PDP-8; inspect character stream'),
 ('05 · Guide','In-dashboard memory aid','Follow the four introductory activities')],widths=[114,165,CONTENT_W-279])
H2('The desktop interface')
IMAGE(IMG,caption='Calculator-first dashboard. The two execution modes use exactly the same five tabs, not separate browser applications.')
H2('The Teletype interface')
IMAGE(IMGT,caption='Character output originates in PDP-8 Teletype IOT instructions. A limited TTY model is included; it is not a cycle-accurate mechanical ASR-33.')

H1('6 / The programmable calculator')
H2('Arithmetic conventions')
P('The PDP-8 word length is 12 bits. Machine words and addresses are displayed in octal; four octal digits are sufficient because 4 × 3 = 12 bits. The data range is 0000–7777 octal (0–4095 unsigned). A signed two’s-complement interpretation is −2048 through +2047; the hardware itself still stores exactly the same 12 bits.')
TB(['Example','Unsigned decimal','Octal','Signed 12-bit'],[
 ('7 + 6','13','0015','13'),('7 × 6','42','0052','42'),('6 − 7','4095','7777','−1'),('4095 + 1','0 (wrap)','0000','0')],widths=[112,130,120,CONTENT_W-362])
H2('Native addition: 7 + 6')
CODE('''Addr   Word   Instruction           What it changes
0200   7300   CLA CLL               AC <- 0, LINK <- 0
0201   1250   TAD 0250              AC <- AC + M[0250] (7)
0202   1251   TAD 0251              AC <- AC + M[0251] (6)
0203   3252   DCA 0252              M[0252] <- AC; AC <- 0
0204   1252   TAD 0252              AC <- saved result (13)
0205   7402   HLT                   Stop
0250   0007   first input
0251   0006   second input
0252   0015   result after run''')
P('This is executed PDP-8 word code. The browser creates input values and asks the CPU to load and execute a program, but does not calculate the result itself.')
H2('Subtraction and multiplication')
P('Subtraction uses two’s-complement negation: complement the subtrahend and increment it, then add the minuend. Multiplication has no single general-purpose multiply instruction in the base PDP-8; the lesson performs repeated addition with an <font face="AtlasMono">ISZ</font> loop counter. The dashboard caps the multiplier B at 256 for responsiveness and instructional clarity. Both cases wrap modulo 4096.')
NOTE('Instructional observation','Ask students: “What is an instruction?” “Where is the answer during execution?” “Why does the accumulator become zero after DCA?” “What would happen if the machine had only eight bits?”')

H1('7 / Front-panel operator procedures')
H2('Registers and indicators')
TB(['Label','Meaning'],[
 ('PC','Program counter: address of the next instruction in the current instruction field.'),
 ('AC','12-bit accumulator: arithmetic and logic operand/result.'),
 ('LINK / L','Single carry/link bit, rotated with the accumulator in some OPR instructions.'),
 ('MQ','Multiplier-quotient register; basic transfer operations supported.'),
 ('IR','Last executed/fetched instruction (educational display).'),
 ('MA / MB','Dashboard memory address cursor and last displayed memory buffer value; interpretive controls.'),
 ('IF / DF','Instruction/data field selectors, for optional memory extension.'),
 ('SR','12-bit console switch register, exposed to guest code with OSR.')],widths=[94,CONTENT_W-94])
H2('Manual deposit-and-execute exercise')
P('The following program clears AC, increments it, and halts. All words are octal. Perform the steps in Front Panel/Operator Controls or enter the words on Programs/Octal Loader.')
CODE('''0200  7200  CLA
0201  7001  IAC
0202  7402  HLT''')
B('Clear memory (confirmation required), then set switch register to <font face="AtlasMono">0200</font> and choose <b>LOAD ADDRESS</b>.')
B('Set SR=<font face="AtlasMono">7200</font>, DEPOSIT; then SR=<font face="AtlasMono">7001</font>, DEPOSIT; then SR=<font face="AtlasMono">7402</font>, DEPOSIT.')
B('Set SR=<font face="AtlasMono">0200</font> and LOAD ADDRESS again; single-step three instructions.')
B('Confirm AC=<font face="AtlasMono">0001</font> and PC=<font face="AtlasMono">0203</font>. The CPU should report a halt.')
P('The front panel is a functional <b>educational interpretation</b>, not a claim to duplicate every switch and mechanical function on the 1965 PDP-8, later PDP-8/E or PDP-12 front panel.')
H2('RESET versus CLEAR')
P('<b>RESET CPU</b> clears registers and flags while retaining emulated memory. <b>CLEAR MEMORY</b> clears both registers and all installed memory fields. Switching engines also starts a new session; there is no automatic memory migration.')

H1('8 / PDP-8 programmer’s reference')
H2('The 12-bit instruction word')
P('The three most significant bits select the broad instruction class. Opcodes 0 through 5 are memory-reference instructions (MRI). Opcode 6 is I/O transfer (IOT), and opcode 7 is microcoded operate (OPR). A memory-reference instruction uses bits for indirect addressing, page selection, and seven low-order offset bits.')
TB(['Octal base','Mnemonic','Emulator action'],[
 ('0000','AND','AC <- AC AND memory operand'),
 ('1000','TAD','Add operand to AC; carry toggles LINK through 13-bit sum'),
 ('2000','ISZ','Increment memory operand; skip next if result is zero'),
 ('3000','DCA','Deposit AC into operand; clear AC'),
 ('4000','JMS','Store return PC at subroutine entry and jump to next word'),
 ('5000','JMP','Unconditional branch to target'),
 ('6000','IOT','Device and CPU control operations'),
 ('7000','OPR','Microcoded arithmetic, logical, skip, halt or MQ operations')],widths=[93,87,CONTENT_W-180])
H2('Effective addressing')
B('Page bit 0: use zero-page address <font face="AtlasMono">0000–0177</font>. Page bit 1: use the 128-word page containing the current instruction.')
B('Indirect bit 0: the selected address is the operand address. Indirect bit 1: read a pointer from that location; use its contents as the effective address.')
B('Autoindex cells <font face="AtlasMono">0010–0017</font> in field zero are incremented before their contents are used as indirect pointers.')
B('With memory extension, data-reference operations use DF for indirect data, while branch operations use the current instruction field or pending instruction field. These subtleties are selected-test validated but not exhaustively proven against all PDP-8 variants.')
H2('Group 1 OPR')
TB(['Word / mask','Mnemonic','Behavior'],[
 ('7200','CLA','Clear accumulator'),('7100','CLL','Clear LINK'),('7040','CMA','Complement accumulator'),
 ('7020','CML','Complement LINK'),('7001','IAC','Increment combined AC/LINK'),
 ('7004 / 7006','RAL / RTL','Rotate left one/two positions'),('7010 / 7012','RAR / RTR','Rotate right one/two positions'),
 ('7002','BSW','PDP-8/E byte swap; included in this core')],widths=[112,100,CONTENT_W-212])
P('The emulator applies Group 1 microoperations in a defined order. Some combinations are legal; undefined rotate patterns raise an error in strict mode.')
H2('Group 2 and Group 3 OPR')
TB(['Mnemonic','Purpose'],[
 ('SMA / SZA / SNL','Skip on negative accumulator / zero accumulator / nonzero LINK'),
 ('SPA / SNA / SZL / SKP','Complemented skip tests / unconditional skip'),
 ('OSR','OR the front-panel switch register into AC'),
 ('HLT','Halt execution (e.g., word 7402)'),
 ('MQA / MQL','Transfer data between AC and MQ in supported combinations'),
 ('EAE','Not implemented; unsupported instructions produce explicit errors')],widths=[150,CONTENT_W-150])

H1('9 / Native console I/O and interrupts')
H2('Implemented Teletype instruction set')
TB(['Octal','Mnemonic','Meaning'],[
 ('6030','KCF','Clear keyboard ready flag'),('6031','KSF','Skip next if keyboard ready'),
 ('6032','KCC','Clear keyboard flag and accumulator'),('6034','KRS','OR keyboard buffer into accumulator'),
 ('6035','KIE','Enable/disable TTY interrupt (PDP-8/E convenience)'),('6036','KRB','Read keyboard buffer and clear flag'),
 ('6040','TFL','Set teleprinter flag ready (PDP-8/E convenience)'),('6041','TSF','Skip if teleprinter ready'),
 ('6042','TCF','Clear teleprinter ready flag'),('6044','TPC','Print AC character'),
 ('6045','TSK','Skip if input or output flag is ready'),('6046','TLS','Send character and clear output flag')],widths=[78,89,CONTENT_W-167])
P('The Teletype is a character-stream approximation. The ready flag uses simulated instruction ticks, not period mechanical timing. The `HELLO PDP-8` demo generates characters through genuine 604x IOT instructions.')
H2('CPU interrupt and memory extension subset')
P('Selected CPU IOTs include <font face="AtlasMono">ION</font>, <font face="AtlasMono">IOF</font>, <font face="AtlasMono">SKON</font>, <font face="AtlasMono">SRQ</font> and <font face="AtlasMono">CAF</font>. Memory-control IOTs include CDF/CIF and limited RDF/RIF/RIB/RMF behavior. The unit tests exercise representative cases. This is not yet an exhaustive recreation of all interrupt and device semantics.')

H1('10 / Entering and running machine programs')
H2('Programs tab: native demonstrations')
TB(['Program','What students should observe'],[
 ('ADD TWO CONSTANTS','Two operands are accumulated by TAD; final AC is 0015 octal.'),
 ('COUNT TO ZERO','ISZ increments a negative-count word and skips when it reaches zero.'),
 ('SWITCH ADDER','OSR reads the dashboard switch register into AC before adding a constant.'),
 ('HELLO PDP-8','Keyboard-independent output is generated by a loop using Teletype IOT instructions.')],widths=[153,CONTENT_W-153])
H2('Programs tab: octal loader')
P('Enter the starting address, choose memory field, paste 1–64 octal words, and load. For example:')
CODE('''Origin: 0200     Field: 0
Words:  7300 1250 1251 3252 1252 7402''')
P('This sequence expects the first operand at address 0250 and the second at 0251; without those data values it will only add zeros. Deposit 0007 at 0250 and 0006 at 0251 using the front panel or the memory interface, set PC to 0200, and run.')
P('The <b>Octal Loader</b> is the primary custom-program entry path in the dashboard. The CLI monitor separately supports file-based RIM/BIN and octal-text loading. The browser does not yet expose arbitrary host-file upload.')
H2('Native word versus host representation')
P('Machine code is shown in octal for human readers. Under the JSON protocol the same 12-bit word is transported as a decimal integer. The host does not reinterpret the instruction or translate it to ARM code.')

H1('11 / Teletype and paper-tape handling')
H2('Teletype walkthrough')
B('Open Programs and choose HELLO PDP-8.')
B('Return to Front Panel / Operator Controls, press RUN and allow the machine to halt.')
B('Open Teletype and verify the phrase <font face="AtlasMono">HELLO PDP-8</font>.')
B('Try sending a short string from the Teletype keyboard. It enters the simulated keyboard queue; it appears only if guest code reads it.')
P('The TTY screen uses a bounded character buffer. Long output may cause older characters to leave the displayed window. It is not archival storage.')
H2('RIM and BIN paper tapes — CLI only')
P('The command-line monitor supports provisional RIM and BIN loading. Synthetic fixtures are tested; original DEC media compatibility is not established. RIM loads words into memory, but executing a historical interpreter also requires its original memory size, entry point, and exact I/O expectations.')
CODE('''# CLI monitor examples (not dashboard commands)
pdp8> reset clear
pdp8> load rim original.rim
pdp8> pc 0200
pdp8> run 10000
pdp8> regs''')
P('The <font face="AtlasMono">0200</font> entry point is illustrative, not universal. Never assume an original tape starts at that address. An unsupported IOT is a useful diagnostic, not a reason to silently skip a device instruction.')

H1('12 / Dashboard command protocol')
P('ATLAS-PDP8/1 is intentionally small and inspectable. The browser sends commands to the local server; the host dispatches them to the selected backend. JSON requests use ordinary integer values, while the UI displays octal labels.')
CODE('''POST /api/command  Content-Type: application/json
{"id":1,"op":"calculator",
 "args":{"operation":"add","a":7,"b":6}}

Reply: {"id":1,"ok":true,"state":{...},"data":{...}}

POST /api/mode
{"mode":"sim"}
{"mode":"serial","port":"COM7"}''')
H2('Principal bridge operations')
TB(['Operation','Effect'],[
 ('hello / status','Identify protocol and retrieve complete CPU state'),
 ('calculator / demo','Load built-in native instruction programs'),
 ('switches / panel_addr','Set SR, PC and front-panel cursor'),
 ('examine / deposit','Read or write emulated memory'),
 ('load_words','Load up to 64 native words in one call'),
 ('step / start / tick / halt','Control bounded CPU execution'),
 ('keyboard','Queue characters for the guest keyboard'),
 ('reset / field / breakpoint','Reset machine, select fields, manage debug stops')],widths=[189,CONTENT_W-189])
H2('Why bounded execution matters')
P('A direct unlimited run could prevent the host from honoring STOP while the guest loops. ATLAS-8 uses a start command and repeated capped execution bursts. The server serializes requests against each backend to prevent conflicting memory operations. A hardware-specific future implementation can add asynchronous stop channels, but this release favors simplicity and inspectability.')

H1('13 / Troubleshooting and recovery')
TB(['Symptom','Likely cause and action'],[
 ('Browser does not load','Check the host window for the actual URL; the default is 8878, but an occupied port triggers a fallback. Do not use 8765.'),
 ('Page appears disconnected','Restart host; inspect server output; verify /api/info responds.'),
 ('LIVE PICO fails','Port name incorrect, board not flashed, or serial port owned by Thonny/mpremote. SIM remains available.'),
 ('MicroPython ImportError','Copy all dashboard runtime modules; copy main_dashboard.py as main.py last.'),
 ('Program stops on unattached IOT','Guest requires unsupported device. Record octal opcode; do not suppress it.'),
 ('Calculator shows wrapping','12-bit arithmetic is modulo 4096; switch decimal/octal for interpretation.'),
 ('No Teletype output','Load HELLO, RUN to HLT, then inspect the TTY tab; check 604x IOT flow.'),
 ('Memory does not persist across engine switch','Intentional session reset; preserve program listing/snapshot separately.'),
 ('Not enough Pico memory','Use one 4K field; avoid 32K until physical heap has been measured.'),
 ('No scroll on small monitor','Use browser full screen or reduce zoom; the dashboard pages content instead of scrolling.')],widths=[164,CONTENT_W-164])
H2('Pico recovery sequence')
P('First close the PC dashboard host and reconnect with a serial REPL. Send Ctrl-C to interrupt the dashboard bridge. Rename or remove <font face="AtlasMono">main.py</font> to prevent automatic restarting. If the board remains unresponsive, reflash the appropriate UF2; do this only after trying ordinary REPL recovery.')

H1('14 / Validation and operator acceptance tests')
H2('Automated tests')
CODE('''python -m unittest discover -s tests -v
# Expected in v0.5.1: 30 tests, all OK

python tests/browser_smoke.py
# Expected: no page overflow, no JS exceptions;
# calculator 13 and 42; HELLO PDP-8 via guest TTY.''')
P('The browser smoke uses a mocked request transport to a real Python Bridge, not a connected Pico. There are three host tests covering static/API metadata, switching a SIM session, and safe retention of SIM when live mode lacks a port.')
H2('First live hardware acceptance checklist')
for st in [
 'Confirm actual Pico model and MicroPython version; record port and cable type.',
 'Verify raw JSON-line hello request and matching response over USB serial.',
 'Use selector to connect LIVE PICO with no other REPL client open.',
 'Run 7+6 and 7×6; verify result register, link and instruction count.',
 'Run HELLO PDP-8 and verify TTY string.',
 'Deposit 7200, 7001, 7402 at 0200; step to AC=0001.',
 'Disconnect USB during operation; confirm visible error and recoverability.',
 'Repeat after a full power cycle; record any required Pico-specific changes.'
]:B(st)
NOTE('Release gate','The 30 desktop tests and browser smoke tests have passed, but physical acceptance tests are <b>still open</b>. Do not label this build as validated live hardware or native OS/8 compatible until those separate milestones are met.')

H1('15 / Classroom laboratory sequence')
TB(['Activity','Learner evidence'],[
 ('01 — Calculator as a machine','Annotated trace of 7+6, explaining AC/PC/HLT in words.'),
 ('02 — Number base and word size','Octal/decimal table including 7777 and 0000 wrapping.'),
 ('03 — Front-panel programming','A deposited 3-instruction program and verified register result.'),
 ('04 — Loops and decisions','Trace of ISZ/JMP loop; identify how the loop terminates.'),
 ('05 — Input and output','HELLO Teletype output, linked to TLS/TSF IOT behavior.'),
 ('06 — Historical comparison','Explain what a LINC SAM/DIS extension would add to PDP-8.'),
 ('07 — Two execution targets','Same machine program and result on PC SIM and verified live Pico.'),
 ('08 — SDL bridge','Map read/plot/control operations to a future software-defined laboratory.')],widths=[183,CONTENT_W-183])
P('This sequence intentionally begins with the PDP-8 as a programmable calculator, then progresses to a computer that handles loops and terminals. Laboratory measurement is a later extension through LINC/PDP-12 and the MSP430. Each lesson should begin with an observable problem, then use historical context and implementation to explain the solution.')

H1('16 / Roadmap: toward LINC, PDP-12 and SDL')
H2('Next engineering milestones')
B('<b>Physical acceptance:</b> Verify the JSON-line MicroPython bridge on the target Pico.')
B('<b>Historical PDP-8 software:</b> Establish a validated RIM paper-tape load, run a real tiny PAL or FOCAL image, and add only necessary device IOTs.')
B('<b>PDP-12:</b> Implement a separate LINC instruction mode and accurate mode switching; keep the PDP-8 CPU core modular.')
B('<b>Laboratory hardware:</b> Attach MSP430 analog and digital I/O to LINC functions such as sample and display, with safe voltage conversion.')
B('<b>SDL:</b> Derive portable SAMPLE, PLOT, CONTROL, TRIGGER and RECORD operations from functioning historical reference behavior.')
B('<b>Portability:</b> Connect Arduino UNO, micro:bit V2, M5Stack ESP32-S3, and finally low-cost smartphones as user interfaces and portable labs.')
P('The sequence preserves the central Project Atlas idea: begin at the historical problem, reconstruct the operating principle, then extend it to accessible contemporary tools.')

H1('Appendix A / Quick-reference card')
TB(['Task','Where','Action'],[
 ('Start desktop','PC shell','python pc_dashboard_server.py --mode sim --open'),
 ('Connect Pico','Topbar','LIVE PICO → port name → CONNECT'),
 ('Add 7 and 6','Calculator','A=7, Add, B=6, Load, Run to HLT'),
 ('Multiply 7 and 6','Calculator','A=7, Multiply, B=6, Load, Run to HLT'),
 ('Inspect registers','Front Panel','Registers & lamps'),
 ('Deposit instruction','Front Panel','Set SR, Load Address, Deposit'),
 ('Load octal code','Programs','Octal Loader: origin + 1–64 words'),
 ('Observe guest output','Teletype','Run HELLO demo then Teletype tab'),
 ('Recover from fault','PC/Pico','Stop host, reclaim serial REPL, check Pico main.py')],widths=[111,101,CONTENT_W-212])
H2('PDP-8 vocabulary')
TB(['Term','Definition'],[
 ('Word','One 12-bit quantity (0000–7777 octal).'),('Core','The emulated 12-bit memory array.'),
 ('Field','A bank of 4096 words; optional extension up to eight fields.'),('PC','Program counter; next instruction location.'),
 ('AC','Accumulator; central arithmetic/logic register.'),('L','Link bit; participates in carry and rotate operations.'),
 ('IOT','Input/output transfer instruction; controls guest devices.'),('OPR','Microcoded operate instruction; many register functions packed in one word.'),
 ('RIM/BIN','Historical punched paper-tape loader formats; provisional support.')],widths=[87,CONTENT_W-87])

H1('Appendix B / Files, sources and boundaries')
TB(['File','Role'],[
 ('pdp8.py','MicroPython/CPython PDP-8 CPU, memory and I/O core'),
 ('programs.py','Native demos and calculator word-code generators'),
 ('dashboard_bridge.py','JSON-line / JSON-object bridge to the CPU'),
 ('main_dashboard.py','Dashboard mode source: install on Pico as main.py'),
 ('main.py, monitor.py, tape.py','Standalone text monitor main.py; monitor and tape helpers'),
 ('pc_dashboard_server.py','Dedicated PC HTTP server and SIM/LIVE transport selector'),
 ('dashboard/index.html','Single fixed-height five-tab interface'),
 ('dashboard/style.css, app.js','Presentation and browser protocol client'),
 ('tests/','CPython CPU, host, and browser smoke tests'),
 ('INSTALL_PICO.ps1 / .bat','Windows Pico deploy, backup, readback verification'),
 ('docs/','PICO_DEPLOYMENT, INSTALL, OPERATOR, PROTOCOL')],widths=[184,CONTENT_W-184])
H2('Reference material')
P('For historical instruction semantics, consult Digital Equipment Corporation PDP-8/PDP-8/E programming handbooks and field-maintenance documentation; Doug Jones’s University of Iowa PDP-8 FAQ; and the open-source SIMH PDP-8 simulator. These references are useful for comparing obscure instruction combinations and IOT behavior. They do not independently validate the present build.')
P('Source pointers: <font face="AtlasMono">github.com/simh/simh</font> and <font face="AtlasMono">homepage.cs.uiowa.edu/~jones/pdp8/</font>. Historical binary media may impose their own licensing and provenance requirements. This bundle includes <b>original educational demos</b>, not a packaged DEC OS/8 or FOCAL distribution.')
H2('Version declaration')
P('This manual describes the source tree in ATLAS-8 v0.5.2-alpha as inspected and tested on 22 November 2026. If dashboard behavior changes, regenerate the manual and rerun all verification. The operator should prioritize the executable source and automated tests when a disagreement is found.')
NOTE('The point of the project','Students are not merely operating an old-style computer. They are discovering how an instruction, register, measured signal and human question connect—and how those same ideas later reappear in LINC, the Arduino Revolution and the smartphone laboratory.')

# doc render
manual=ManualDoc(str(DEST),pagesize=letter,leftMargin=MARGIN_X,rightMargin=MARGIN_X,topMargin=44,bottomMargin=48,
                 title='ATLAS-8: Operator and Programmer Manual',author='Project Atlas / SDL',
                 subject='PDP-8 MicroPython RP2040 emulator with unified Chrome dashboard')
manual.multiBuild(story)
print(f'PDF GENERATED: {DEST} ({DEST.stat().st_size} bytes)')
