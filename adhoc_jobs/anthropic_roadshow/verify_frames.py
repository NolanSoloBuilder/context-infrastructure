from pathlib import Path
import subprocess,json,bisect,hashlib
P=Path(__file__).resolve().parents[2]/'contexts/source_materials/anthropic_roadshow_2026_11_10'
V=P/'verification';V.mkdir(exist_ok=True)
f=P/'anthropic_roadshow.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));(V/'probe.json').write_text(json.dumps(probe,indent=2))
# Decode every video and audio frame; CRC provides a compact audit trail per decoded video frame.
with (V/'decode.log').open('w') as log:
 r=subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-xerror','-threads','2','-i',str(f),'-map','0:v:0','-an','-f','framehash','-hash','crc32',str(V/'frames.crc32'),'-map','0:a:0','-vn','-f','null','-'],stderr=log)
assert r.returncode==0, 'Full decode failed; inspect decode.log'
lines=(V/'frames.crc32').read_text().splitlines();tb=[s.split(':',1)[1].strip() for s in lines if s.startswith('#tb 0:')][0];n,d=map(int,tb.split('/'));unit=n/d
frames=[line.split(',') for line in lines if line and not line.startswith('#')];pts=[int(f[2])*unit for f in frames]
assert all(b>a for a,b in zip(pts,pts[1:])), 'Non-monotonic frame times'
cues=json.loads((P/'subtitle_validation.json').read_text())['cues'];counts={str(c['id']):0 for c in cues};starts=[c['start'] for c in cues];uncovered=0
for t in pts:
 i=bisect.bisect_right(starts,t)-1
 if i>=0 and t<cues[i]['end']:counts[str(cues[i]['id'])]+=1
 else:uncovered+=1
assert all(counts.values()),'Some subtitle cues have no video frames'
assert max(c['end'] for c in cues)<=float(probe['format']['duration'])
summary={'decode_exit_code':r.returncode,'video_frames':len(frames),'first_frame_seconds':pts[0],'last_frame_seconds':pts[-1],'strictly_increasing_pts':True,'subtitle_cues':len(cues),'all_cues_have_frames':True,'frames_without_official_caption':uncovered,'frames_per_cue':counts,'visual_review':'Selected frames only; full-frame decoding and timestamp checks are automated, not a claim of manually viewing every frame.'}
(V/'frame_validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='frames_per_cue'},ensure_ascii=False))
