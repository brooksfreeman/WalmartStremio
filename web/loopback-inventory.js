'use strict';
(async function () {
  const destination = new URL('/loopback-origin-report', document.currentScript.src).href;
  const report = {
    origin:location.origin, secure_context:isSecureContext,
    connection_type:'undefined', own_names:[], prototype_names:[],
    cache_storage:'caches' in window, service_worker:'serviceWorker' in navigator,
    indexed_db:'indexedDB' in window, registrations:[],
    cache_count:null, idb_count:null, errors:[],
    file_system_request:typeof (window.requestFileSystem || window.webkitRequestFileSystem),
    storage_persisted:null, storage_estimate:null, debuggers:[],
  };
  document.body.style.cssText='background:#101216;color:white;font:28px sans-serif;padding:40px';
  document.body.textContent='Read-only loopback-origin check…';
  // Inspect names only. Never invoke the native binding or load the SDK.
  try {
    const bridge=navigator.vizioConnection;
    report.connection_type=typeof bridge;
    if (bridge != null) {
      report.own_names=Object.getOwnPropertyNames(bridge).slice(0,40);
      const prototype=Object.getPrototypeOf(bridge);
      report.prototype_names=prototype ? Object.getOwnPropertyNames(prototype).slice(0,40) : [];
    }
  } catch (error) {report.errors.push('binding:'+error.name);}
  try {
    if (report.service_worker) {
      const entries=await navigator.serviceWorker.getRegistrations();
      report.registrations=entries.slice(0,10).map(x=>({scope:x.scope,script:(x.active||x.waiting||x.installing)?.scriptURL||null}));
    }
  } catch (error) {report.errors.push('workers:'+error.name);}
  try {if (report.cache_storage) report.cache_count=(await caches.keys()).length;}
  catch (error) {report.errors.push('caches:'+error.name);}
  try {if (indexedDB.databases) report.idb_count=(await indexedDB.databases()).length;}
  catch (error) {report.errors.push('idb:'+error.name);}
  try {
    report.storage_persisted=await navigator.storage.persisted();
    const estimate=await navigator.storage.estimate();
    report.storage_estimate={usage:estimate.usage,quota:estimate.quota};
  } catch (error) {report.errors.push('storage:'+error.name);}
  // The externally refused debugger ports may have different loopback binding.
  // Fetch metadata only; do not connect a debugger or execute CDP commands.
  for (const port of [9555,9222]) {
    const result={port};
    try {
      const response=await fetch('http://127.0.0.1:'+port+'/json/version',{signal:AbortSignal.timeout(2000)});
      result.status=response.status;
      const data=await response.json();
      result.browser=typeof data.Browser==='string' ? data.Browser : null;
      result.has_websocket_url=typeof data.webSocketDebuggerUrl==='string';
    } catch (error) {result.error=error.name;}
    report.debuggers.push(result);
  }
  try {
    await fetch(destination,{method:'POST',mode:'no-cors',body:JSON.stringify(report)});
    document.body.textContent='Read-only check sent. Use Input → HDMI-2 to return.';
  } catch (error) {
    document.body.textContent='Report could not be sent: '+error.name+'. Use Input → HDMI-2 to return.';
  }
}());
