'use strict';
(async function () {
  // Browser-sandbox data only. No native filesystem path, bridge call or setting.
  const source = new URL(document.currentScript.src);
  const destination = new URL('/loopback-file-report',source).href;
  const mode = source.searchParams.get('mode') || 'write';
  const folder = 'owner-tv-lab-disposable-v1';
  const filename = 'local-test.html';
  const report = {phase:mode,origin:location.origin,protocol:location.protocol,steps:[],error:null,url:null};
  const send = async () => {
    await fetch(destination,{method:'POST',mode:'no-cors',body:JSON.stringify(report)});
  };
  document.body.style.cssText='background:#101216;color:white;font:28px sans-serif;padding:40px';
  document.body.textContent='Disposable browser file test…';
  try {
    if (!['write','open','cleanup'].includes(mode)) throw new Error('Unsupported mode');
    const request = window.requestFileSystem || window.webkitRequestFileSystem;
    const fs = await new Promise((resolve,reject)=>request.call(window,window.PERSISTENT,8192,resolve,reject));
    report.steps.push('persistent-filesystem-opened');
    if (mode === 'cleanup') {
      // This exact directory was created exclusively by the write test.
      const directory = await new Promise((resolve,reject)=>fs.root.getDirectory(folder,{create:false},resolve,reject));
      await new Promise((resolve,reject)=>directory.removeRecursively(resolve,reject));
      report.steps.push('own-directory-removed');
      document.body.textContent='Disposable test directory removed. Input → HDMI-2 returns to the PC.';
    } else {
      const directory = await new Promise((resolve,reject)=>fs.root.getDirectory(folder,{create:mode==='write',exclusive:mode==='write'},resolve,reject));
      report.steps.push(mode==='write' ? 'exclusive-directory-created' : 'existing-directory-opened');
      const entry = await new Promise((resolve,reject)=>directory.getFile(filename,{create:mode==='write',exclusive:mode==='write'},resolve,reject));
      if (mode === 'write') {
        const pageScript = `
          const report={phase:'executed',origin:location.origin,protocol:location.protocol,steps:['self-contained-local-page-running'],error:null,url:null};
          fetch(${JSON.stringify(destination)},{method:'POST',mode:'no-cors',body:JSON.stringify(report)}).catch(()=>{});
          const buttons=Array.from(document.querySelectorAll('button'));let index=0;
          document.addEventListener('keydown',event=>{
            if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)){
              event.preventDefault();index=(index+(event.key==='ArrowLeft'||event.key==='ArrowUp'?-1:1)+buttons.length)%buttons.length;buttons[index].focus();
            }else if(event.key==='Enter'){event.preventDefault();buttons[index].click();}
          },true);
          for(const button of buttons)button.onclick=()=>document.getElementById('status').textContent=button.textContent+' selected locally';
          buttons[0].focus();
          setInterval(()=>document.getElementById('clock').textContent=new Date().toLocaleTimeString(),1000);
        `;
        const html = '<!doctype html><html><head><meta charset="utf-8"><title>Disposable local TV page</title>'+
          '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; connect-src '+source.origin+'; base-uri \'none\'; form-action \'none\'">'+
          '<style>body{background:#101216;color:white;font:32px sans-serif;padding:60px}button{font:inherit;padding:30px;margin:20px;background:#303745;color:white;border:4px solid transparent}button:focus{border-color:#a5ed80}#status{color:#a5ed80}</style></head><body>'+
          '<h1>This test page is stored on the TV</h1><p>No external images, styles or scripts are needed to display or control this page.</p><p>This does not replace Home or install Stremio.</p>'+
          '<button>Green</button><button>Orange</button><p id="status">Local page loaded</p><p id="clock"></p><p>Physical Input → HDMI-2 returns to the PC.</p><script>'+pageScript+'</scr'+'ipt></body></html>';
        const writer = await new Promise((resolve,reject)=>entry.createWriter(resolve,reject));
        await new Promise((resolve,reject)=>{
          writer.onwriteend=resolve;writer.onerror=()=>reject(writer.error);
          writer.write(new Blob([html],{type:'text/html'}));
        });
        const file = await new Promise((resolve,reject)=>entry.file(resolve,reject));
        if (await file.text() !== html) throw new Error('Readback mismatch');
        report.steps.push('file-written-and-byte-readback-matched');
      }
      report.url = entry.toURL();
      report.steps.push('attempting-local-page-navigation');
      await send();
      setTimeout(async()=>{
        // If top-frame filesystem navigation is blocked, render only our own
        // stored HTML in this existing local-origin document.
        const file=await new Promise((resolve,reject)=>entry.file(resolve,reject));
        const html=await file.text();
        report.steps.push('top-navigation-did-not-unload','rendering-own-stored-file-in-local-document');
        await send();
        document.open();document.write(html);document.close();
      },2000);
      location.replace(report.url);
      return;
    }
  } catch (error) {
    report.error=error.name+': '+error.message;
    document.body.textContent='File test stopped: '+report.error+'. Input → HDMI-2 returns to the PC.';
  }
  await send().catch(()=>{});
}());
