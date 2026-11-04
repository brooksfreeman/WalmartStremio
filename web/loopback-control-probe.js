'use strict';
(async function () {
  const destination=new URL('/loopback-control-report',document.currentScript.src).href;
  const report={origin:location.origin,bootstrap_status:null,token_available:false,capabilities_status:null,capability_keys:[],bindings:{},error:null};
  document.body.style.cssText='background:#101216;color:white;font:28px sans-serif;padding:40px';
  document.body.textContent='Reading local control-service capabilities…';
  for(const name of ['vizio','vizioSystemRegistry']) {
    const value=navigator[name];
    const prototype=value!=null ? Object.getPrototypeOf(value) : null;
    report.bindings[name]={type:typeof value,own_names:value!=null ? Object.getOwnPropertyNames(value).slice(0,40) : [],prototype_names:prototype ? Object.getOwnPropertyNames(prototype).slice(0,40) : []};
  }
  try {
    // The SDK's existing local bootstrap. Credential stays inside this closure;
    // never send it to the PC, put it in a URL, store it, or execute the SDK.
    const bootstrap=await fetch('http://127.0.0.1:7346/app/get_auth_token',{signal:AbortSignal.timeout(5000)});
    report.bootstrap_status=bootstrap.status;
    const data=await bootstrap.json();
    const token=data?.ITEM?.VALUE;
    report.token_available=typeof token==='string' && token.length>0;
    if(!report.token_available)throw new Error('No local credential returned');
    const response=await fetch('http://127.0.0.1:7346/system/capabilities',{headers:{AUTH:token},signal:AbortSignal.timeout(5000)});
    report.capabilities_status=response.status;
    const capabilities=await response.json();
    report.capability_keys=Object.keys(capabilities).slice(0,30);
    if(capabilities?.STATUS?.RESULT && capabilities.STATUS.RESULT!=='SUCCESS')throw new Error('Capability read failed');
    document.body.textContent='Local capability read completed. Input → HDMI-2 returns to the PC.';
  } catch(error) {
    // Error names only: vendor responses and URLs can contain credentials.
    report.error=error.name;
    document.body.textContent='Local control read stopped: '+error.name+'. Input → HDMI-2 returns to the PC.';
  }
  await fetch(destination,{method:'POST',mode:'no-cors',body:JSON.stringify(report)}).catch(()=>{});
}());
