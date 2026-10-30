"""Loopback-only, read-only market-data dashboard with atomic cached snapshots.

No authenticated broker calls. The fixed watchlist is read from the registry;
refreshes update public price data, never private positions or research facts.
"""
from __future__ import annotations
import argparse
import copy
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import threading
import time
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import pandas as pd
from catalog_metrics import process
from collect_extended import collect_symbol

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE=ROOT/'contexts/survey_sessions/us_market_daily'
BJ=ZoneInfo('Asia/Shanghai');ET=ZoneInfo('America/New_York')


def stamp():return datetime.now(timezone.utc).isoformat()


def atomic_json(path, obj):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    temp.replace(path)


def latest_reference():
    candidates=sorted(ARCHIVE.glob('????-??-??/watchlist_catalog/catalog.json'))
    if not candidates:raise RuntimeError('No reviewed catalog snapshot exists')
    return candidates[-1].parent


def sync_registry(catalog, source_catalog=None):
    """Authoritative membership plus reviewed descriptions, without invented facts."""
    registry=json.loads((HERE/'watchlist_groups.json').read_text())
    known={a['symbol']:a for g in catalog['groups'] for a in g['assets']}
    incoming={a['symbol']:a for g in (source_catalog or {'groups':[]})['groups'] for a in g['assets']}
    result=copy.deepcopy(catalog);result['groups']=[]
    for g in registry['groups']:
        group={**g,'assets':[]}
        for registered in g['assets']:
            s=registered['symbol'];asset=copy.deepcopy(known.get(s) or incoming.get(s))
            if asset is None:
                is_stock='industry_id' in registered
                asset={'symbol':s,'name':registered['name'],'kind':'stock' if is_stock else 'fund','kind_label':'个股' if is_stock else 'ETF','facts':{'name':registered['name'],'strategy':'新增研究候选，经营与持仓资料待人工核验','sources':[],'gaps':['本地研究资料尚未补齐']},'personal_note':'新增观察不代表低估或已批准仓位。','quote':{}}
            if s in incoming:
                for key in ['facts','personal_note','role','next','industry_id','industry','name','kind','kind_label']:
                    if key in incoming[s]:asset[key]=copy.deepcopy(incoming[s][key])
            asset.update(registered);group['assets'].append(asset)
        result['groups'].append(group)
    return result


def probe_completed_session(out, now=None):
    """Use actual exchange bars and the provider's current session end metadata.

    Past dated bars are finished. A bar for today's NY date is usable only if
    its declared regular session end has passed, including early-close days.
    No weekday/holiday guess or intraday close is silently treated as final.
    """
    now=now or datetime.now(timezone.utc)
    url='https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1mo&interval=1d&includePrePost=false'
    raw=subprocess.run(['curl','--silent','--show-error','--fail','--location','--max-time','30','--retry','1','-A','Mozilla/5.0',url],check=True,capture_output=True).stdout
    (out/'raw'/'completed_session_probe.json').write_bytes(raw)
    result=json.loads(raw)['chart']['result'][0];meta=result['meta']
    if meta.get('symbol')!='^GSPC':raise ValueError('Session probe symbol mismatch')
    current_end=meta.get('currentTradingPeriod',{}).get('regular',{}).get('end')
    current_end_day=datetime.fromtimestamp(current_end,ET).date() if current_end else None
    today=now.astimezone(ET).date();eligible=[]
    for ts,c in zip(result['timestamp'],result['indicators']['quote'][0]['close']):
        day=datetime.fromtimestamp(ts,ET).date()
        if c is None or c<=0:continue
        if day<today or (day==today and current_end_day==day and now.timestamp()>=current_end+60):eligible.append(day)
    if not eligible:raise ValueError('No verified completed session from actual daily bars')
    session=max(eligible).isoformat()
    return session,{'source_url':url,'latest_completed_regular_session':session,'captured_at_utc':now.isoformat(),'current_regular_end_utc':datetime.fromtimestamp(current_end,timezone.utc).isoformat() if current_end else None,'method':'Actual valid dated daily closes; same-day close admitted only after provider-declared regular end plus60sec'}


