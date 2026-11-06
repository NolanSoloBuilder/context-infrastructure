import test from 'node:test';
import assert from 'node:assert/strict';
import {trendRange,trendCard} from './trend_view.mjs';
const asset={name:'测试指数',unit:'点',basis:'价格指数',asof:'2026-10-30',source:'https://example.com',points:[{date:'2023-10-27',close:100},{date:'2024-10-30',close:120},{date:'2025-10-29',close:110},{date:'2025-10-30',close:100},{date:'2026-10-29',close:80},{date:'2026-10-30',close:90}]};
test('calendar range uses cutoff or preceding trading close',()=>{const r=trendRange(asset,'1y');assert.equal(r.start,'2025-10-30');assert.ok(Math.abs(r.return_pct+10)<1e-10);assert.ok(Math.abs(r.mdd_pct+20)<1e-10);assert.equal(r.high.close,100);assert.equal(r.low.close,80);assert.equal(r.points.length,3);});
test('missing history reports partial range honestly',()=>{const short={...asset,points:asset.points.slice(-3)};assert.equal(trendRange(short,'3y').complete,false);assert.match(trendCard('sh000688',short,'3y'),/不足所选年限/);});
test('price changes and volatility are not total return or annualized return',()=>{const r=trendRange(asset,'1y');const returns=[-.2,.125],mean=-.0375;const expected=Math.sqrt(returns.reduce((a,v)=>a+(v-mean)**2,0))*Math.sqrt(252)*100;assert.ok(Math.abs(r.volatility_pct-expected)<1e-10);assert.match(trendCard('sh000688',asset),/价格变化/);});
test('disabling overlays removes only moving-average paths',()=>{const html=trendCard('sh000688',asset,'1y',{ma20:false,ma60:false,extrema:false});assert.match(html,/data-series="close"/);assert.doesNotMatch(html,/data-series="ma60"|data-series="ma20"/);});
test('markup escapes source names and constrains SVG dimensions',()=>{const html=trendCard('x',{...asset,name:'<script>bad</script>'});assert.doesNotMatch(html,/<script>bad/);assert.match(html,/viewBox="0 0 640 238"/);});
