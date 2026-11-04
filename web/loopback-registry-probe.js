'use strict';
(async function () {
  const source=new URL(document.currentScript.src);
  const destination=new URL('/loopback-registry-report',source).href;
  const mode=source.searchParams.get('root');
  // These children were returned by the owner's successful enumerate('/').
  const keys=mode==='manager' ? ['/app/platformorchestrator/appmanager','/app/platformorchestrator/appsdatabase','/app/loki/config','/app/loki/home','/app/loki/deployer','/loki/home/dev-tools'] : mode==='policy' ? ['/loki/home','/app/home','/app/loki','/app/deployer','/app/platformorchestrator','/systemregistry/defaults'] : mode==='branches' ? ['/home','/app','/apps','/loki','/bootsc','/systemregistry'] : [mode==='slash' ? '/' : ''];
  const reads=mode==='osu-log-status' ? [
    ['get','/app/osu/ui-logging/enabled'],
  ] : mode==='osu-dlm' ? [
    ['get','/app/osu/dlm/updates'],
  ] : mode==='osu-storage' ? [
    ['get','/app/osu/activeFolder'],
    ['enumerate','/app/osu/manifest'],
    ['enumerate','/app/osu/dlm'],
  ] : mode==='osu-identity' ? [
    ['enumerate','/app/osu'],
    ['get','/app/osu/manifestHash'],
    ['get','/app/osu/manifestVersion'],
  ] : mode==='home-catalog' ? [
    ['get','/app/loki/home/apps/all'],
    ['get','/app/loki/home/apps/default'],
    ['get','/loki/home/catalog-services/catalog-url-type'],
  ] : mode==='home-resources' ? [
    ['get','/app/loki/deployer/active'],
    ['enumerate','/app/loki/home/apps'],
    ['enumerate','/loki/home/catalog-services'],
    ['enumerate','/loki/home/live-hero'],
  ] : mode==='manager-state' ? [
    ['get','/debug/platformorchestrator/appmanager/state_machine'],
  ] : mode==='home-routing' ? [
    ['enumerate','/debug/platformorchestrator/appmanager'],
    ['get','/app/routines/list'],
    ['get','/app/systemregistry/sysreg.json'],
  ] : mode==='debug-names' ? [
    ['enumerate','/debug/platformorchestrator'],['enumerate','/debug/conjure'],
    ['enumerate','/app/systemregistry'],['enumerate','/app/scpl'],
    ['enumerate','/app/routines'],
  ] : mode==='loki' ? [
    ['enumerate','/app/loki/home'],['enumerate','/app/loki/deployer'],
    ['enumerate','/loki/home/devtool'],['enumerate','/loki/home/dev-tools'],
    ['enumerate','/loki/debug'],['enumerate','/debug'],
  ] : mode==='status' ? [
    ['get','/app/platformorchestrator/appmanager/apps_status'],
    ['get','/app/deployer/appVersionMap'],
    ['get','/app/loki/bundle_version'],
    ['enumerate','/app/platformorchestrator/cache'],
    ['enumerate','/app/platformorchestrator/multiplexer'],
  ] : mode==='database' ? [
    ['get','/app/platformorchestrator/appsdatabase/apps'],
    ['get','/app/platformorchestrator/appsdatabase/app_symbols'],
    ['get','/app/platformorchestrator/appsdatabase/app_aliases'],
  ] : mode==='providers' ? [
    ['get','/app/platformorchestrator/appsdatabase/home_provider'],
    ['enumerate','/app/platformorchestrator/appsdatabase/apps'],
    ['enumerate','/app/platformorchestrator/appsdatabase/app_symbols'],
    ['enumerate','/app/platformorchestrator/appsdatabase/app_aliases'],
  ] : keys.map(key=>['enumerate',key]);
  document.body.style.cssText='background:#101216;color:white;font:28px sans-serif;padding:40px';
  document.body.textContent='Reading bounded Home metadata…';
  const registry=await navigator.vizio.createSystemRegistryConnection();
  for(const [operation,key] of reads) {
    const report={origin:location.origin,operation,key,result:null,error:null};
    try {
      const value=await Promise.race([
        registry[operation](key),
        new Promise((_,reject)=>setTimeout(()=>reject(new Error('Read timeout')),5000)),
      ]);
      report.result=value===undefined ? null : value;
      if(value===undefined)report.error='UndefinedResult';
      // Preserve raw shape privately, never display values onscreen.
      if(JSON.stringify(report).length>200000){report.result=null;report.error='ResultTooLarge';}
    } catch(error) {report.error=error.name;}
    await fetch(destination,{method:'POST',mode:'no-cors',body:JSON.stringify(report)}).catch(()=>{});
  }
  document.body.textContent='Read-only registry enumeration sent. Input → HDMI-2 returns to the PC.';
}());
