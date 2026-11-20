import {DatabaseSync} from 'node:sqlite';
import {dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {existsSync,mkdirSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {handleLanguages} from './languages.mjs';
import {handleAccount,initAccounts} from './account.mjs';
import {handleEvaluation,initEvaluation} from './evaluation.mjs';
import {handleNaming,initNaming} from './naming.mjs';
import {handleTools} from './tools.mjs';

const cookie = 'qingzhu_bazi_session';
const uuid = /^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/;
class LocalApiError extends Error {
  constructor(code,message,status) {
    super(message);
    this.code=code;
    this.status=status;
  }
}
const fail = (code,message,status=200) => {throw new LocalApiError(code,message,status);};
const sent = Symbol('response already written');

async function readBody(req) {
  const chunks=[];
  let bytes=0;
  for await(const chunk of req){
    bytes+=chunk.length;
    if(bytes<=64*1024) chunks.push(chunk);
  }
  if(bytes>64*1024) fail(413,'请求内容过大',413);
  if(!bytes) return {};
  try {
    const body=JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if(body && typeof body==='object' && !Array.isArray(body)) return body;
  } catch {}
  fail(1001,'请求内容需要是 JSON 对象');
}

export function localSession(req,res) {
  const current=(req.headers.cookie??'').split(/;\s*/).find(value=>value.startsWith(cookie+'='))?.slice(cookie.length+1);
  if(uuid.test(current??'')) return current;
  const session=randomUUID();
  const rest=(req.headers.cookie??'').split(/;\s*/).filter(x=>x&&!x.startsWith(cookie+'='));
  req.headers.cookie=[...rest,cookie+'='+session].join('; ');
  res.setHeader('Set-Cookie',`${cookie}=${session}; HttpOnly; SameSite=Strict; Path=/; Max-Age=31536000${process.env.QINGYAN_PUBLIC === '1' ? '; Secure' : ''}`);
  return session;
}

function openDatabase(filename) {
  if(filename!==':memory:') mkdirSync(dirname(filename),{recursive:true,mode:0o700});
  const db=new DatabaseSync(filename);
  db.exec('PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL');
  return db;
}

export async function createLocalApi() {
  const filename=process.env.QINGZHU_LOCAL_DB || fileURLToPath(new URL('../.local/site.sqlite',import.meta.url));
  const baziFilename=process.env.QINGZHU_BAZI_DB || fileURLToPath(new URL('../.local/bazi.sqlite',import.meta.url));
  const db=openDatabase(filename);
  const baziDb=existsSync(baziFilename) ? new DatabaseSync(baziFilename,{readOnly:true}) : null;
  initAccounts(db);
  initEvaluation(db);
  initNaming(db);
  const handlers=[handleAccount,handleEvaluation,handleNaming,handleTools,handleLanguages];
  return async (req,res,url,send)=>{
    if(req.headers['sec-fetch-site']==='cross-site' && !['GET','HEAD'].includes(req.method)){
      send(res,200,{code:1001,message:'请从本地应用访问',data:null});
      return true;
    }
    const session=localSession(req,res);
    const bodyKey=Symbol.for('qingzhu.local.json');
    const ctx={db,baziDb,session,body:()=>req[bodyKey]??=readBody(req),fail,sent};
    try {
      for(const handler of handlers){
        const data=await handler(req,res,url,ctx);
        if(data===undefined) continue;
        if(data!==sent) send(res,200,{code:0,message:'操作成功',data});
        return true;
      }
      return false;
    } catch(error) {
      if(!(error instanceof LocalApiError)) throw error;
      send(res,error.status,{code:error.code,message:error.message,data:null});
      return true;
    }
  };
}
