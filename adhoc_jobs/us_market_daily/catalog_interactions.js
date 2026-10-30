const search=document.getElementById('search');
const buttons=[...document.querySelectorAll('.type-tabs button')];
const hoverPanel=document.getElementById('asset-hover-panel');
const detailDialog=document.getElementById('asset-dialog');
const dialogBody=document.getElementById('dialog-body');
let activeKind='all',hoverTimer,closeTimer,hoverCard=null,returnFocus=null,activeSymbol=null;
const boundCards=new WeakSet();
const canHover=window.matchMedia('(hover:hover) and (pointer:fine)');
const runtime=JSON.parse(document.getElementById('catalog-runtime').textContent);
function applyFilters(){
  const groups=[...document.querySelectorAll('.asset-group')];let total=0;
  const term=search.value.trim().toLowerCase();
  groups.forEach(group=>{let shown=0;group.querySelectorAll('.asset-summary-card').forEach(card=>{const visible=(activeKind==='all'||activeKind===group.dataset.kind)&&card.dataset.search.includes(term);card.hidden=!visible;if(visible)shown++;});group.hidden=shown===0;total+=shown;});
  const stocks=document.getElementById('stocks');if(stocks)stocks.hidden=groups.filter(g=>g.dataset.kind==='stock').every(g=>g.hidden);
  document.getElementById('result-count').textContent=total+'项观察';document.getElementById('empty-state').hidden=total!==0;hideHover();
}
function hideHover(){clearTimeout(hoverTimer);clearTimeout(closeTimer);hoverPanel.hidden=true;hoverCard=null;}
function detailMarkup(card){return card.querySelector('.asset-detail-template').innerHTML;}
function expandFirst(container){const first=container.querySelector('.asset-detail');if(first)first.open=true;}
function setDialogContent(card){activeSymbol=card.dataset.symbol;document.getElementById('dialog-label').textContent=activeSymbol+' · 完整数据';dialogBody.innerHTML=detailMarkup(card);expandFirst(dialogBody);}
function openDialog(card){returnFocus=card;hideHover();setDialogContent(card);if(!detailDialog.open)detailDialog.showModal();document.getElementById('close-detail').focus();}
function showHover(card){
  if(!canHover.matches||detailDialog.open||card.hidden)return;
  hoverCard=card;hoverPanel.innerHTML='<div class="detail-toolbar"><span></span><button type="button" data-pin>固定查看</button><button type="button" data-close-hover aria-label="关闭预览">关闭</button></div><div class="detail-body"></div>';
  hoverPanel.querySelector('.detail-toolbar span').textContent=card.dataset.symbol+' · 数据预览';const body=hoverPanel.querySelector('.detail-body');body.innerHTML=detailMarkup(card);expandFirst(body);
  hoverPanel.querySelector('[data-pin]').addEventListener('click',()=>openDialog(card));hoverPanel.querySelector('[data-close-hover]').addEventListener('click',hideHover);
  hoverPanel.hidden=false;const r=card.getBoundingClientRect(),w=hoverPanel.offsetWidth,h=hoverPanel.offsetHeight;
  let left=r.right+10;if(left+w>window.innerWidth-12)left=r.left-w-10;if(left<12)left=Math.max(12,(window.innerWidth-w)/2);
  hoverPanel.style.left=left+'px';hoverPanel.style.top=Math.max(12,Math.min(r.top,window.innerHeight-h-12))+'px';
}
function bindCards(){document.querySelectorAll('.asset-summary-card').forEach(card=>{
  if(boundCards.has(card))return;boundCards.add(card);
  card.addEventListener('pointerenter',()=>{if(!canHover.matches)return;clearTimeout(closeTimer);clearTimeout(hoverTimer);hoverTimer=setTimeout(()=>showHover(card),220);});
  card.addEventListener('pointerleave',()=>{clearTimeout(hoverTimer);closeTimer=setTimeout(hideHover,230);});
  card.addEventListener('click',()=>openDialog(card));
  card.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();openDialog(card);}});
});}
hoverPanel.addEventListener('pointerenter',()=>clearTimeout(closeTimer));hoverPanel.addEventListener('pointerleave',()=>{closeTimer=setTimeout(hideHover,230);});
document.getElementById('close-detail').addEventListener('click',()=>detailDialog.close());
detailDialog.addEventListener('close',()=>{if(returnFocus?.isConnected)returnFocus.focus();activeSymbol=null;});
detailDialog.addEventListener('click',event=>{if(event.target===detailDialog){const r=detailDialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)detailDialog.close();}});
document.addEventListener('keydown',event=>{if(event.key==='Escape')hideHover();});window.addEventListener('resize',hideHover);window.addEventListener('scroll',()=>{if(!hoverPanel.contains(document.activeElement))hideHover();},{passive:true});
search.addEventListener('input',applyFilters);
buttons.forEach(button=>button.addEventListener('click',()=>{activeKind=button.dataset.kind;buttons.forEach(b=>{const selected=b===button;b.classList.toggle('active',selected);b.setAttribute('aria-pressed',String(selected));});applyFilters();}));
document.querySelectorAll('.navigation a').forEach(anchor=>anchor.addEventListener('click',()=>{const target=anchor.getAttribute('href');if(target==='#etfs'||target==='#stocks'){search.value='';buttons.find(b=>b.dataset.kind===(target==='#etfs'?'fund':'stock')).click();}}));
document.getElementById('print-report').addEventListener('click',()=>window.print());bindCards();
const refreshButton=document.getElementById('refresh-data'),statusLine=document.getElementById('refresh-status');let refreshBusy=false;
let autoLastAttempt=0,autoLastSuccess=Date.parse(runtime.status?.last_success_at_utc||'')||0;
function beijing(stamp){if(!stamp)return '';const date=new Date(stamp);return Number.isNaN(date.getTime())?'':date.toLocaleString('zh-CN',{timeZone:'Asia/Shanghai',hour12:false});}
function showStatus(status){
  const state=status.status||status.state||'idle';statusLine.dataset.state=state;
  const success=Date.parse(status.last_success_at_utc||'');if(Number.isFinite(success))autoLastSuccess=Math.max(autoLastSuccess,success);
  const progress=Number.isFinite(status.completed)&&Number.isFinite(status.total)?' '+status.completed+'/'+status.total:'';
  const time=beijing(status.last_success_at_utc||status.finished_at_utc||status.completed_at);
  if(state==='running')statusLine.textContent='正在更新行情与指标'+progress+'，可以继续浏览。';
  else if(state==='failed')statusLine.textContent='本次刷新失败，已保留上次有效数据。'+(status.message||'');
  else if(state==='partial')statusLine.textContent='部分行情更新失败，失败标的保留原日期。'+(time?' 最近完成：'+time+'（北京时间）':'');
  else statusLine.textContent=(time?'行情最近更新：'+time+'（北京时间）。':'已载入缓存行情。')+' 持仓披露与财报研究按各自日期保留。';
}
async function api(url,options={}){const response=await fetch(url,{cache:'no-store',...options});if(response.status===401)throw Error('登录状态已失效，请重新登录站点。');const data=await response.json();return {response,data};}
async function applyLatestView(){
  const stateResult=await api('/api/state');if(!stateResult.response.ok)throw Error('无法读取最新数据');
  const response=await fetch('/',{cache:'no-store'});if(!response.ok)throw Error('无法读取更新后的页面');
  const incoming=new DOMParser().parseFromString(await response.text(),'text/html');const content=incoming.getElementById('catalog-assets');if(!content)throw Error('更新内容不完整');
  const scroll=window.scrollY,pinned=detailDialog.open?activeSymbol:null;hideHover();
  document.getElementById('catalog-assets').replaceChildren(...[...content.childNodes].map(n=>document.importNode(n,true)));
  for(const id of ['catalog-data-times','catalog-export']){const fresh=incoming.getElementById(id),old=document.getElementById(id);if(fresh&&old)old.replaceWith(document.importNode(fresh,true));}
  runtime.version=stateResult.data.version;bindCards();applyFilters();
  if(pinned){const card=[...document.querySelectorAll('.asset-summary-card')].find(c=>c.dataset.symbol===pinned);if(card){setDialogContent(card);returnFocus=card;}}
  window.scrollTo({top:scroll,behavior:'instant'});document.getElementById('catalog-assets').classList.add('refresh-updated');setTimeout(()=>document.getElementById('catalog-assets').classList.remove('refresh-updated'),900);
}
async function monitorRefresh(){
  for(let count=0;count<600;count++){
    const {response,data}=await api('/api/status');if(!response.ok)throw Error('无法读取刷新进度');showStatus(data);
    if(!['running','queued'].includes(data.status||data.state)){if(['complete','partial'].includes(data.status||data.state))await applyLatestView();return;}
    await new Promise(resolve=>setTimeout(resolve,1500));
  }
  throw Error('刷新仍在后台运行，请稍后再次查看进度。');
}
async function refreshData(){
  if(refreshBusy)return;autoLastAttempt=Date.now();refreshBusy=true;refreshButton.disabled=true;refreshButton.textContent='更新中…';
  try{
    const {response,data}=await api('/api/refresh',{method:'POST',headers:{'X-Catalog-Refresh':'1'}});
    if(response.status===429){statusLine.dataset.state='idle';statusLine.textContent='距离上次刷新不足一分钟，'+Math.ceil(data.retry_after_seconds||60)+'秒后可重试。';return;}
    if(!response.ok&&response.status!==409)throw Error(data.message||data.error||'刷新请求失败');
    await monitorRefresh();
  }catch(error){statusLine.dataset.state='failed';statusLine.textContent='刷新未完成，当前数据已保留。'+error.message;}
  finally{refreshBusy=false;refreshButton.disabled=false;refreshButton.textContent='刷新行情';}
}
if(runtime.live&&refreshButton){refreshButton.addEventListener('click',refreshData);showStatus(runtime.status||{});api('/api/status').then(({response,data})=>{if(!response.ok)return;showStatus(data);if((data.status||data.state)==='running'){refreshBusy=true;refreshButton.disabled=true;refreshButton.textContent='更新中…';monitorRefresh().catch(error=>{statusLine.textContent=error.message;}).finally(()=>{refreshBusy=false;refreshButton.disabled=false;refreshButton.textContent='刷新行情';});}}).catch(()=>{statusLine.textContent='数据服务暂不可用，当前缓存仍可阅读。';});}

