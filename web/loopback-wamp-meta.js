'use strict';
(async function () {
  // Standard WAMP registration metadata only. No application methods invoked.
  // Spec: https://wamp-proto.org/wamp_latest_ietf.html section 10.2.
  const destination=new URL('/loopback-wamp-meta-report',document.currentScript.src).href;
  const report={origin:location.origin,realm:'systemregistry',router_roles:[],feature_names:[],registration_count:null,uris:[],error:null,detail_limit:32};
  document.body.textContent='Reading local bridge API names…';
  let socket,ended=false,timer;
  const pending=new Set();
  const finish=async()=>{
    if(ended)return;ended=true;clearTimeout(timer);
    if(socket?.readyState===WebSocket.OPEN){socket.send(JSON.stringify([6,{},'wamp.close.normal']));socket.close();}
    await fetch(destination,{method:'POST',mode:'no-cors',body:JSON.stringify(report)}).catch(()=>{});
    document.body.textContent='Read-only API-name check sent. Input → HDMI-2 returns to the PC.';
  };
  try {
    socket=new WebSocket('ws://127.0.0.1:55555','wamp.2.json');
    timer=setTimeout(()=>{report.error='Timeout';finish();},6000);
    socket.onopen=()=>socket.send(JSON.stringify([1,'systemregistry',{roles:{caller:{}}}]));
    socket.onerror=()=>{report.error='WebSocketError';finish();};
    socket.onmessage=event=>{
      if(ended)return;
      try {
        const message=JSON.parse(event.data);
        if(message[0]===2){
          const roles=message[2]?.roles||{};
          report.router_roles=Object.keys(roles);
          report.feature_names=Object.entries(roles).flatMap(([role,data])=>Object.keys(data.features||{}).map(name=>role+':'+name));
          socket.send(JSON.stringify([48,1,{},'wamp.registration.list']));
        }else if(message[0]===50&&message[1]===1){
          const lists=message[3]?.[0]||{};
          const ids=[...new Set(Object.values(lists).filter(Array.isArray).flat())];
          report.registration_count=ids.length;
          ids.slice(0,32).forEach((id,index)=>{pending.add(index+2);socket.send(JSON.stringify([48,index+2,{},'wamp.registration.get',[id]]));});
          if(!pending.size)finish();
        }else if(message[0]===50&&pending.has(message[1])){
          const uri=message[3]?.[0]?.uri;
          if(typeof uri==='string')report.uris.push(uri.slice(0,300));
          pending.delete(message[1]);if(!pending.size)finish();
        }else if(message[0]===8){report.error=String(message[4]||'WampError').slice(0,150);finish();}
        else if(message[0]===3){report.error='RealmJoinAborted';finish();}
      }catch(_){report.error='InvalidMetadataResponse';finish();}
    };
  }catch(error){report.error=error.name;await finish();}
}());
