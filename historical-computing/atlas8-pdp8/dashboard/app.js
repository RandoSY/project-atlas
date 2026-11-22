/* Project Atlas ATLAS-8 dashboard — plain JavaScript, no build step.
 * A single HTTP request maps to one simulator/Pico command. The host does not
 * execute calculator arithmetic: it loads actual PDP-8 machine instructions.
 */
'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const mask = 0o7777;
  const oct = (n, width=4) => ((Number(n) || 0) & mask).toString(8).padStart(width, '0');
  const decSigned = n => ((n & mask) & 0o4000) ? (n & mask) - 4096 : (n & mask);
  const ui = {
    counter: 0, state: null, busy: false, calculating: false, loaded: false,
    base: 'dec', list: [], activeAddr: null, recentAddr: null,
    memoryAddress: 0o200, memoryField: 0, polling: false,
    stopped: false, pendingSwitch: false, toastTimer: null, ttyText: '', tracePage: 0,
    singleInstruction: false, panelLocked: false, lessonStep: 0,
  };
  const names = [['PC', 'pc'], ['AC', 'ac'], ['L', 'l'], ['MA', 'ma'], ['MB', 'mb'], ['IR', 'ir']];
  const lessonWords=[0o7301,0o7001,0o7430,0o7402,0o5001];

  function toast(message, bad=false) {
    const el = $('toast');
    el.textContent = message;
    el.classList.toggle('bad', bad);
    el.classList.add('show');
    clearTimeout(ui.toastTimer);
    ui.toastTimer = setTimeout(() => el.classList.remove('show'), 3200);
  }

  async function api(op, args={}) {
    const id = ++ui.counter;
    const result = await fetch('/api/command', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id,op,args}),
    });
    if (!result.ok) {
      let body;
      try { body = await result.json(); } catch { body = {}; }
      throw new Error(body.error || `Host returned HTTP ${result.status}`);
    }
    const payload = await result.json();
    if (payload.id !== id) throw new Error('Mismatched response ID');
    if (payload.state) {ui.state = payload.state; renderState();}
    if (payload.tty) appendTty(payload.tty);
    if (!payload.ok) throw new Error(payload.error || `Command ${op} failed`);
    return payload;
  }

  async function command(op, args={}, reportErrors=true) {
    // Prevent an accidental batch of simultaneous commands from racing a RUN.
    if (ui.busy) return null;
    ui.busy = true;
    try { return await api(op,args); }
    catch (error) {
      ui.stopped = true;
      ui.polling = false;
      $('panelMessage').textContent = error.message;
      if (reportErrors) toast(error.message,true);
      return null;
    }
    finally { ui.busy = false; }
  }

  function makeLampLine(name, property) {
    const row = document.createElement('div');
    row.className = 'register-row' + (name === 'AC' ? ' featured' : '');
    row.dataset.field = property;
    const title = document.createElement('span'); title.className = 'register-name'; title.textContent = name;
    const lamps = document.createElement('div'); lamps.className = 'register-lights';
    for (let group=0; group<(property==='l'?1:4); group++) {
      const block=document.createElement('div'); block.className='lamp-group';
      for (let bit=(property==='l'?0:11-group*3);bit>=(property==='l'?0:9-group*3);bit--) {
        const lamp=document.createElement('span');lamp.className='lamp';lamp.dataset.bit=String(bit);
        lamp.setAttribute('aria-hidden','true');
        block.appendChild(lamp);
      }
      lamps.appendChild(block);
    }
    const value=document.createElement('span');value.className='reg-value';value.textContent='0000';
    row.append(title,lamps,value);
    $('registers').appendChild(row);
  }
  function makeToggle(bit,kind) {
    const btn=document.createElement('button');btn.type='button';btn.className='switch-key';
    btn.dataset.bit=String(bit);btn.dataset.kind=kind;
    btn.setAttribute('aria-label',`${kind==='word'?'Switch register':kind==='df'?'Data field':'Instruction field'} bit ${bit}`);
    btn.setAttribute('aria-pressed','false');
    const label=document.createElement('span');label.className='bit-label';label.textContent=String(bit).padStart(2,'0');
    const housing=document.createElement('span');housing.className='toggle-housing';
    const handle=document.createElement('span');handle.className='toggle-handle';
    housing.appendChild(handle);btn.append(label,housing);
    btn.addEventListener('click',async()=>{
      if(!ui.state||ui.busy||ui.panelLocked)return;
      if(kind==='word'){
        const value=ui.state.switches^(1<<bit);
        const response=await command('switches',{value});
        if(!response)toast('Switch operation failed.',true);
      } else {
        const ifield=kind==='if'?(ui.state.ifield^(1<<bit)):ui.state.ifield;
        const dfield=kind==='df'?(ui.state.dfield^(1<<bit)):ui.state.dfield;
        await command('panel_fields',{ifield,dfield});
      }
    });
    return btn;
  }
  function buildPanel() {
    names.forEach(([name,field])=>makeLampLine(name,field));
    for(let bit=11;bit>=0;bit--)$('switches').appendChild(makeToggle(bit,'word'));
    for(let bit=2;bit>=0;bit--){
      $('dataFieldSwitches').appendChild(makeToggle(bit,'df'));
      $('instructionFieldSwitches').appendChild(makeToggle(bit,'if'));
    }
  }
  function updateLesson() {
    const steps=[
      ['Set address 0000, then press LOAD ADD.',0],
      ...lessonWords.map((word,index)=>[`Set ${oct(word)} for address ${oct(index)}, then press DEP.`,word]),
      ['Set 0000 and LOAD ADD to return to program start.',0],
      ['Press START to execute the toggled-in program.',0]
    ];
    const index=Math.min(ui.lessonStep,steps.length);
    $('lessonTarget').textContent=index>=steps.length?'Program running or complete. EXAM or SING INST to explore.':`Step ${index+1}: ${steps[index][0]}`;
    $('lessonProgress').textContent=`${index}/${steps.length} actions`;
    $('btnPanelPreset').disabled=index>=steps.length;
  }
  function lessonPanelAction(name,address,value) {
    const n=ui.lessonStep;
    if(n===0&&name==='load'&&address===0)ui.lessonStep++;
    else if(n>=1&&n<=5&&name==='deposit'&&address===n-1&&value===lessonWords[n-1])ui.lessonStep++;
    else if(n===6&&name==='load'&&address===0)ui.lessonStep++;
    else if(n===7&&name==='start')ui.lessonStep++;
    updateLesson();
  }

  function renderSwitches() {
    if (!ui.state) return;
    const value=ui.state.switches;
    $('switchReadout').textContent='';
    $('switchReadout').append(document.createTextNode(oct(value)+' '));
    const note=document.createElement('small');note.textContent='OCT';$('switchReadout').append(note);
    for (const btn of $('switches').children) btn.setAttribute('aria-pressed',Boolean(value & (1<<Number(btn.dataset.bit))).toString());
    for(const btn of $('dataFieldSwitches').children){btn.setAttribute('aria-pressed',Boolean(ui.state.dfield&(1<<Number(btn.dataset.bit))).toString());btn.disabled=ui.state.fields===1;}
    for(const btn of $('instructionFieldSwitches').children){btn.setAttribute('aria-pressed',Boolean(ui.state.ifield&(1<<Number(btn.dataset.bit))).toString());btn.disabled=ui.state.fields===1;}
  }

  function updateRegister(property,value) {
    const row=$('registers').querySelector(`.register-row[data-field="${property}"]`);
    if (!row) return;
    row.querySelector('.reg-value').textContent=property==='l'?String(value):oct(value);
    for (const lamp of row.querySelectorAll('.lamp')) lamp.classList.toggle('on',Boolean(value & (1<<Number(lamp.dataset.bit))));
  }

  function renderState() {
    const s=ui.state;
    if (!s) return;
    for (const [,field] of names) updateRegister(field,s[field]);
    $('statPc').textContent=oct(s.pc);$('statAc').textContent=oct(s.ac);
    $('statLink').textContent=String(s.l);$('statFields').textContent=`${s.ifield} / ${s.dfield}`;
    $('statDf').textContent=String(s.dfield);$('statIf').textContent=String(s.ifield);
    for(const [i,el] of [...$('opcodeLamps').children].entries())el.classList.toggle('on',s.instructions>0 && (s.ir>>>9)===i);
    $('instructionCounter').textContent=`${s.instructions.toLocaleString()} EXECUTED`;
    $('flagKbd').classList.toggle('active',s.tty_kbd_ready);
    $('flagTty').classList.toggle('active',s.tty_print_ready);
    $('flagIon').classList.toggle('active',s.ion);
    $('flagBreak').classList.toggle('active',(s.breakpoints||[]).length>0);
    const running=s.running&&!s.halted;
    $('cpuRunStatus').textContent=running?'RUNNING':(s.reason==='BREAKPOINT'?'BREAKPOINT':'HALTED');
    $('cpuRunStatus').classList.toggle('running',running);
    $('btnSingleInstruction').setAttribute('aria-pressed',String(ui.singleInstruction));
    $('panelLock').setAttribute('aria-pressed',String(ui.panelLocked));
    $('panelMessage').textContent=s.reason || (running?'Executing bounded instruction batches.':'Machine ready.');
    renderSwitches();
    if (s.calculator && ui.loaded) {
      const result=s.calculator.result;
      const complete=s.calculator.complete;
      $('calcResult').textContent=complete?formatValue(result):'…';
      $('calcLink').textContent=String(s.l);
      $('calcResultDetail').textContent=complete?
        `OCT ${oct(result)} · decimal ${result} · signed ${decSigned(result)}`:
        `Core result at 0252: ${oct(result)} · ${s.instructions} instructions`;
      $('calcExplanation').querySelector('p').textContent=explanation(s);
    } else if (!ui.loaded) {
      $('calcResult').textContent='—';$('calcResultDetail').textContent='Load a program to begin.';
      $('calcLink').textContent=String(s.l);
    }
    if ($('tapeReadout') && s.tape){
      const t=s.tape;
      const rate=t.nominal_cps===null?'TURBO':`${t.nominal_cps} cps`;
      const condition=t.paused?'PAUSED':t.ready?'FRAME READY':t.eof?'END OF TAPE':t.pending?'FEEDING':'STANDBY';
      $('tapeReadout').textContent=t.size?`READER ${t.position}/${t.size} frames · ${rate} · observed ${t.effective_cps || 0} cps · ${condition} · PUNCH ${t.punch_bytes}`:'Tape not mounted';
      $('tapeProgress').max=Math.max(1,t.size);
      $('tapeProgress').value=t.position;
      // Do not overwrite the speed currently being selected while an API call is pending.
      if(document.activeElement!==$('tapeSpeed')) $('tapeSpeed').value=t.speed;
    }
    if($('labReadout') && s.lab) {
      const lab=s.lab;
      const value=lab.mode==='timer'?`${lab.value} ticks`:lab.value + ' ADC counts';
      $('labReadout').textContent=`${lab.kind.toUpperCase()} · ${lab.online?'ONLINE':'OFFLINE'} · ${lab.busy?'BUSY':lab.ready?'READY':'IDLE'} · ${value}${lab.error?' · ERROR: '+lab.error:''}`;
    }
    $('instructionHint').textContent=`PC ${oct(s.pc)}`;
    if (ui.list.length) markActiveLine(s.pc);
  }

  function explanation(s) {
    if (!s.calculator) return 'Load a calculator example to study the instruction sequence.';
    const operation=s.calculator.operation;
    const base = 'The PDP-8 stores only 12-bit words: arithmetic wraps modulo 4096; LINK records carries independently.';
    if (operation==='multiply') return `Multiplication repeats TAD (add) while ISZ advances a negative loop count toward zero. ${base}`;
    if (operation==='subtract') return `Subtraction forms the two's complement with CMA and IAC, then uses TAD. ${base}`;
    return `Addition loads A and B with TAD, stores the result with DCA, and finally executes HLT. ${base}`;
  }

  function formatValue(v) {return ui.base === 'oct'?oct(v):String(v&mask);}
  function parseOct(id,max=0o7777) {
    const raw=$(id).value.trim();
    if (!/^[0-7]+$/.test(raw)) throw new Error(`${id}: enter an octal number (digits 0–7)`);
    const n=parseInt(raw,8);
    if(n>max) throw new Error(`${id}: must be at most ${max.toString(8)}`);
    return n;
  }
  function parseOperand(raw) {
    const value=String(raw).trim();
    const re=ui.base==='oct'?/^[0-7]+$/:/^[0-9]+$/;
    if(!re.test(value))throw new Error(`Enter a nonnegative ${ui.base==='oct'?'octal':'decimal'} integer.`);
    const n=parseInt(value,ui.base==='oct'?8:10);
    if(n<0||n>4095)throw new Error('Calculator operands must be 0–4095 (0000–7777 octal).');
    return n;
  }

  function disasm(word,addr) {
    const code=word>>9;
    if(code<6) {
      const names=['AND','TAD','ISZ','DCA','JMS','JMP'];
      const indirect=(word&0o400)?' I':'';
      const zero=(word&0o200)?' C':' Z';
      return names[code]+indirect+zero+' '+(word&0o177).toString(8).padStart(3,'0');
    }
    if(code===6) {
      const dict={0o6011:'RSF',0o6012:'RRB',0o6014:'RFC',0o6016:'RRB RFC',0o6031:'KSF',0o6032:'KCC',0o6034:'KRS',0o6036:'KRB',0o6041:'TSF',0o6046:'TLS',0o6044:'TPC',0o6540:'LABCLR',0o6541:'LABGO',0o6542:'LABRDY',0o6543:'LABTIM',0o6544:'LABGET',0o6545:'LABSTS',0o6546:'LABHI',0o6547:'LABTOP',0o6001:'ION',0o6002:'IOF'};
      return dict[word]||'IOT '+oct(word);
    }
    const known={0o7000:'NOP',0o7200:'CLA',0o7300:'CLA CLL',0o7402:'HLT',0o7404:'OSR',0o7040:'CMA',0o7001:'IAC',0o7440:'SZA',0o7510:'SPA',0o7450:'SNA'};
    if(known[word])return known[word];
    const group3=Boolean(word&1)&&Boolean(word&0o400);
    return group3?'OPR 3':'OPR '+oct(word);
  }

  function drawListing() {
    const parent=$('programListing');parent.replaceChildren();
    if(!ui.list.length) {
      const empty=document.createElement('div');empty.className='placeholder';empty.textContent='Load the calculator program to inspect its native instructions.';
      parent.append(empty);return;
    }
    const pageSize=10; const pageCount=Math.max(1,Math.ceil(ui.list.length/pageSize));
    ui.tracePage=Math.max(0,Math.min(ui.tracePage,pageCount-1));
    $('tracePageInfo').textContent=`WORDS ${ui.tracePage*pageSize+1}–${Math.min(ui.list.length,(ui.tracePage+1)*pageSize)} / ${ui.list.length}`;
    $('btnTracePrev').disabled=ui.tracePage===0; $('btnTraceNext').disabled=ui.tracePage>=pageCount-1;
    for(const [address,word] of ui.list.slice(ui.tracePage*pageSize,(ui.tracePage+1)*pageSize)){
      const line=document.createElement('div');line.className='code-line';line.dataset.address=String(address);
      const arrow=document.createElement('span');arrow.className='arrow';arrow.textContent=' ';const ad=document.createElement('span');ad.textContent=oct(address);
      const op=document.createElement('span');op.className='opcode';op.textContent=oct(word);
      const mnemonic=document.createElement('span');mnemonic.className='mnemonic';mnemonic.textContent=disasm(word,address);
      line.append(arrow,ad,op,mnemonic);parent.append(line);
    }
    if(ui.state)markActiveLine(ui.state.pc);
  }
  function markActiveLine(pc) {
    if(ui.list.length){const index=ui.list.findIndex(([addr])=>addr===pc);if(index>=0 && Math.floor(index/10)!==ui.tracePage){ui.tracePage=Math.floor(index/10);drawListing();return;}}
    for(const line of $('programListing').querySelectorAll('.code-line')) {
      const active=Number(line.dataset.address)===pc;
      line.classList.toggle('active',active);
      line.children[0].textContent=active?'▸':' ';
    }
  }

  function appendTty(text) {
    // CRLF handling for DEC TTY display; keep finite text for long-running demos.
    ui.ttyText += text.replace(/\r\n/g,'\n').replace(/\r/g,'\n');
    if(ui.ttyText.length>12000)ui.ttyText=ui.ttyText.slice(-12000);
    $('ttyScreen').textContent=ui.ttyText;
    $('ttyScreen').scrollTop=$('ttyScreen').scrollHeight;
  }

  function showTab(name) {
    for(const tab of document.querySelectorAll('.tab')) {
      const selected=tab.dataset.tab===name;
      tab.classList.toggle('active',selected);tab.setAttribute('aria-selected',String(selected));
    }
    for(const panel of document.querySelectorAll('.tab-body')) panel.classList.toggle('hidden',panel.dataset.panel!==name);
  }

  async function loadCalculator() {
    if(ui.busy)return;
    try {
      const a=parseOperand($('calcA').value), b=parseOperand($('calcB').value);
      const operation=$('calcOperation').value;
      if(operation==='multiply'&&b>256)throw new Error('For this teaching demonstration, B must be at most 256 for multiplication.');
      ui.stopped=true;
      const res=await command('calculator',{operation,a,b});
      if(!res)return;
      ui.loaded=true;ui.list=res.data.listing;ui.activeAddr=null;ui.stopped=false;ui.tracePage=0;
      drawListing();renderState();
      toast(`${operation.toUpperCase()} loaded as native PDP-8 code at 0200.`);
      $('panelMessage').textContent=`Calculator ready: ${operation}; step or run to HLT.`;
    } catch(error){toast(error.message,true);}
  }

  async function step() {
    ui.stopped=true;
    const response=await command('step',{count:1});
    if(response&&response.data.trace&&response.data.trace.length){
      const [f,pc,ir]=response.data.trace[0];
      ui.recentAddr=pc;
      $('panelMessage').textContent=`Executed ${f}:${oct(pc)}  ${oct(ir)}  ${disasm(ir,pc)}`;
    }
  }

  async function start() {
    if(ui.busy)return;
    ui.stopped=false;
    const result=await command('start',{});
    if(result&&result.state.running) tickLoop();
  }
  async function tickLoop() {
    if(ui.polling)return;
    ui.polling=true;
    try {
      while(!ui.stopped&&ui.state&&ui.state.running&&!ui.state.halted){
        if(!ui.busy){
          const result=await command('tick',{count:384});
          if(!result)break;
        }
        await new Promise(resolve=>setTimeout(resolve,65));
      }
    }finally{ui.polling=false;}
  }
  async function historicalStart(fresh) {
    if(ui.panelLocked)return toast('Panel locked; unlock before operating.',true);
    if(ui.busy)return;
    ui.stopped=true;
    const response=await command(fresh?'panel_start':'panel_continue',{'single_instruction':ui.singleInstruction});
    if(!response)return;
    if(fresh)lessonPanelAction('start');
    if(response.state.running){ui.stopped=false;tickLoop();}
    else if(ui.singleInstruction)toast(`${fresh?'START':'CONT'}: executed one native instruction, PC ${oct(response.state.pc)}.`);
  }
  async function halt() {
    ui.stopped=true;
    // If a tick is currently in flight, wait for it to complete before STOP.
    for(let i=0;i<40&&ui.busy;i++)await new Promise(resolve=>setTimeout(resolve,15));
    await command('halt');
  }

  async function examinePanel() {
    const s=ui.state;if(!s)return;
    const at=s.panel_next_addr;
    const result=await command('examine',{address:at,field:s.panel_field,count:1,panel:true});
    if(result)toast(`${s.panel_field}:${oct(at)} = ${oct(result.data.words[0])}; next ${oct((at+1)&mask)}`);
  }
  async function depositPanel() {
    const s=ui.state;if(!s)return;
    const at=s.panel_next_addr;
    const result=await command('deposit',{address:at,field:s.panel_field,value:s.switches,panel:true});
    if(result){toast(`Deposited ${oct(s.switches)} at ${s.panel_field}:${oct(at)}; next ${oct((at+1)&mask)}`);lessonPanelAction('deposit',at,s.switches);}
  }
  async function reset(clear=false) {
    if(clear&&!confirm('Erase all emulated memory and reset the CPU?'))return;
    ui.stopped=true;ui.loaded=false;ui.list=[];drawListing();
    const res=await command('reset',{clear});
    if(res)toast(clear?'Memory cleared and CPU reset.':'CPU reset (memory retained).');
  }

  async function inspectMemory() {
    try {
      const address=parseOct('memoryAddr'),field=parseOct('memoryField',7);
      if(ui.state&&field>=ui.state.fields)throw new Error(`Only ${ui.state.fields} field(s) installed.`);
      const res=await command('examine',{address,field,count:32});
      if(!res)return;
      const lines=[];
      for(let i=0;i<res.data.words.length;i+=8){
        lines.push(`${field}:${oct((address+i)&mask)}  ${res.data.words.slice(i,i+8).map(n=>oct(n)).join('  ')}`);
      }
      $('memoryDump').textContent=lines.join('\n');
    }catch(error){toast(error.message,true);}
  }

  async function loadWords() {
    try {
      const origin=parseOct('loadOrigin'),field=parseOct('loadField',7);
      const raw=$('loadWords').value.trim().split(/[\s,]+/).filter(Boolean);
      if(raw.length<1||raw.length>64)throw new Error('Load 1–64 octal words at a time.');
      const words=raw.map(w=>{
        if(!/^[0-7]{1,4}$/.test(w)||parseInt(w,8)>mask)throw new Error(`Invalid PDP-8 word: ${w}`);
        return parseInt(w,8);
      });
      ui.stopped=true;
      const res=await command('load_words',{origin,field,words});
      if(res){ui.loaded=false;ui.list=[];drawListing();toast(`Loaded ${words.length} native 12-bit words at ${field}:${oct(origin)}.`);}
    }catch(error){toast(error.message,true);}
  }

  async function runDemo(name){
    ui.stopped=true;
    const response=await command('demo',{name});
    if(response){ui.loaded=false;ui.list=[];drawListing();toast(response.data.description);}
  }

  async function tapeAction(op,args={}) {
    ui.stopped=true;
    const r=await command(op,args);
    if(r)toast(`${op.replaceAll('_',' ')} completed.`);
    return r;
  }

  async function mountTape() {
    const file=$('tapeFile').files[0];
    if(!file){toast('Select a raw paper tape file.',true);return;}
    if(file.size<1||file.size>32768){toast('Tape must contain 1–32768 bytes.',true);return;}
    if(ui.busy){return;}
    ui.busy=true;ui.stopped=true;
    try {
      const bytes=new Uint8Array(await file.arrayBuffer());
      await api('tape_begin',{size:bytes.length});
      for(let i=0;i<bytes.length;i+=192){
        await api('tape_chunk',{bytes:Array.from(bytes.subarray(i,i+192))});
        $('tapeReadout').textContent=`UPLOADING ${Math.min(i+192,bytes.length)}/${bytes.length} frames`;
      }
      await api('tape_end');
      toast(`Mounted ${file.name}, ${bytes.length} tape frames.`);
    } catch(e) {toast(`Tape upload failed: ${e.message}`,true);}
    finally {ui.busy=false;}
  }

  async function tapeStart() {
    ui.stopped=true;
    const set=await command('switches',{value:0o7756});
    if(!set)return;
    const started=await command('panel_start',{single_instruction:false});
    if(started){ui.stopped=false;toast('RIM is reading raw tape frames. STOP at end of tape.');tickLoop();}
  }

  async function boot() {
    buildPanel();
    for(const tab of document.querySelectorAll('.tab'))tab.addEventListener('click',()=>showTab(tab.dataset.tab));
    updateLesson();
    for(const btn of document.querySelectorAll('[data-program-view]'))btn.addEventListener('click',()=>{
      for(const peer of document.querySelectorAll('[data-program-view]'))peer.classList.toggle('selected',peer===btn);
      for(const view of document.querySelectorAll('.program-view'))view.classList.toggle('hidden',view.dataset.view!==btn.dataset.programView);
    });
    const wire=(id,event,fn)=>$(id).addEventListener(event,fn);
    wire('btnTracePrev','click',()=>{ui.tracePage=Math.max(0,ui.tracePage-1);drawListing();});
    wire('btnTraceNext','click',()=>{ui.tracePage++;drawListing();});
    wire('btnCalcLoad','click',loadCalculator);
    wire('btnCalcStep','click',step);
    wire('btnCalcFinish','click',start);
    wire('btnStep','click',step);
    wire('btnRun','click',()=>historicalStart(true));
    wire('btnContinue','click',()=>historicalStart(false));
    wire('btnSingleInstruction','click',()=>{ui.singleInstruction=!ui.singleInstruction;$('btnSingleInstruction').setAttribute('aria-pressed',String(ui.singleInstruction));toast(ui.singleInstruction?'SING INST ON: START/CONT executes one instruction.':'SING INST OFF: continuous RUN.');});
    wire('panelLock','click',()=>{ui.panelLocked=!ui.panelLocked;$('panelLock').setAttribute('aria-pressed',String(ui.panelLocked));$('panelLock').textContent=ui.panelLocked?'PANEL LOCKED':'PANEL UNLOCKED';});
    wire('btnPanelPreset','click',async()=>{const words=[0,...lessonWords,0,0];const n=words[ui.lessonStep];if(n===undefined)return;const r=await command('switches',{value:n});if(r)toast('Switch register set to '+oct(n)+'. Press the actual panel key to proceed.');});
    wire('btnPanelGuideReset','click',()=>{ui.lessonStep=0;updateLesson();toast('Lesson prompts restarted; emulated memory unchanged.');});
    wire('btnStop','click',halt);
    wire('btnReset','click',()=>reset(false));
    wire('btnClear','click',()=>reset(true));
    wire('btnLoadAddress','click',async()=>{
      if(!ui.state)return;
      const address=ui.state.switches;
      if(ui.panelLocked)return toast('Panel locked; unlock before operating.',true);
      const res=await command('panel_addr',{address,ifield:ui.state.ifield,dfield:ui.state.dfield});
      if(res){toast(`LOAD ADD: address ${oct(address)}.`);lessonPanelAction('load',address);}
    });
    wire('btnExamine','click',()=>{if(!ui.panelLocked)examinePanel();else toast('Panel is locked',true);});
    wire('btnDeposit','click',()=>{if(!ui.panelLocked)depositPanel();else toast('Panel is locked',true);});
    for(const card of document.querySelectorAll('[data-demo]'))card.addEventListener('click',()=>runDemo(card.dataset.demo));
    wire('btnMemoryRead','click',inspectMemory);
    wire('btnLoadWords','click',loadWords);
    wire('btnLabDemo','click',async()=>{const r=await command('lab_demo',{mode:'adc'});if(r)toast('ADC program loaded at 0200. Press RUN LOADED PROGRAM.');});
    wire('btnLabTimerDemo','click',async()=>{const r=await command('lab_demo',{mode:'timer'});if(r)toast('Timer program loaded at 0200. Press RUN LOADED PROGRAM.');});
    wire('btnLabRun','click',async()=>{ui.stopped=false;const r=await command('start',{address:0o200});if(r&&r.state.running)tickLoop();});
    wire('btnLabStatus','click',()=>command('lab_status'));
    wire('btnRimInstall','click',()=>tapeAction('rim_install'));
    wire('btnTapeDemo','click',()=>tapeAction('rim_fixture'));
    wire('btnTapeRewind','click',()=>tapeAction('tape_rewind'));
    wire('btnTapeMount','click',mountTape);
    wire('btnTapeStart','click',tapeStart);
    wire('btnTapeStop','click',stop);
    wire('tapeSpeed','change',async e=>{
      const value=e.target.value;
      const reply=await command('tape_speed',{speed:value});
      if(reply)toast(`Reader timing: ${value==='asr33'?'10 cps':value==='high'?'300 cps':'TURBO'}.`);
    });
    wire('btnTapePlay','click',async()=>{
      const reply=await command('tape_transport',{action:'play'});
      if(reply)toast('Paper tape transport PLAY.');
    });
    wire('btnTapePause','click',async()=>{
      const reply=await command('tape_transport',{action:'pause'});
      if(reply)toast('Paper tape transport PAUSED.');
    });

    wire('btnSetPc','click',async()=>{
      try {const address=parseOct('loadOrigin');const r=await command('pc',{address});if(r)toast(`PC set to ${oct(address)}.`);}
      catch(error){toast(error.message,true);}
    });
    wire('btnTtySend','click',async()=>{
      const str=$('ttyEntry').value;
      if(!str)return;
      const response=await command('keyboard',{text:str+'\r'});
      if(response){$('ttyEntry').value='';toast('Keystrokes queued for PDP-8 TTY input.');}
    });
    wire('ttyEntry','keydown',e=>{if(e.key==='Enter'){$('btnTtySend').click();}});
    wire('btnTtyClear','click',()=>{ui.ttyText='';$('ttyScreen').textContent='';});
    for(const base of ['Decimal','Octal'])wire('base'+base,'click',()=>{
      const next=base==='Decimal'?'dec':'oct';if(next===ui.base)return;
      try {
        const a=parseOperand($('calcA').value),b=parseOperand($('calcB').value);
        ui.base=next;
        $('calcA').value=formatValue(a);$('calcB').value=formatValue(b);
        $('baseDecimal').classList.toggle('active',next==='dec');
        $('baseOctal').classList.toggle('active',next==='oct');
        renderState();
      }catch(error){toast('Correct operand values before switching base: '+error.message,true);}
    });
    const updateTarget = info => {
      $('executionMode').value=info.mode;
      $('serialPort').value=info.port || '';
      $('serialPort').classList.toggle('unused',info.mode!=='serial');
      $('modeBadge').textContent=info.mode==='sim'?'DESKTOP SIMULATION':'LIVE RP2040';
      $('connectionBadge').classList.remove('connecting','error');
      $('connectionBadge').lastChild.textContent=info.mode==='sim'?' Simulator connected':' Pico connected';
    };
    wire('executionMode','change',()=>{
      $('serialPort').classList.toggle('unused',$('executionMode').value!=='serial');
      $('btnConnectTarget').textContent='CONNECT';
    });
    wire('btnConnectTarget','click',async()=>{
      if(ui.busy || ui.polling)return toast('Stop the current program before changing engine.',true);
      const mode=$('executionMode').value;
      const port=$('serialPort').value.trim();
      if(mode==='serial'&&!port)return toast('Enter the Pico USB serial port first.',true);
      ui.busy=true;
      $('btnConnectTarget').disabled=true;
      try {
        const response=await fetch('/api/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode,port})});
        const body=await response.json();
        if(!response.ok||!body.ok)throw new Error(body.error||'Could not connect engine');
        ui.state=null;ui.loaded=false;ui.list=[];ui.tracePage=0;ui.ttyText='';ui.calculating=false;ui.stopped=false;ui.lessonStep=0;updateLesson();
        $('ttyScreen').textContent='';
        $('programListing').textContent='';
        updateTarget(body);
        toast(mode==='sim'?'PC simulator ready.':'Live Pico connected.');
      } catch(error) {
        toast(error.message,true);
        const actual=await (await fetch('/api/info')).json();
        updateTarget(actual);
      } finally {ui.busy=false;$('btnConnectTarget').disabled=false;}
      await command('hello',{},false);
    });
    try {
      const info=await(await fetch('/api/info')).json();
      updateTarget(info);
      const response=await command('hello',{},false);
      if(!response)throw new Error('Emulator did not reply.');
      appendTty('\nATLAS-8 / READY\n');
    }catch(error){
      $('connectionBadge').classList.add('error');
      $('connectionBadge').lastChild.textContent=' Disconnected';
      toast('Cannot reach emulator: '+error.message,true);
    }
  }
  document.addEventListener('DOMContentLoaded',boot);
})();
