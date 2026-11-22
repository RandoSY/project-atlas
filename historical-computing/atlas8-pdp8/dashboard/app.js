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
  };
  const names = [['PC', 'pc'], ['AC', 'ac'], ['MQ', 'mq'], ['IR', 'ir'], ['MA', 'ma'], ['MB', 'mb']];

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
    for (let group=0; group<4; group++) {
      const block=document.createElement('div'); block.className='lamp-group';
      for (let bit=11-group*3;bit>=9-group*3;bit--) {
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
  function buildPanel() {
    names.forEach(([name,field]) => makeLampLine(name,field));
    for (let bit=11;bit>=0;bit--) {
      const button=document.createElement('button');
      button.type='button';button.className='switch-key';button.dataset.bit=String(bit);
      button.setAttribute('aria-label',`Switch bit ${bit}`);button.setAttribute('aria-pressed','false');
      const label=document.createElement('span');label.className='bit-label';label.textContent=String(bit).padStart(2,'0');
      const housing=document.createElement('span');housing.className='toggle-housing';
      const handle=document.createElement('span');handle.className='toggle-handle';
      housing.append(handle);button.append(label,housing);
      button.addEventListener('click',async () => {
        if (!ui.state || ui.busy) return;
        const current=ui.state.switches ^ (1<<bit);
        ui.state.switches=current;
        renderSwitches();
        const response=await command('switches',{value:current});
        if (!response) renderSwitches();
      });
      $('switches').appendChild(button);
    }
  }

  function renderSwitches() {
    if (!ui.state) return;
    const value=ui.state.switches;
    $('switchReadout').textContent='';
    $('switchReadout').append(document.createTextNode(oct(value)+' '));
    const note=document.createElement('small');note.textContent='OCT';$('switchReadout').append(note);
    for (const btn of $('switches').children) btn.setAttribute('aria-pressed',Boolean(value & (1<<Number(btn.dataset.bit))).toString());
  }

  function updateRegister(property,value) {
    const row=$('registers').querySelector(`.register-row[data-field="${property}"]`);
    if (!row) return;
    row.querySelector('.reg-value').textContent=oct(value);
    for (const lamp of row.querySelectorAll('.lamp')) lamp.classList.toggle('on',Boolean(value & (1<<Number(lamp.dataset.bit))));
  }

  function renderState() {
    const s=ui.state;
    if (!s) return;
    for (const [,field] of names) updateRegister(field,s[field]);
    $('statPc').textContent=oct(s.pc);$('statAc').textContent=oct(s.ac);
    $('statLink').textContent=String(s.l);$('statFields').textContent=`${s.ifield} / ${s.dfield}`;
    $('instructionCounter').textContent=`${s.instructions.toLocaleString()} EXECUTED`;
    $('flagKbd').classList.toggle('active',s.tty_kbd_ready);
    $('flagTty').classList.toggle('active',s.tty_print_ready);
    $('flagIon').classList.toggle('active',s.ion);
    $('flagBreak').classList.toggle('active',(s.breakpoints||[]).length>0);
    const running=s.running&&!s.halted;
    $('cpuRunStatus').textContent=running?'RUNNING':(s.reason==='BREAKPOINT'?'BREAKPOINT':'HALTED');
    $('cpuRunStatus').classList.toggle('running',running);
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
      const dict={0o6031:'KSF',0o6032:'KCC',0o6034:'KRS',0o6036:'KRB',0o6041:'TSF',0o6046:'TLS',0o6044:'TPC',0o6001:'ION',0o6002:'IOF'};
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
  async function halt() {
    ui.stopped=true;
    // If a tick is currently in flight, wait for it to complete before STOP.
    for(let i=0;i<40&&ui.busy;i++)await new Promise(resolve=>setTimeout(resolve,15));
    await command('halt');
  }

  async function examinePanel() {
    const s=ui.state;if(!s)return;
    const at=s.ma;
    const result=await command('examine',{address:at,field:s.panel_field,count:1});
    if(result)toast(`${s.panel_field}:${oct(at)} = ${oct(result.data.words[0])}`);
  }
  async function depositPanel() {
    const s=ui.state;if(!s)return;
    const at=s.ma;
    const result=await command('deposit',{address:at,field:s.panel_field,value:s.switches});
    if(result)toast(`Deposited ${oct(s.switches)} at ${s.panel_field}:${oct(at)}.`);
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

  async function boot() {
    buildPanel();
    for(const tab of document.querySelectorAll('.tab'))tab.addEventListener('click',()=>showTab(tab.dataset.tab));
    for(const btn of document.querySelectorAll('[data-panel-section]'))btn.addEventListener('click',()=>{
      $('panelTab').dataset.section=btn.dataset.panelSection;
      for(const peer of document.querySelectorAll('[data-panel-section]'))peer.classList.toggle('selected',peer===btn);
    });
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
    wire('btnRun','click',start);
    wire('btnStop','click',halt);
    wire('btnReset','click',()=>reset(false));
    wire('btnClear','click',()=>reset(true));
    wire('btnLoadAddress','click',async()=>{
      if(!ui.state)return;
      const address=ui.state.switches;
      const res=await command('panel_addr',{address,field:ui.state.panel_field});
      if(res)toast(`PC loaded from switches: ${oct(address)}.`);
    });
    wire('btnExamine','click',examinePanel);
    wire('btnDeposit','click',depositPanel);
    for(const card of document.querySelectorAll('[data-demo]'))card.addEventListener('click',()=>runDemo(card.dataset.demo));
    wire('btnMemoryRead','click',inspectMemory);
    wire('btnLoadWords','click',loadWords);
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
        ui.state=null;ui.loaded=false;ui.list=[];ui.tracePage=0;ui.ttyText='';ui.calculating=false;ui.stopped=false;
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
