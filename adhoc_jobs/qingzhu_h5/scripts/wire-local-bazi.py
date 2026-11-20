"""Wire the retained Vite form to the local API on the independent server."""
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "public/assets/form-BEeo8LQI.js"
source = path.read_text()
edits = [
    ('Ve=5,cn=', 'Ve=5,localBazi=()=>!!document.querySelector(\'meta[name="qingzhu-local-bazi"]\'),cn='),
    ('ye=async(l=1)=>{if(f.isLoggedIn)', 'ye=async(l=1)=>{if(localBazi()||f.isLoggedIn)'),
    ('Pe=async()=>{if(!he()||!Q())return;if(!f.isLoggedIn)', 'Pe=async()=>{if(!he()||!Q())return;if(!localBazi()&&!f.isLoggedIn)'),
    ('_e=async()=>{if(f.isLoggedIn)', '_e=async()=>{if(localBazi()||f.isLoggedIn)'),
    ('ss=async()=>{if(!le.value&&!($.value<=0)&&he()&&Q()){if(!f.isLoggedIn)', 'ss=async()=>{if(!le.value&&!($.value<=0)&&he()&&Q()){if(!localBazi()&&!f.isLoggedIn)'),
    ('w.post("/v1/bazi-naming/redeem-generate",', 'w.post(localBazi()?"/v1/bazi-naming/generate":"/v1/bazi-naming/redeem-generate",'),
    ('k("兑换成功"),e.history_id&&', 'k(localBazi()?"起名成功":"兑换成功"),e.history_id&&'),
    ('k(l?.message||"兑换失败"),_e()', 'k(l?.message||(localBazi()?"生成失败":"兑换失败")),_e()'),
    ('const l=Y(u.birthTime,"12:00");T.push({path:"/bazi-naming/character-library"', 'const l=Y(u.birthTime,localBazi()?"unknown":"12:00");T.push({path:"/bazi-naming/character-library"'),
    ('!R.value&&P(f).isLoggedIn&&ee.value>0', '!R.value&&(localBazi()||P(f).isLoggedIn)&&ee.value>0'),
    ('$.value>0&&!P(f).isVipActive&&!z.value?', '!localBazi()&&$.value>0&&!P(f).isVipActive&&!z.value?'),
]
for old, new in edits:
    if source.count(old) != 1:
        raise ValueError(f"Unexpected match count for {old}")
    source = source.replace(old, new)
path.write_text(source)
# Preserve the unknown-hour display in the retained result component.
result_path = path.with_name("result-NNERRZlp.js")
result = result_path.read_text()
old = 'N=$(()=>{const i=l.value?.birth_time||"";'
new = 'N=$(()=>{if(l.value?.full_analysis?.hour_unknown)return"不清楚";const i=l.value?.birth_time||"";'
if result.count(old) != 1:
    raise ValueError("Unexpected result component shape")
result_path.write_text(result.replace(old, new))
