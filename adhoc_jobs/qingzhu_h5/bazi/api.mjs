import {randomUUID} from 'node:crypto';
import {mkdirSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {parseBirth, InputError} from './calendar.mjs';
import {analysisFor, effectiveElements, generateNames, libraryFor, NAME_LIMIT} from './names.mjs';

const base = '/api/v1/bazi-naming';
const cookie = 'qingzhu_bazi_session';
const uuid = /^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/;
const packages = [
  {id:1,code:'LOCAL',type:'bazi_naming',name:'本地八字起名',price:0,originalPrice:0,nameCount:NAME_LIMIT,isDefault:true,tag:'本地生成',features:[]},
];
const allowedAuxiliary = new Set([
  'GET /api/v1/naming/detail','POST /api/v1/naming/collect',
]);
class NotFound extends Error {}

async function readBody(req) {
  if(req[Symbol.for('qingzhu.local.json')]) return req[Symbol.for('qingzhu.local.json')];
  let byteLength = 0;
  const chunks = [];
  for await (const chunk of req) {
    byteLength += chunk.length;
    if (byteLength > 8192) throw new InputError('请求内容过大');
    chunks.push(chunk);
  }
  try {
    const body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if (body && typeof body === 'object' && !Array.isArray(body)) return body;
  } catch {}
  throw new InputError('请求内容需要是 JSON 对象');
}

const genderCode = birth => birth.gender==='male' ? 1 : 2;
const birthStamp = birth => birth.time==='unknown' ? birth.birthDate : birth.birthDate+'T'+birth.time+':00';

function createStore(filename) {
  if (filename!==':memory:') mkdirSync(dirname(filename),{recursive:true,mode:0o700});
  const db = new DatabaseSync(filename);
  db.exec(`
    PRAGMA busy_timeout = 5000;
    PRAGMA journal_mode = WAL;
    CREATE TABLE IF NOT EXISTS bazi_history (
      id TEXT PRIMARY KEY, session TEXT NOT NULL, created TEXT NOT NULL, request_key TEXT NOT NULL, data TEXT NOT NULL,
      UNIQUE(session,request_key)
    );
    CREATE INDEX IF NOT EXISTS bazi_history_session ON bazi_history(session, created DESC);
    CREATE TABLE IF NOT EXISTS favorites (
      session TEXT NOT NULL, kind TEXT NOT NULL, target TEXT NOT NULL, PRIMARY KEY(session,kind,target)
    );
  `);
  return {
    get(id,session) {
      const row = db.prepare('SELECT data FROM bazi_history WHERE id=? AND session=?').get(id,session);
      if (!row) throw new NotFound('未找到这条起名记录');
      return JSON.parse(row.data);
    },
    list(session,page,size) {
      const rows = db.prepare('SELECT data FROM bazi_history WHERE session=? ORDER BY created DESC,id DESC LIMIT ? OFFSET ?')
        .all(session,size,(page-1)*size);
      const total = db.prepare('SELECT count(*) AS total FROM bazi_history WHERE session=?').get(session).total;
      return {total,items:rows.map(({data})=>{
        const record=JSON.parse(data);
        return {id:record.id,surname:record.birth.surname,gender:genderCode(record.birth),
          birthTime:birthStamp(record.birth),bazi:record.analysis.bazi_str,createdAt:record.created,
          nameCount:record.names.length,charLibraryUnlocked:false};
      })};
    },
    generate(session,birth) {
      const requestKey = JSON.stringify(['strength-and-name-score-v2',birth.surname,birth.gender,birth.birthDate,birth.time,birth.selected]);
      const lookup = db.prepare('SELECT id FROM bazi_history WHERE session=? AND request_key=?');
      const existing = lookup.get(session,requestKey);
      if (existing) return existing.id;
      const analysis = analysisFor(birth);
      const names = generateNames(birth,analysis);
      if (!names.length) throw new InputError('当前用字条件下没有合适的名字，请尝试更换喜用五行');
      const id = randomUUID();
      const created = new Date().toISOString();
      const data = JSON.stringify({id,birth,analysis,names,created});
      db.prepare('INSERT OR IGNORE INTO bazi_history VALUES (?,?,?,?,?)').run(id,session,created,requestKey,data);
      return lookup.get(session,requestKey).id;
    },
    favorites(session,kind) {
      return new Set(db.prepare('SELECT target FROM favorites WHERE session=? AND kind=?').all(session,kind).map(x=>x.target));
    },
    favorite(session,kind,target,value) {
      if (value) db.prepare('INSERT OR IGNORE INTO favorites VALUES (?,?,?)').run(session,kind,target);
      else db.prepare('DELETE FROM favorites WHERE session=? AND kind=? AND target=?').run(session,kind,target);
      return value;
    },
  };
}

function pageFrom(url) {
  const positive = (value,fallback,max) => /^\d+$/.test(value??'')
    ? Math.min(max,Math.max(1,Number(value))) : fallback;
  return {
    page:positive(url.searchParams.get('page'),1,100000),
    size:positive(url.searchParams.get('page_size') ?? url.searchParams.get('pageSize'),30,100),
  };
}

function nameId(recordId, row) {return recordId+':'+row.index;}

function publicName(recordId, row, favorites) {
  const {givenChars,index,...name} = row;
  const id = nameId(recordId,row);
  return {...name,id,isFavorite:favorites.has(id),is_collected:favorites.has(id)};
}

function sliceNames(record,favorites,page=1,size=30) {
  const offset = (page-1)*size;
  const total = record.names.length;
  return {
    names:record.names.slice(offset,offset+size).map(row=>publicName(record.id,row,favorites)),
    total,has_more:offset+size<total,is_unlimited:false,
  };
}

function nameDetails(record,row,favorites) {
  const {birth,analysis}=record;
  const name=publicName(record.id,row,favorites);
  const score = {total:row.score,level:'喜用匹配',comment:'本地用字筛选与音形排序，仅供同批候选比较。',dimensions:[]};
  const chosen=effectiveElements(birth,analysis);
  return {
    name_card:{name:row.name,full_name:row.full_name,surname:birth.surname,pinyin:row.pinyin,gender:birth.gender==='male'?'男':'女'},
    id:name.id,history_id:record.id,birth_time:birthStamp(birth),reference:row.source,
    is_collected:name.is_collected,score,meaning:{brief:row.meaning,detail:row.meaning},
    poem:row.source ? {has_poem:true,source:row.source.title,verse:row.source.poem} : {has_poem:false},
    characters:row.givenChars.map(ch=>({
      character:ch.character,char:ch.character,pinyin:ch.pinyin,wuxing:ch.wuxing,strokes:ch.strokes,
      meaning:ch.nameConnotation,connotation:ch.nameConnotation,
    })),
    xiyong_shen:chosen,xiyong_source:birth.selected.length?'parent':'system',
    system_xiyong_shen:analysis.xiyong_shen,ji_shen:analysis.ji_shen,bazi:analysis.bazi,
    ri_gan:analysis.riGan,ri_zhu_strength:analysis.riZhuStrength,pattern:analysis.pattern,
    yong_shen_detail:analysis.yong_shen_detail,zodiac:analysis.zodiac,zodiac_rules:analysis.zodiac_rules,
  };
}

export function createBaziApi(filename = process.env.QINGZHU_BAZI_DB ||
  fileURLToPath(new URL('../.local/bazi.sqlite',import.meta.url))) {
  const store = createStore(filename === ':memory:' ? filename : resolve(filename));
  return async (req,res,url,send) => {
    const pathname = url.pathname;
    const route = req.method+' '+pathname;
    if (!pathname.startsWith(base+'/') && !allowedAuxiliary.has(route)) return false;
    const incoming = (req.headers.cookie??'').split(/;\s*/).find(part=>part.startsWith(cookie+'='))?.slice(cookie.length+1);
    const session = uuid.test(incoming??'') ? incoming : randomUUID();
    if (session!==incoming) res.setHeader('Set-Cookie',`${cookie}=${session}; HttpOnly; SameSite=Strict; Path=/; Max-Age=31536000${process.env.QINGYAN_PUBLIC === '1' ? '; Secure' : ''}`);
    function ok(data) {
      send(res,200,{code:0,message:'操作成功',data});
      return true;
    }
    try {
      if (req.headers['sec-fetch-site'] === 'cross-site') throw new InputError('请从本地应用访问');
      const leaf = pathname.slice(base.length);
      switch (req.method+' '+leaf) {
        case 'GET /packages': return ok(packages);
        case 'GET /free-quota': return ok({bazi_free_count:1,name_count_per_use:NAME_LIMIT});
        case 'GET /pending-paid-order': return ok(null);
        case 'GET /pending-vouchers': return ok({items:[]});
        case 'POST /analysis': {
          return ok(analysisFor(parseBirth(await readBody(req))));
        }
        case 'POST /character-library/preview': {
          const birth = parseBirth(await readBody(req));
          const limit = url.searchParams.get('limit')==='0' ? 0 : 3;
          return ok(libraryFor(birth,analysisFor(birth),limit,store.favorites(session,'character')));
        }
        case 'POST /unlock-char-library': {
          const {history_id}=await readBody(req);
          if(history_id) store.get(history_id,session);
          return ok({locked:false,unlocked:true,history_id:history_id||null});
        }
        case 'POST /claim-and-generate':
        case 'POST /generate-vip':
        case 'POST /redeem-generate':
        case 'POST /generate': {
          const id = store.generate(session,parseBirth(await readBody(req)));
          return ok({history_id:id,bazi_free_count_remaining:1});
        }
        case 'GET /history': {
          const {page,size} = pageFrom(url);
          return ok(store.list(session,page,size));
        }
        case 'GET /character-library': {
          const {birth,analysis}=store.get(url.searchParams.get('historyId')??'',session);
          return ok(libraryFor(birth,analysis,0,store.favorites(session,'character')));
        }
        case 'POST /character-library/favorite': {
          const {character,action}=await readBody(req);
          if (typeof character!=='string'||!/^[\p{Script=Han}]$/u.test(character)) throw new InputError('请选择要收藏的用字');
          const favorites = store.favorites(session,'character');
          return ok({favorited:store.favorite(session,'character',character,action==='uncollect'?false:action==='collect'?true:!favorites.has(character))});
        }
      }
      const history = req.method==='GET' && /^\/history\/([a-f0-9-]+)(\/names)?$/.exec(leaf);
      if (history && uuid.test(history[1])) {
        const record = store.get(history[1],session);
        const favorites = store.favorites(session,'name');
        if (history[2]) {
          const {page,size} = pageFrom(url);
          return ok(sliceNames(record,favorites,page,size));
        }
        const {birth,analysis}=record;
        // The result view loads its first page from /history then fetches more on demand.
        return ok({
          history_id:record.id,surname:birth.surname,gender:genderCode(birth),birth_time:birthStamp(birth),
          bazi:analysis.bazi,bazi_str:analysis.bazi_str,full_analysis:analysis,
          package_code:'LOCAL',name_count:record.names.length,xiyong_shen:effectiveElements(birth,analysis),
          xiyong_source:birth.selected.length?'parent':'system',system_xiyong_shen:analysis.xiyong_shen,
          ji_shen:analysis.ji_shen,...sliceNames(record,favorites,1,NAME_LIMIT),
        });
      }
      if (allowedAuxiliary.has(route)) {
        const args = req.method==='GET' ? Object.fromEntries(url.searchParams) : await readBody(req);
        const name = /^([a-f0-9-]+):(\d+)$/.exec(args.name_id??'');
        if (!name || !uuid.test(name[1])) throw new NotFound('未找到这个名字');
        const record = store.get(name[1],session);
        const row=record.names[Number(name[2])];
        if (!row) throw new NotFound('未找到这个名字');
        if (req.method==='GET') return ok(nameDetails(record,row,store.favorites(session,'name')));
        if (!['collect','uncollect'].includes(args.action)) throw new InputError('不支持的收藏操作');
        return ok({is_collected:store.favorite(session,'name',nameId(record.id,row),args.action==='collect')});
      }
      return false;
    } catch (error) {
      if (error instanceof InputError) {
        send(res,200,{code:1001,message:error.message,data:null});
        return true;
      }
      if (error instanceof NotFound) {
        send(res,404,{code:404,message:error.message,data:null});
        return true;
      }
      throw error;
    }
  };
}