class Store:
    def __init__(self,directory,reference=None,cooldown=60):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        self.reference=Path(reference) if reference else latest_reference()
        self.reference_signature=self._reference_signature(self.reference)
        self.lock=threading.RLock();self.cooldown=cooldown;self.running=False;self.last_started=0.
        self.state_path=self.directory/'state.json';self.status_path=self.directory/'refresh_status.json'
        source=json.loads((self.reference/'catalog.json').read_text())
        if self.state_path.exists():self.state=json.loads(self.state_path.read_text())
        else:
            risks=json.loads((self.reference/'risk_metrics.json').read_text())
            self.state={'schema_version':1,'version':'initial-'+hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()[:12],'catalog':source,'risk_metrics':risks,'refresh_status':{'status':'idle','completed':0,'total':0,'last_success_at_utc':risks.get('captured_at_utc'),'note':'已载入最近已核验快照；点刷新更新行情，研究正文按原披露日期保留。'}}
        self.state['catalog']=sync_registry(self.state['catalog'],source)
        wanted={a['symbol'] for g in self.state['catalog']['groups'] for a in g['assets']}
        self.state['risk_metrics']['symbols']={s:r for s,r in self.state['risk_metrics']['symbols'].items() if s in wanted}
        self.status=self.state.get('refresh_status',{'status':'idle'})
        if self.status.get('status')=='running':self.status={**self.status,'status':'interrupted','message':'上次刷新进程中断，保留最后有效快照。'}
        self.state['refresh_status']=self.status;atomic_json(self.state_path,self.state);atomic_json(self.status_path,self.status)

    @staticmethod
    def _reference_signature(reference):
        file=Path(reference)/'catalog.json';stat=file.stat()
        return (str(file.resolve()),stat.st_mtime_ns,stat.st_size)

    def _sync_reviewed_reference(self):
        try:
            reference=latest_reference();signature=self._reference_signature(reference)
            if signature==self.reference_signature:return
            source=json.loads((reference/'catalog.json').read_text())
            self.state['catalog']=sync_registry(self.state['catalog'],source)
            self.state['reviewed_source']={'relative_path':str(reference.relative_to(ARCHIVE)),'loaded_at_utc':stamp(),'report_date':source.get('report_date')}
            suffix=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()[:12]
            self.state['version']=self.state['version'].split('.research-')[0]+'.research-'+suffix
            self.reference=reference;self.reference_signature=signature
            atomic_json(self.state_path,self.state)
        except (OSError,ValueError,KeyError) as exc:
            self.status['reviewed_source_warning']='最新研究资料未能载入，保留上次有效版本：'+str(exc)

    def snapshot(self):
        with self.lock:
            self._sync_reviewed_reference()
            state=copy.deepcopy(self.state);state['catalog']=sync_registry(state['catalog']);state['refresh_status']=copy.deepcopy(self.status)
            wanted={a['symbol'] for g in state['catalog']['groups'] for a in g['assets']}
            state['risk_metrics']['symbols']={s:m for s,m in state['risk_metrics']['symbols'].items() if s in wanted}
            return state

    def status_snapshot(self):
        with self.lock:return copy.deepcopy(self.status)

    def start_refresh(self):
        with self.lock:
            if self.running:return 409,self.status_snapshot()
            elapsed=time.monotonic()-self.last_started
            if self.last_started and elapsed<self.cooldown:return 429,{**self.status_snapshot(),'retry_after_seconds':max(1,int(self.cooldown-elapsed)+1)}
            self.running=True;self.last_started=time.monotonic()
            job=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            self.status={'status':'running','job_id':job,'phase':'session','completed':0,'total':0,'started_at_utc':stamp(),'last_success_at_utc':self.state.get('refresh_status',{}).get('last_success_at_utc'),'message':'正在核验最近已完成交易日'}
            atomic_json(self.status_path,self.status)
            threading.Thread(target=self._refresh,args=(job,),name='catalog-market-refresh',daemon=True).start()
            return 202,self.status_snapshot()

    def progress(self,**values):
        with self.lock:self.status.update(values);atomic_json(self.status_path,self.status)

    def _refresh(self,job):
        captured=datetime.now(timezone.utc);run=self.directory/'refreshes'/job;(run/'raw').mkdir(parents=True)
        old=self.snapshot();catalog=old['catalog'];risks=copy.deepcopy(old['risk_metrics'])
        assets={a['symbol']:a for g in catalog['groups'] for a in g['assets']}
        failures=[];new_metrics={};new_extended={};done=0
        try:
            overrides=self.reference/'metrics_quality_overrides.json'
            if overrides.exists():shutil.copy2(overrides,run/'metrics_quality_overrides.json')
            asof,probe=probe_completed_session(run,captured)
            atomic_json(run/'session_verification.json',probe)
            self.progress(phase='history',total=len(assets)*2,message='正在获取历史行情并重算指标',regular_session=asof)
            with ThreadPoolExecutor(max_workers=4) as pool:
                jobs={pool.submit(process,s,a,run,pd.Timestamp(asof),captured):s for s,a in assets.items()}
                for f in as_completed(jobs):
                    s=jobs[f]
                    try:
                        m=f.result()
                        if m.get('asof_session')!=asof:
                            failures.append({'symbol':s,'phase':'history_freshness','error':f"日线截至{m.get('asof_session')}，落后已完成交易日{asof}；保留上次有效数据"})
                        else:new_metrics[s]=m
                        # The extended collector consumes exactly dated regular
                        # baselines. No synthetic close/high/low is appended.
                        if s in new_metrics:shutil.copy2(run/f'metrics_{s}_daily.csv',run/f'{s}_daily.csv')
                    except Exception as exc:failures.append({'symbol':s,'phase':'history','error':str(exc)})
                    done+=1;self.progress(completed=done)
            self.progress(phase='extended',message='正在读取独立盘前盘后分钟参考')
            rawdir=run/'extended_raw'/job;rawdir.mkdir(parents=True)
            with ThreadPoolExecutor(max_workers=4) as pool:
                jobs={pool.submit(collect_symbol,s,run,asof,captured,rawdir):s for s in assets if s in new_metrics and new_metrics[s].get('asof_session')==asof}
                for f in as_completed(jobs):
                    s=jobs[f]
                    try:
                        v=f.result();new_extended[s]=v
                        if v.get('raw_file'):
                            raw_result=json.loads((run/v['raw_file']).read_text())['chart']['result'][0]
                            meta=raw_result['meta'];ts=meta.get('regularMarketTime');price=meta.get('regularMarketPrice')
                            regular=meta.get('currentTradingPeriod',{}).get('regular',{})
                            if ts and isinstance(price,(int,float)) and price>0 and ts<=captured.timestamp()+60:
                                tm=datetime.fromtimestamp(ts,ET)
                                if tm.date().isoformat()>=asof:
                                    in_progress=regular.get('start',0)<=ts<regular.get('end',0) and captured.timestamp()<regular.get('end',0)
                                    v['latest_regular']={'price_usd':price,'session':tm.date().isoformat(),'segment':'regular_intraday' if in_progress else 'regular_close_reference','time_et':tm.isoformat(),'time_beijing':tm.astimezone(BJ).isoformat(),'captured_at_utc':captured.isoformat(),'source_url':v['source_url'],'single_source':True,'note':'明确时间戳的常规时段提供方参考；盘中数据不进入已完成日线指标'}
                        if v.get('status')!='available':failures.append({'symbol':s,'phase':'extended','error':v.get('error','Minute data unavailable')})
                    except Exception as exc:failures.append({'symbol':s,'phase':'extended','error':str(exc)})
                    done+=1;self.progress(completed=done)
            for s,a in assets.items():
                if s not in new_metrics:
                    a['last_refresh_error']=next(x['error'] for x in failures if x['symbol']==s and x['phase'] in ('history','history_freshness'));a['last_refresh_attempt_at_utc']=captured.isoformat();continue
                m=new_metrics[s];risks['symbols'][s]=m
                with (run/f'metrics_{s}_daily.csv').open() as stream:rows=list(csv.DictReader(stream))
                rows=[x for x in rows if x['date']<=m['asof_session']]
                close=float(rows[-1]['close']);previous=float(rows[-2]['close'])
                a['quote']={'symbol':s,'session':m['asof_session'],'close':round(close,2),'day_pct':(close/previous-1)*100,'source_url':m['source_url'],'captured_at_utc':captured.isoformat(),'crosscheck_status':'Yahoo完整常规日线，单一提供方；本次自动刷新未重新执行第二来源逐项核验。'}
                a.pop('last_refresh_error',None);a['last_refresh_attempt_at_utc']=captured.isoformat()
                # Do not keep stale post quotes under a new capture label.
                a.pop('post_snapshot',None)
                if s in new_extended:a['extended']=new_extended[s]
                else:a['extended']={'status':'unavailable','captured_at_utc':captured.isoformat(),'error':'未取得本次有效分钟行情'}
            if not new_metrics:raise RuntimeError('All symbols failed; last valid state retained')
            catalog['report_date']=captured.astimezone(BJ).date().isoformat();catalog['regular_session']=asof;catalog['generated_at_beijing']=captured.astimezone(BJ).isoformat();catalog['research_updated_by_refresh']=False
            risks['requested_asof']=asof;risks['captured_at_utc']=captured.isoformat();risks['errors']=failures
            status={'status':'partial' if failures else 'complete','job_id':job,'phase':'done','completed':len(assets)*2,'total':len(assets)*2,'started_at_utc':captured.isoformat(),'finished_at_utc':stamp(),'last_success_at_utc':stamp(),'regular_session':asof,'successful_history_symbols':len(new_metrics),'symbol_count':len(assets),'errors':failures,'message':'行情与历史指标已更新；研究文字及发行人持仓仍保留各自披露日期。'}
            state={'schema_version':1,'version':job,'catalog':catalog,'risk_metrics':risks,'refresh_status':status,'session_verification':probe}
            atomic_json(run/'state.json',state)
            with self.lock:
                atomic_json(self.state_path,state);self.state=state;self.status=status;atomic_json(self.status_path,status)
        except Exception as exc:
            self.progress(status='failed',phase='done',finished_at_utc=stamp(),errors=failures,message=str(exc)+'；保留最后有效数据。')
        finally:
            with self.lock:self.running=False


