from pathlib import Path
import concurrent.futures,subprocess,time,shutil
ROOT=Path(__file__).resolve().parents[2]/'contexts/source_materials/anthropic_roadshow_2026_11_10'
cache=ROOT/'.segments';cache.mkdir(exist_ok=True)
text=Path('/tmp/anthropic_playlist.m3u8').read_text();(cache/'index.m3u8').write_text(text)
files=['init_0.mp4']+[x for x in text.splitlines() if x and not x.startswith('#')]
def fetch(name):
    target=cache/name
    if target.exists() and target.stat().st_size:return name
    tmp=target.with_suffix(target.suffix+'.part')
    subprocess.run(['curl','-x','http://127.0.0.1:17891','-fLsS','--retry','3','--retry-delay','1','--connect-timeout','10','--max-time','90','https://ipo.anthropic.com/video/us/roadshow/1080p/'+name,'-o',str(tmp)],check=True,capture_output=True)
    tmp.rename(target);return name
start=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for n,name in enumerate(pool.map(fetch,files),1):
        if n%40==0:print(f'{n}/{len(files)} segments, {time.monotonic()-start:.0f}s',flush=True)
print('All segments downloaded',flush=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-i',str(cache/'index.m3u8'),'-map','0:v','-map','0:a','-c','copy','-movflags','+faststart',str(ROOT/'anthropic_roadshow.full.mp4')],check=True)
print('Remux complete',flush=True)
