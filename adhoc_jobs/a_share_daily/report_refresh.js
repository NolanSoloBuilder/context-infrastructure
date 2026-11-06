(() => {
 const panel=document.getElementById('report-refresh');if(!panel)return;
 const toggle=panel.querySelector('input'),button=panel.querySelector('button'),status=panel.querySelector('[role=status]');
 const revision=document.querySelector('meta[name=report-revision]')?.content,interval=300000;
 let next=Date.now()+interval,pending=false,last='';
 if(!['http:','https:'].includes(location.protocol)){toggle.disabled=button.disabled=true;status.textContent='离线副本，不自动检查新版';return;}
 function tick(){if(!toggle.checked){status.textContent='自动检查已关闭';return;}if(document.visibilityState!=='visible'){status.textContent='后台暂停检查';return;}if(!pending&&Date.now()>=next){check();return;}if(!pending)status.textContent=`每5分钟检查新版${last?' · 上次 '+last:''} · ${Math.max(0,Math.ceil((next-Date.now())/1000))}秒后检查`;}
 async function check(){if(pending)return;pending=true;button.disabled=true;status.textContent='正在检查最新已发布晨报…';const c=new AbortController(),timeout=setTimeout(()=>c.abort(),10000);
  try{const response=await fetch('/report-meta.json?check='+Date.now(),{cache:'no-store',signal:c.signal});if(!response.ok)throw new Error('HTTP '+response.status);const meta=await response.json();if(typeof meta.content_revision!=='string'||!meta.content_revision)throw new Error('缺少版本标识');
   if(meta.content_revision!==revision){status.textContent='发现已发布更新，正在载入…';window.dispatchEvent(new Event('a-share-before-refresh'));const url=new URL(location.href);url.searchParams.set('v',meta.content_revision.slice(0,12));location.replace(url.href);return;}
   last=new Date().toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit',timeZone:'Asia/Shanghai'});status.textContent='已是最新发布版本 · '+last;
  }catch{last='失败，保留当前页';status.textContent='检查失败，保留当前晨报；稍后重试';}finally{clearTimeout(timeout);pending=false;button.disabled=false;next=Date.now()+interval;}
 }
 toggle.addEventListener('change',()=>{next=Date.now()+interval;tick();});button.addEventListener('click',check);document.addEventListener('visibilitychange',tick);setInterval(tick,15000);tick();
})();
