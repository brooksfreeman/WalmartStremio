'use strict';
(async function () {
  const status = document.getElementById('status');
  const localParams = new URLSearchParams(location.search);
  if (localParams.get('loopbackRedirect') === '1' || localParams.has('loopbackFile') || localParams.has('loopbackStored') || localParams.has('loopbackControl') || localParams.has('loopbackBindings') || localParams.has('loopbackRegistry') || localParams.has('localHome') || localParams.has('wampMeta') || localParams.has('homePolicy')) {
    // Same read-only probe as probe_loopback_origin.py. Navigate inside the
    // already-running page so the control API receives only an ordinary URL.
    // The installed Conjure redirect loader is the sole vendor script run.
    const scriptUrl = new URL(localParams.has('loopbackFile') ? '/loopback-file-probe.js' : '/loopback-inventory.js', location.href);
    if(localParams.has('loopbackControl')) scriptUrl.pathname='/loopback-control-probe.js';
    if(localParams.has('loopbackBindings')) scriptUrl.pathname='/loopback-binding-probe.js';
    if(localParams.has('wampMeta'))scriptUrl.pathname='/loopback-wamp-meta.js';
    if(localParams.has('homePolicy')) {
      scriptUrl.pathname='/loopback-home-policy.js';
      scriptUrl.searchParams.set('operation',localParams.get('homePolicy'));
      scriptUrl.searchParams.set('nonce',localParams.get('nonce')||'');
    }
    if(localParams.has('localHome')){
      scriptUrl.pathname='/loopback-home-install.js';scriptUrl.searchParams.set('mode',localParams.get('localHome'));
    }
    if(localParams.has('loopbackRegistry')) {
      scriptUrl.pathname='/loopback-registry-probe.js';
      scriptUrl.searchParams.set('root',localParams.get('loopbackRegistry'));
    }
    if (localParams.has('loopbackFile')) scriptUrl.searchParams.set('mode',localParams.get('loopbackFile'));
    const script = scriptUrl.href;
    let code = "void(document.head.appendChild(Object.assign(document.createElement('script'),{src:" + JSON.stringify(script) + "})))";
    if (localParams.has('loopbackStored')) {
      // This entire bootstrap uses TV-local code and our own persistent file.
      // It contains no LAN script URL or HTTP helper dependency.
      code = "void(webkitRequestFileSystem(PERSISTENT,0,function(fs){fs.root.getFile('owner-tv-lab-disposable-v1/local-test.html',{},function(entry){entry.file(function(file){var reader=new FileReader();reader.onload=function(){document.open();document.write(reader.result);document.close()};reader.readAsText(file)})})}))";
    }
    const target = new URL('http://127.0.0.1:12345/scfs/conjure/index.html');
    target.searchParams.set('offlineAppUrl', 'javascript:' + code);
    target.searchParams.set('retryDelay','0');
    status.textContent = localParams.has('loopbackFile') ? 'Opening the disposable local file test…' : 'Opening the local read-only capability check…';
    location.replace(target.href);
    return;
  }
  const homeWorker = new URLSearchParams(location.search).get('homeWorker') === '1';
  const nativeEntries = new URLSearchParams(location.search).get('nativeEntries') === '1';
  const nativeLoader = new URLSearchParams(location.search).get('nativeLoader') === '1';
  if (nativeLoader || nativeEntries || homeWorker || new URLSearchParams(location.search).get('homeScripts') === '1') {
    document.querySelector('h1').textContent = nativeEntries ? 'Reading native launcher bundle files' : 'Reading Home application scripts';
    document.querySelector('main > p').textContent = 'Reading a fixed set of bundle files as text only. No downloaded code runs and no TV settings change.';
    if (nativeEntries) {
      // Inventory native binding names only. Do not call the binding or SDK.
      const inventory = {connection_type:'undefined',own_names:[],prototype_names:[],send_type:'undefined',receive_type:'undefined'};
      try {
        const bridge = navigator.vizioConnection;
        inventory.connection_type = typeof bridge;
        if (bridge != null) {
          inventory.own_names = Object.getOwnPropertyNames(bridge).slice(0,40);
          const prototype = Object.getPrototypeOf(bridge);
          inventory.prototype_names = prototype ? Object.getOwnPropertyNames(prototype).slice(0,40) : [];
          inventory.send_type = typeof bridge.send;
          inventory.receive_type = typeof bridge.receive;
        }
      } catch (error) {inventory.connection_type = 'error:' + error.name;}
      await fetch('/native-bridge-report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(inventory)}).catch(()=>{});
    }
    const targets = nativeLoader ? [['conjure-script','/scfs/conjure/js/scripts.js']] : nativeEntries ? [
      ['conjure-main','/scfs/conjure/main.html'],
      ['conjure-index','/scfs/conjure/index.html'],
      ['conjure-package','/scfs/conjure/package.json'],
      ['scu-package','/scfs/scu/package.json'],
    ] : homeWorker ? [
      ['sctv-worker','/scfs/sctv/service-worker.js'],
      ['sctv-source-map','/scfs/sctv/app.js.map'],
    ] : [
      ['sctv-app','/scfs/sctv/app.js'],
      ['system-ui-main','/scfs/system-ui-app/static/js/main.61012d2e.chunk.js'],
    ];
    for (const [name,path] of targets) {
      const report = {name,path};
      try {
        const response = await fetch('http://127.0.0.1:12345'+path,{signal:AbortSignal.timeout(20000)});
        report.status = response.status;
        const reader = response.body.getReader();
        const chunks = []; let size = 0;
        for (;;) {
          const part = await reader.read();
          if (part.done) break;
          size += part.value.length;
          if (size > 8*1024*1024) {await reader.cancel(); report.oversized = true; break;}
          chunks.push(part.value);
        }
        report.bytes = size;
        if (!report.oversized) {
          const bytes = new Uint8Array(size); let offset = 0;
          for (const chunk of chunks) {bytes.set(chunk,offset); offset += chunk.length;}
          report.text = new TextDecoder().decode(bytes);
        }
      } catch (error) {report.error = error.name;}
      try {
        const saved = await fetch('/home-script-report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(report)});
        if (!saved.ok) throw new Error('Save failed');
      } catch (_) {status.textContent='Could not save '+name+'. Use Input → HDMI-2 to return.'; return;}
    }
    status.textContent='Read-only script check saved. Use Input → HDMI-2 to return to the PC.';
    return;
  }
  const homeLoader = new URLSearchParams(location.search).get('homeLoader') === '1';
  const actualHome = new URLSearchParams(location.search).get('actualHome') === '1';
  if (actualHome || homeLoader || new URLSearchParams(location.search).get('homeSources') === '1') {
    document.querySelector('h1').textContent = homeLoader ? 'Reading the local UI loader' : 'Reading Home UI entry pages';
    document.querySelector('main > p').textContent = 'Saving local UI source as text. No downloaded scripts are executed and no TV settings are changed.';
    const report = {resources:{}};
    const targets = actualHome ? [['sctv','/scfs/sctv/main.html'],['system-ui-index','/scfs/system-ui-app/index.html']] : homeLoader ? [['scu-loader','/scfs/scu/js/dlm.js']] : [
      ['scu','/scfs/scu/main.html'],
      ['system-ui-app','/scfs/system-ui-app/main.html'],
    ];
    for (const [name,path] of targets) {
      try {
        const response = await fetch('http://127.0.0.1:12345'+path,{signal:AbortSignal.timeout(8000)});
        const text = await response.text();
        report.resources[name] = {path,status:response.status,text:text.length <= 1600000 ? text : '',oversized:text.length > 1600000};
      } catch (error) {report.resources[name] = {path,error:error.name};}
    }
    try {
      const response = await fetch('/home-source-report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(report)});
      if (!response.ok) throw new Error('Save failed');
      status.textContent = 'Read-only source check saved. Use Input → HDMI-2 to return to the PC.';
    } catch (_) {status.textContent='Could not save the check. Use Input → HDMI-2 to return to the PC.';}
    return;
  }
  const result = {features:{
    secureContext:window.isSecureContext,
    serviceWorker:'serviceWorker' in navigator,
    cacheStorage:'caches' in window,
    indexedDB:'indexedDB' in window,
    fileSystemPicker:typeof window.showDirectoryPicker,
    nativeVizioObject:typeof window.VIZIO,
    nativeLaunchApp:typeof window.VIZIO?.launchApp,
  }, resources:{}};
  try { result.features.storagePersisted = await navigator.storage?.persisted(); } catch (_) {}
  // Fetch as inert text. Never insert, import, eval, or execute these resources.
  for (const [name,path] of [
    ['manifest','/scfs/manifest.json'],
    ['companion','/scfs/cl/js/vizio-companion-lib.js'],
  ]) {
    try {
      const response = await fetch('http://127.0.0.1:12345'+path,{signal:AbortSignal.timeout(8000)});
      const body = await response.text();
      result.resources[name] = {status:response.status, text:body.length <= 1600000 ? body : '', oversized:body.length > 1600000};
    } catch (error) {result.resources[name] = {error:error.name};}
  }
  try {
    const response=await fetch('/local-runtime-report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(result)});
    if (!response.ok) throw new Error('Report not saved');
    status.textContent='Read-only check saved locally. Use Input → HDMI-2 to return to the PC.';
  } catch (_) {status.textContent='Report could not be saved. Use Input → HDMI-2 to return to the PC.';}
}());
