from pathlib import Path
from PIL import Image
import json,re,hashlib
root=Path(__file__).parent;pkg=Path('/Users/xuhao/Documents/Other/xhs-minitools/packages/skewer-jam');m=json.loads((root/'evidence/exported/manifest.json').read_text())
base=['饺子串','玉子烧','年糕串','红椒肉串','青椒肉串','三文鱼串','牛肉串','黄瓜串','香肠串','豆角串','鸡翅串','烤豆腐','烤鸡腿','菠萝串','蔬菜串']
extra=[(54,'大葱串'),(56,'热狗串'),(62,'香菇串'),(64,'平菇串'),(66,'金针菇串'),(68,'鸣门卷'),(69,'玉米串'),(73,'披萨串'),(76,'白菜串'),(83,'烤肠'),(84,'塔可串'),(85,'蟹柳串'),(86,'肉丸串'),(89,'蜜桃串'),(90,'龙虾串'),(92,'饭团串'),(96,'紫薯包'),(99,'花菜串'),(100,'西兰花串'),(102,'扇贝串'),(104,'虾串'),(120,'芦笋串'),(122,'榴莲串'),(129,'柠檬虾串'),(98,'洋葱串')]
foods=[{'name':name} for name in base];provenance=[]
for num,name in extra:
 choices=[x for x in m if x['name']==f'item_{num:03}' and x['source'].startswith('shared_ui')]
 assert choices,num
 r=next((x for x in choices if num==54 and str(x['id']).startswith('60211049')),choices[0]);idx=len(foods);im=Image.open(root/r['file']);im.save(pkg/f'src/assets/food_{idx}.webp','WEBP',lossless=True,method=6)
 foods.append({'name':name});provenance.append({'asset':f'food_{idx}.webp','original_name':r['name'],'source':r['source'],'id':r['id'],'source_sha256':hashlib.sha256((root/r['file']).read_bytes()).hexdigest()})
s='(function(root){\n  var foods='+json.dumps(foods,ensure_ascii=False,separators=(',',':'))+';\n  if(typeof module!=="undefined"&&module.exports)module.exports=foods;else root.SkewerFoods=foods;\n}(typeof window!=="undefined"?window:this));\n'
(pkg/'src/foods.js').write_text(s)
(root/'evidence/wifi_refine/food_catalog.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
print('food catalog',len(foods),'new sprites',len(extra))
