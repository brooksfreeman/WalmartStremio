'use strict';
(async function () {
  const source=new URL(document.currentScript.src);
  const mode=source.searchParams.get('mode')||'install';
  const operation=mode.replace('-rest','');
  const rest=mode.endsWith('-rest');
  const destination=new URL('/loopback-home-report',source).href;
  const report={origin:location.origin,mode,steps:[],html_sha256:null,bridge_available:typeof navigator.vizio?.createAppLaunchConnection==='function',native_launch_at:null,error:null};
  const send=()=>fetch(destination,{method:'POST',mode:'no-cors',body:JSON.stringify(report)});
  document.body.textContent='Preparing the TV-local launcher…';
  try {
    if(!['install','open','test','cleanup','install-rest','open-rest','test-rest','cleanup-rest'].includes(mode))throw new Error('Unsupported mode');
    const fs=await new Promise((resolve,reject)=>webkitRequestFileSystem(PERSISTENT,65536,resolve,reject));
    const directory=await new Promise((resolve,reject)=>fs.root.getDirectory(rest ? 'owner-tv-home-rest-v1' : 'owner-tv-home-v1',{create:operation==='install',exclusive:operation==='install'},resolve,reject));
    if(operation==='cleanup'){
      await new Promise((resolve,reject)=>directory.removeRecursively(resolve,reject));
      report.steps.push('own-launcher-directory-removed');await send();
      document.body.textContent='Own launcher directory removed. Input → HDMI-2 returns to the PC.';return;
    }
    const entry=await new Promise((resolve,reject)=>directory.getFile('index.html',{create:operation==='install',exclusive:operation==='install'},resolve,reject));
    if(operation==='install') {
      const response=await fetch(new URL(rest ? '/tv-local-launcher-rest.html' : '/tv-local-launcher.html',source),{signal:AbortSignal.timeout(5000)});
      if(!response.ok)throw new Error('Package unavailable');
      const packageText=await response.text();
      if(packageText.length>65536)throw new Error('Package too large');
      const writer=await new Promise((resolve,reject)=>entry.createWriter(resolve,reject));
      await new Promise((resolve,reject)=>{writer.onwriteend=resolve;writer.onerror=()=>reject(writer.error);writer.write(new Blob([packageText],{type:'text/html'}));});
      const file=await new Promise((resolve,reject)=>entry.file(resolve,reject));
      if(await file.text()!==packageText)throw new Error('Readback mismatch');
      report.steps.push('exclusive-launcher-created','byte-readback-matched');
    }
    const file=await new Promise((resolve,reject)=>entry.file(resolve,reject));
    const html=await file.text();
    report.html_sha256=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(html)))).map(x=>x.toString(16).padStart(2,'0')).join('');
    report.steps.push('rendering-stored-launcher');
    if(operation==='test')report.native_launch_at=Date.now()+15000;
    await send();
    if(operation==='test')window.__ownerNativeLaunchAt=report.native_launch_at;
    document.open();document.write(html);document.close();
  } catch(error){
    report.error=error.name;await send().catch(()=>{});
    document.body.textContent='Local launcher preparation stopped: '+error.name+'. Input → HDMI-2 returns to the PC.';
  }
}());
