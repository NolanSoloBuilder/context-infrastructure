"""Apply browser wiring for the standalone self-service backend to the shipped chunks."""
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'public' / 'assets'
flag = """document.querySelector('meta[name="qingzhu-local-bazi"]')"""

def edit(name, edits):
    p = root / (name + '.js')
    text = p.read_text()
    for old, new in edits:
        if new in text: continue
        if text.count(old) != 1:
            raise ValueError(f'{name}: expected unique match for {old}')
        text = text.replace(old,new)
    p.write_text(text)

edit('index-GEgtjqXc', [
    ('Lt(async()=>{if(new URLSearchParams(window.location.search).get("debug")==="clear")',
     f'Lt(async()=>{{if({flag})return;if(new URLSearchParams(window.location.search).get("debug")==="clear")'),
    ('yi.use(ff);yi.use(yn);yi.mount("#app")',
     f'yi.use(ff);if({flag})try{{await cf(ff).deviceLogin()}}catch(e){{console.error("本地设备启动失败",e)}}yi.use(yn);yi.mount("#app")'),
    ('{path:"/test/report/:id",name:"TestReport",','{path:"/test/report/:id",name:"TestReport",...('+
     flag+'?{redirect:e=>({path:"/test/score",query:{reportId:e.params.id}})}:{}),'),
])

edit('score-yzmNdTRt', [
    ('x.query.unlocked==="true"&&(k.value=!0)',f'({flag}||x.query.unlocked==="true")&&(k.value=!0)'),
])
edit('naming-history-DL5EAW6h', [
    ('id:Number(e.id),type:"bazi"', 'id:e.id,type:"bazi"'),
])
edit('favorites-DDgL2FcO', [
    ('query:{name_id:a.name_id,surname:a.surname,gender:a.gender||void 0}', 'query:{name_id:a.name_id,surname:a.surname,gender:a.gender||void 0,from:a.from,history_id:a.history_id}'),
])

edit('buy-CuVSR05g', [
    ('if(!(I.value&&!await $()))', f'if(!(!{flag}&&I.value&&!await $()))'),
    ('if(await V(),!I.value)',f'if(await V(),{flag}||!I.value)'),
    ('i(d.value.price||29.9)', 'i(d.value.price??29.9)'),
    ('i(w.value?"立即续费 30 天":"立即开通 30 天会员")',
     f'i({flag}?"进入本地演示结算":w.value?"立即续费 30 天":"立即开通 30 天会员")'),
])
edit('HomeVipCard-C_ELQGlv', [
    ('"一张会员，畅用全站"',f'{flag}?"本地演示会员":"一张会员，畅用全站"'),
])
edit('result-CB9YxfXm', [
    ('score:r.score||90,isFavorite:!1','score:r.score||90,isFavorite:!!r.is_collected'),
    ('score:n.score||90,isFavorite:!1','score:n.score||90,isFavorite:!!n.is_collected'),
])
edit('detail-BGqGZFZv', [
    ('title:"AI 自由组合"', f'title:{flag}?"本地用字组合":"AI 自由组合"'),
    ('一并注入大模型。AI 从精选后的字池中自由挑选两字组合，',
     '\一起作为本地筛字和匹配条件。程序从筛选后的字池和古籍候选中组合用字，'),
])

edit('index-9e3LbACy', [
    ('x.getRandom(i.gender,i.difficulty,1)', 'x.getRandom(i.gender,i.difficulty,1,h.value.join(","))'),
])
edit('foreignerName-BTTGJ6I0', [
    ('getRandom(e,t,n=1){','getRandom(e,t,n=1,tags){'),
    ('params:{gender:e,difficulty:t,count:n}','params:{gender:e,difficulty:t,count:n,meaning_tags:tags||void 0}'),
])
edit('index-GEgtjqXc', [
    ('{path:"/tools/character",name:"ToolCharacter",','{path:"/tools/name-analysis",redirect:"/test/form"},{path:"/tools/character",name:"ToolCharacter",...('+
     flag+'?{redirect:"/tools/naming-characters/filter"}:{}),'),
])

edit('report-select-DsAl7vi8', [
    ('const a={surname:l,name:u,gender:', 'const a={surname:l,name:u,...('+flag+'?{name_id:W}:{}),gender:'),
    ('const s={surname:l,name:u,gender:', 'const s={surname:l,name:u,...('+flag+'?{name_id:W}:{}),gender:'),
    ('a.history_id=parseInt(v)', 'a.history_id='+flag+'?v:parseInt(v)'),
    ('s.history_id=parseInt(v)', 's.history_id='+flag+'?v:parseInt(v)'),
])

edit('favorites-DDgL2FcO',[
    ('await C.post(`/v1/tools/naming-characters/${encodeURIComponent(a.char_info.character)}/collect`,null,{params:{action:"uncollect"}})',
     'await C.post(a.from==="bazi-naming"?"/v1/bazi-naming/character-library/favorite":`/v1/tools/naming-characters/${encodeURIComponent(a.char_info.character)}/collect`,a.from==="bazi-naming"?{character:a.char_info.character,action:"uncollect"}:null,{params:{action:"uncollect"}})')
])
edit('result-Blnse5TN',[
    ('I.value?.surname?(a(),t("span",nt,[e("span",lt,o(I.value.surname),1),I.value.wuxing?',
     '(I.value?.surname||v.value?.surname)?(a(),t("span",nt,[e("span",lt,o(I.value?.surname||v.value?.surname),1),I.value?.wuxing?')
])

edit('buy-CuVSR05g', [
    ('sessionStorage.setItem("vipAlipayOrderNo",p.value),sessionStorage.setItem("vipAlipayRedirect",m.query.redirect||"/mine"),window.location.href=s','document.querySelector(\'meta[name="qingzhu-local-bazi"]\')||(sessionStorage.setItem("vipAlipayOrderNo",p.value),sessionStorage.setItem("vipAlipayRedirect",m.query.redirect||"/mine")),window.location.href=s')
])

edit('detail-BGqGZFZv', [
    ('s.push({title:document.querySelector(\'meta[name="qingzhu-local-bazi"]\')?"本地用字组合":"AI 自由组合",body:`将${os}，连同上述喜用神方向、生肖禁忌、字库评分\\一起作为本地筛字和匹配条件。程序从筛选后的字池和古籍候选中组合用字，重点把握 ——寓意典雅契合家长期望、声调起伏自然、字形错落不雷同；并主动规避网红名、声母重复、谐音歧义等不良搭配。`})','s.push({title:o.ai_model?"GPT-6.2 Sol 推荐":document.querySelector(\'meta[name="qingzhu-local-bazi"]\')?"本地用字组合":"AI 自由组合",body:o.ai_reason?o.ai_reason+" 使用提醒："+(o.ai_tradeoff||""): `根据${os}，结合可核对的字义、五行和诗词出处生成候选。`})')
])