class Handler(BaseHTTPRequestHandler):
    server_version='LocalMarketCatalog/1.0'
    def authorized_host(self):return self.headers.get('Host') in self.server.allowed_hosts
    def send(self,code,body,kind='application/json; charset=utf-8'):
        if not isinstance(body,(bytes,bytearray)):body=json.dumps(body,ensure_ascii=False).encode()
        self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if not self.authorized_host():return self.send(403,{'error':'Host not allowed'})
        if self.path=='/api/state':return self.send(200,self.server.store.snapshot())
        if self.path=='/api/status':return self.send(200,self.server.store.status_snapshot())
        if self.path=='/':
            from render_catalog import render
            state=self.server.store.snapshot();catalog=state['catalog'];catalog['live_mode']=True;catalog['live_status']=state['refresh_status'];catalog['live_version']=state['version']
            try:
                return self.send(200,render(catalog,state['risk_metrics']).encode(),'text/html; charset=utf-8')
            except Exception as exc:
                print('Catalog render failed:',repr(exc),flush=True)
                return self.send(500,{'error':'页面渲染失败，最后有效市场数据仍已保存。'})
        return self.send(404,{'error':'Not found'})
    def do_POST(self):
        if not self.authorized_host():return self.send(403,{'error':'Host not allowed'})
        if self.path!='/api/refresh':return self.send(404,{'error':'Not found'})
        origin=self.headers.get('Origin')
        if origin not in self.server.allowed_origins or self.headers.get('X-Catalog-Refresh')!='1':return self.send(403,{'error':'Same-origin refresh header required'})
        try:length=int(self.headers.get('Content-Length','0'))
        except ValueError:return self.send(400,{'error':'Invalid content length'})
        if length>512:return self.send(413,{'error':'Request too large'})
        if length:self.rfile.read(length)
        code,status=self.server.store.start_refresh();return self.send(code,status)
    def do_OPTIONS(self):return self.send(403,{'error':'Cross-origin access is disabled'})
    def log_message(self,format,*args):print(datetime.now(timezone.utc).isoformat(),format%args,flush=True)


