'use strict';
(async function () {
  // One known, observed native key. No arbitrary key/value interface.
  const KEY='/app/platformorchestrator/appsdatabase/home_provider';
  const ORIGINAL='vizios-home', TARGET='netflix';
  const source=new URL(document.currentScript.src);
  const operation=source.searchParams.get('operation');
  const nonce=source.searchParams.get('nonce');
  const report={nonce,operation,phase:'starting',previous:null,current:null,error:null};
  const send=()=>fetch(new URL('/native-home-policy-report',source),{
    method:'POST',mode:'no-cors',body:JSON.stringify(report),
  });
  document.body.style.cssText='background:#101216;color:white;font:28px sans-serif;padding:40px';
  document.body.textContent='Checking the native Home provider…';
  try {
    if(!['preflight','apply','restore'].includes(operation)||!/^[a-f0-9]{32}$/.test(nonce))throw new Error('Invalid operation');
    const permitUrl=new URL('/native-home-policy-permit',source);
    permitUrl.search=new URLSearchParams({operation,nonce});
    const response=await fetch(permitUrl,{credentials:'omit',cache:'no-store'});
    if(!response.ok)throw new Error('No current local permit');
    const permit=await response.json();
    if(permit.operation!==operation||permit.nonce!==nonce)throw new Error('Permit mismatch');
    const registry=await navigator.vizio.createSystemRegistryConnection();
    report.previous=await registry.get(KEY);
    report.current=report.previous;
    report.phase='before';await send();
    if(operation==='preflight') {
      if(report.previous!==ORIGINAL)throw new Error('Unexpected baseline');
    } else if(operation==='apply') {
      if(report.previous!==ORIGINAL)throw new Error('Baseline changed');
      // Secondary rollback if this document remains alive. Independent PC
      // recovery is mandatory because app switching may destroy this timer.
      setTimeout(async()=>{
        try {
          if(await registry.get(KEY)===TARGET)await registry.set(KEY,ORIGINAL);
        } catch (_) {}
      },45000);
      await registry.set(KEY,TARGET);
      report.current=await registry.get(KEY);
      if(report.current!==TARGET)throw new Error('Apply readback mismatch');
    } else {
      if(![ORIGINAL,TARGET].includes(report.previous))throw new Error('Unexpected value; refusing overwrite');
      if(report.previous===TARGET)await registry.set(KEY,ORIGINAL);
      report.current=await registry.get(KEY);
      if(report.current!==ORIGINAL)throw new Error('Restore readback mismatch');
    }
    report.phase='complete';await send();
    document.body.textContent=operation==='apply'
      ? 'Temporary Home-provider test active. Automatic rollback is armed.'
      : 'Native Home check saved; original provider verified. Input → HDMI-2 returns to the PC.';
  } catch(error) {
    report.phase='error';report.error=error.name+': '+error.message;
    await send().catch(()=>{});
    document.body.textContent='Home-provider check stopped. Recovery instructions are saved on the PC. Input → HDMI-2 returns here.';
  }
}());
