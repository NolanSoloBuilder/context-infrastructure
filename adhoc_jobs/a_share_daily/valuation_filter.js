(() => {
 const root=document.getElementById('watchlist'),form=root?.querySelector('.valuation-filters');if(!form)return;
 const table=root.querySelector(':scope > .table-scroll table'),rows=[...table.tBodies[0].rows],search=form.querySelector('input'),status=form.querySelector('[role=status]'),empty=root.querySelector('.valuation-empty');
 const focus=['上证指数','上证50','沪深300','中证A500','科创50'];let mode='all';
 const info=rows.map(row=>({row,zone:row.querySelector('[data-valuation-class]')?.dataset.valuationClass,name:row.cells[0].textContent.trim(),text:(row.cells[0].textContent+' '+row.cells[5].textContent).replace(/\s/g,'').toLowerCase()}));
 const matches=(x,m)=>m==='all'||(m==='focus'?focus.some(n=>x.name.startsWith(n)):x.zone===m);
 function apply(){const query=search.value.replace(/\s/g,'').toLowerCase();let shown=0;for(const x of info){x.row.hidden=!(matches(x,mode)&&x.text.includes(query));if(!x.row.hidden)shown++;}for(const b of form.querySelectorAll('[data-valuation-filter]')){b.setAttribute('aria-pressed',String(b.dataset.valuationFilter===mode));const count=info.filter(x=>matches(x,b.dataset.valuationFilter)).length;b.textContent=b.dataset.label+' '+count;}status.textContent=`显示 ${shown} / ${rows.length} 项`;empty.hidden=shown>0;}
 form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('click',e=>{const b=e.target.closest('[data-valuation-filter]');if(b){mode=b.dataset.valuationFilter;apply();}});search.addEventListener('input',apply);
 try{const saved=JSON.parse(sessionStorage.getItem('a-share-valuation-restore')||'null');sessionStorage.removeItem('a-share-valuation-restore');if(saved){mode=['all','focus','low','normal','high'].includes(saved.mode)?saved.mode:'all';search.value=saved.query||'';}}catch{}
 window.addEventListener('a-share-before-refresh',()=>{try{sessionStorage.setItem('a-share-valuation-restore',JSON.stringify({mode,query:search.value}));}catch{}});apply();
})();