def serve(port=8789,directory=None,reference=None):
    store=Store(directory or ARCHIVE/'live_catalog',reference)
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.store=store;server.allowed_hosts={f'127.0.0.1:{port}',f'localhost:{port}'};server.allowed_origins={f'http://{x}' for x in server.allowed_hosts}
    print(f'Local catalog running at http://127.0.0.1:{port}/',flush=True)
    server.serve_forever()

def start_background(port=8789,directory=None,reference=None):
    import sys
    import urllib.request
    endpoint=f'http://127.0.0.1:{port}/api/status'
    try:
        with urllib.request.urlopen(endpoint,timeout=2) as response:
            existing=json.load(response)
            if isinstance(existing,dict) and 'status' in existing:
                print(f'Catalog is already running at http://127.0.0.1:{port}/');return
    except Exception:
        pass
    logs=Path.home()/'Library/Logs/CodexMarketCatalog';logs.mkdir(parents=True,exist_ok=True)
    destination=Path(directory or ARCHIVE/'live_catalog');destination.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,'-u',str(Path(__file__).resolve()),'--port',str(port)]
    if directory:command += ['--directory',str(directory)]
    if reference:command += ['--reference',str(reference)]
    with (logs/'detached-server.log').open('ab') as log:
        child=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    (destination/'server.pid').write_text(str(child.pid)+'\n')
    for _ in range(40):
        if child.poll() is not None:raise RuntimeError('Catalog process exited; inspect local server log')
        try:
            with urllib.request.urlopen(endpoint,timeout=.3) as response:
                if response.status==200:
                    print(f'Catalog started at http://127.0.0.1:{port}/ (PID{child.pid})');return
        except Exception:
            time.sleep(.1)
    raise RuntimeError('Startup has not completed; inspect local server log and port')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8789);p.add_argument('--directory',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--background',action='store_true');args=p.parse_args()
    if args.background:start_background(args.port,args.directory,args.reference)
    else:serve(args.port,args.directory,args.reference)
