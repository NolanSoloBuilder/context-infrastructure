/** Style explicit author classifications; never infer valuation from numeric values. */
const valuationKinds={'低估':'low','正常':'normal','高估':'high'};
export function valuationBadge(label){return `<span class="valuation-badge valuation-${valuationKinds[label]}">${label}</span>`;}
export function colorValuationCells(html){
 return html.replace(/<td([^>]*)>([\s\S]*?)<\/td>/g,(cell,attributes,content)=>{
  const labelOnly=content.replace(/<[^>]*>/g,'').trim();
  if(valuationKinds[labelOnly])return `<td${attributes} data-valuation-class="${valuationKinds[labelOnly]}">${valuationBadge(labelOnly)}</td>`;
  const metric=/^([\s\S]+?)\s*[·／]\s*(低估|正常|高估)(?:估值)?\s*$/.exec(content);
  if(!metric)return cell;
  return `<td${attributes} data-valuation-class="${valuationKinds[metric[2]]}"><span class="valuation-metric">${metric[1]}</span>${valuationBadge(metric[2])}</td>`;
 });
}
export function valuationLegend(){return `<p class="valuation-legend" aria-label="作者估值分类图例"><span>作者估值分类</span>${['低估','正常','高估'].map(valuationBadge).join('')}</p>`;}

export function valuationControls(){return `<form class="valuation-filters" aria-label="筛选作者估值全表"><label>搜索指数或基金代码<input type="search" aria-label="搜索指数或基金代码" placeholder="名称／基金代码"></label><div role="group" aria-label="估值分类筛选">${[['all','全部'],['focus','重点'],['low','低估'],['normal','正常'],['high','高估']].map(([id,label])=>`<button type="button" data-valuation-filter="${id}" data-label="${label}" aria-pressed="${id==='all'}">${label}</button>`).join('')}</div><span role="status" aria-live="polite"></span></form>`;}
