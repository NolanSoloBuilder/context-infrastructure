const search=document.getElementById('search');
const groups=[...document.querySelectorAll('.asset-group')];
const buttons=[...document.querySelectorAll('.type-tabs button')];
let activeKind='all';
function applyFilters(){
  const term=search.value.trim().toLowerCase();let total=0;
  groups.forEach(group=>{let shown=0;group.querySelectorAll('.asset-card').forEach(card=>{const visible=(activeKind==='all'||activeKind===group.dataset.kind)&&card.dataset.search.includes(term);card.hidden=!visible;if(visible)shown++;});group.hidden=shown===0;total+=shown;});
  const stockSection=document.getElementById('stocks');
  if(stockSection)stockSection.hidden=groups.filter(g=>g.dataset.kind==='stock').every(g=>g.hidden);
  document.getElementById('result-count').textContent=total+'项观察';
  document.getElementById('empty-state').hidden=total!==0;
}
search.addEventListener('input',applyFilters);
buttons.forEach(button=>button.addEventListener('click',()=>{activeKind=button.dataset.kind;buttons.forEach(b=>{const selected=b===button;b.classList.toggle('active',selected);b.setAttribute('aria-pressed',String(selected));});applyFilters();}));
document.querySelectorAll('.navigation a').forEach(anchor=>anchor.addEventListener('click',()=>{
  const target=anchor.getAttribute('href');
  if(target==='#etfs'||target==='#stocks'){
    search.value='';
    buttons.find(b=>b.dataset.kind===(target==='#etfs'?'fund':'stock')).click();
  }
}));
document.getElementById('print-report').addEventListener('click',()=>window.print());
