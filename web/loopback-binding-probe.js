'use strict';
(async function () {
  const destination=new URL('/loopback-binding-report',document.currentScript.src).href;
  const report={origin:location.origin,functions:[],connections:[],appman:null,errors:[]};
  const manager=window.appman;
  const managerPrototype=manager!=null ? Object.getPrototypeOf(manager) : null;
  report.appman={type:typeof manager,own_names:manager!=null ? Object.getOwnPropertyNames(manager).slice(0,60) : [],prototype_names:managerPrototype ? Object.getOwnPropertyNames(managerPrototype).slice(0,60) : [],source:managerPrototype ? Function.prototype.toString.call(managerPrototype.constructor).slice(0,50000) : null,methods:[]};
  if(manager!=null) {
    for(const name of new Set([...report.appman.own_names,...report.appman.prototype_names])) {
      if(name==='constructor')continue;
      const descriptor=Object.getOwnPropertyDescriptor(manager,name)||Object.getOwnPropertyDescriptor(managerPrototype,name);
      if(typeof descriptor?.value==='function')report.appman.methods.push({name,arity:descriptor.value.length,source:Function.prototype.toString.call(descriptor.value).slice(0,8000)});
    }
  }
  // Read function metadata/source only. Never call any inspected function.
  const targets=[
    ['vizio','createSystemRegistryConnection'],['vizio','createAppLaunchConnection'],
    ['vizio','createLokiConnection'],['vizioSystemRegistry','get'],
    ['vizioSystemRegistry','subscribeToKeyChange'],['vizioConnection','send'],
    ['vizio','constructor'],['vizioSystemRegistry','constructor'],['vizioConnection','constructor'],
  ];
  for(const [object,name] of targets) {
    try {
      const fn=navigator[object]?.[name];
      report.functions.push({object,name,type:typeof fn,arity:typeof fn==='function' ? fn.length : null,source:typeof fn==='function' ? Function.prototype.toString.call(fn).slice(0,16000) : null});
    } catch(error) {report.errors.push(object+'.'+name+':'+error.name);}
  }
  // Establish temporary local bridge connections, then inspect their class
  // definitions. Never call get/set/launch/subscribe on the returned clients.
  for(const factory of ['createSystemRegistryConnection','createAppLaunchConnection','createLokiConnection','createVizioTestConnection']) {
    try {
      const connection=await Promise.race([
        navigator.vizio[factory](),
        new Promise((_,reject)=>setTimeout(()=>reject(new Error('Connect timeout')),5000)),
      ]);
      const prototype=Object.getPrototypeOf(connection);
      report.connections.push({factory,prototype_names:Object.getOwnPropertyNames(prototype).slice(0,60),source:Function.prototype.toString.call(prototype.constructor).slice(0,50000)});
    } catch(error) {report.errors.push(factory+':'+error.name);}
  }
  await fetch(destination,{method:'POST',mode:'no-cors',body:JSON.stringify(report)}).catch(()=>{});
  document.body.style.cssText='background:#101216;color:white;font:28px sans-serif;padding:40px';
  document.body.textContent='Read-only binding metadata sent. Input → HDMI-2 returns to the PC.';
}());