// Refresh only while this page is visible. No closed-page scheduler or trading.
const autoToggle=document.getElementById('auto-refresh'),autoInterval=document.getElementById('auto-refresh-interval'),autoCountdown=document.getElementById('auto-refresh-countdown');
if(runtime.live&&autoToggle&&autoInterval&&autoCountdown){
  const preferenceKey='market-watch-auto-v1';
  try{const saved=JSON.parse(localStorage.getItem(preferenceKey)||'null');if(saved){autoToggle.checked=saved.enabled!==false;if(['60','300','900'].includes(String(saved.seconds)))autoInterval.value=String(saved.seconds);}}catch{}
  function saveAutoPreference(){try{localStorage.setItem(preferenceKey,JSON.stringify({enabled:autoToggle.checked,seconds:Number(autoInterval.value)}));}catch{}autoTick();}
  function autoTick(){
    if(!autoToggle.checked){autoCountdown.textContent='自动刷新已关闭';return;}
    if(document.hidden){autoCountdown.textContent='后台暂停';return;}
    if(refreshBusy){autoCountdown.textContent='正在更新';return;}
    const seconds=Number(autoInterval.value),due=Math.max(autoLastAttempt,autoLastSuccess)+seconds*1000,left=Math.ceil((due-Date.now())/1000);
    if(left<=0){autoCountdown.textContent='正在自动刷新';void refreshData();return;}
    autoCountdown.textContent=String(Math.floor(left/60)).padStart(2,'0')+':'+String(left%60).padStart(2,'0')+' 后更新';
  }
  autoToggle.addEventListener('change',saveAutoPreference);autoInterval.addEventListener('change',saveAutoPreference);document.addEventListener('visibilitychange',autoTick);
  setTimeout(autoTick,2500);setInterval(autoTick,1000);
}
