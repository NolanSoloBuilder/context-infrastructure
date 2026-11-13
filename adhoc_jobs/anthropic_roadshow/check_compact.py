from pathlib import Path
import json,subprocess,re,hashlib
P=Path(__file__).resolve().parents[2]/'contexts/source_materials/anthropic_roadshow_2026_11_10';V=P/'verification';out=P/'anthropic_roadshow.bilingual.compact.mp4';src=P/'anthropic_roadshow.bilingual.mp4'
def probe(f):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_packets','-show_streams','-show_format','-of','json',str(f)]))
a,b=probe(src),probe(out)
assert a['streams'][0]['nb_read_packets']==b['streams'][0]['nb_read_packets']
assert abs(float(a['format']['duration'])-float(b['format']['duration']))<.1
assert b['streams'][0]['codec_name']=='hevc'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(out),'-map','0:s:0','-c:s','srt',str(V/'compact_bilingual.srt')],check=True)
assert (V/'compact_bilingual.srt').read_text(encoding='utf-8-sig').strip()==(P/'anthropic_roadshow.zh_en.srt').read_text(encoding='utf-8-sig').strip()
quality=[]
for t in [35,1840,2400,2550]:
 r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-threads','2','-ss',str(t),'-i',str(src),'-threads','2','-ss',str(t),'-i',str(out),'-t','2','-filter_complex_threads','1','-filter_complex','[0:v:0]setpts=PTS-STARTPTS[a];[1:v:0]setpts=PTS-STARTPTS[b];[a][b]ssim','-an','-f','null','-'],capture_output=True,text=True,check=True)
 q=float(re.findall(r'All:([0-9.]+)',r.stderr)[-1]);quality.append({'time_seconds':t,'ssim':q})
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-ss','2400','-i',str(out),'-frames:v','1',str(V/'compact_financial.jpg')],check=True)
report={'source_bytes':src.stat().st_size,'compressed_bytes':out.stat().st_size,'reduction_percent':round(100*(1-out.stat().st_size/src.stat().st_size),2),'codec':'hevc/hvc1','resolution':'1920x1080','duration_seconds':b['format']['duration'],'video_packets':b['streams'][0]['nb_read_packets'],'subtitle_roundtrip_identical':True,'sample_ssim':quality}
(V/'compression_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True)
h=hashlib.sha256()
with out.open('rb') as f:
 for x in iter(lambda:f.read(4194304),b''):h.update(x)
with (P/'SHA256SUMS.txt').open('a') as f:f.write(h.hexdigest()+'  '+out.name+'\n')
