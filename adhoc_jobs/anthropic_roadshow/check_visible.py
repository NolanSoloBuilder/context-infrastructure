from pathlib import Path
import subprocess,json,re,hashlib,sys
P=Path(__file__).resolve().parents[2]/'contexts/source_materials/anthropic_roadshow_2026_11_10';V=P/'verification'/('xhs_compatible' if len(sys.argv)>1 and sys.argv[1]=='anthropic_roadshow_bilingual.mp4' else 'under1gb' if len(sys.argv)>1 else '.');src=P/'anthropic_roadshow.mp4';out=P/(sys.argv[1] if len(sys.argv)>1 else 'anthropic_roadshow.bilingual.visible.mp4')
if len(sys.argv)>1: assert out.stat().st_size<1_000_000_000, 'File exceeds 1 GB'
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_packets','-show_streams','-show_format','-of','json',str(out)]))
assert not any(s['codec_type']=='subtitle' for s in d['streams'])
video=next(s for s in d['streams'] if s['codec_type']=='video')
assert int(video['nb_read_packets'])==61458
assert abs(float(d['format']['duration'])-2563.310750)<.1
quality=[]
for t in [40,1840,2400,2493]:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(out),'-frames:v','1',str(V/f'visible_actual_{t}.jpg')],check=True)
 r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-threads','2','-ss',str(t),'-i',str(src),'-threads','2','-ss',str(t),'-i',str(out),'-t','2','-filter_complex_threads','1','-filter_complex','[0:v]crop=1920:840:0:0,setpts=PTS-STARTPTS[a];[1:v]crop=1920:840:0:0,setpts=PTS-STARTPTS[b];[a][b]ssim','-an','-f','null','-'],check=True,capture_output=True,text=True)
 quality.append({'seconds':t,'upper_840px_ssim':float(re.findall(r'All:([0-9.]+)',r.stderr)[-1])})
report={'size_bytes':out.stat().st_size,'duration_seconds':d['format']['duration'],'video_packets':video['nb_read_packets'],'codec':video['codec_name'],'dimensions':[video['width'],video['height']],'subtitle_streams':0,'subtitle_delivery':'Burned into video pixels; see actual extracted frames','ass_event_count':702,'sample_quality_excluding_subtitle_area':quality}
(V/'visible_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True)
h=hashlib.sha256()
with out.open('rb') as f:
 for x in iter(lambda:f.read(4194304),b''):h.update(x)
with (P/'SHA256SUMS.txt').open('a') as f:f.write(h.hexdigest()+'  '+out.name+'\n')
