(() => {
 const trigger=document.querySelector('.valuation-image-button'),dialog=document.getElementById('chart-dialog');if(!trigger||!dialog)return;
 const image=document.getElementById('zoom-image'),title=document.getElementById('chart-title'),controls=document.getElementById('valuation-zoom-controls'),label=controls.querySelector('output'),frame=dialog.querySelector('.zoom-scroll');let scale=1,active=false;
 function resize(value){scale=Math.max(.5,Math.min(3,value));image.style.width=(scale*100)+'%';label.textContent=Math.round(scale*100)+'%';}
 trigger.addEventListener('click',()=>{active=true;dialog.classList.add('valuation-view');dialog.setAttribute('aria-label','螺丝钉估值原图');controls.hidden=false;title.textContent=trigger.dataset.imageTitle;image.src=trigger.querySelector('img').src;image.alt=trigger.dataset.imageTitle;resize(1);dialog.showModal();frame.scrollTop=frame.scrollLeft=0;});
 controls.addEventListener('click',e=>{const action=e.target.closest('[data-valuation-zoom]')?.dataset.valuationZoom;if(!action)return;if(action==='fit'){resize(1);frame.scrollTop=frame.scrollLeft=0;}else resize(scale*(action==='in'?1.25:.8));});
 dialog.addEventListener('close',()=>{if(!active)return;active=false;dialog.classList.remove('valuation-view');dialog.setAttribute('aria-label','放大图表');controls.hidden=true;image.style.removeProperty('width');trigger.focus();});
})();
