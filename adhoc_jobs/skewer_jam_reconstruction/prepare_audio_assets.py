"""Original audio in explicit MPEG byte banks for WebAudio (no media URL or network).
Keep original duration and transients; SFX 44.1 kHz/96 kbps, BGM 24 kHz/64 kbps.
"""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).parent
out=Path('/Users/xuhao/Documents/Other/xhs-minitools/packages/skewer-jam/src/assets')
clips={'tap':'sfx_tap_item','button':'sfx_tap_button','receive':'sfx_box_receive','cache':'sfx_cache_receive','complete':'sfx_box_complete','win':'sfx_win_game','lose':'sfx_lose_game','shuffle':'sfx_booster_wand','extra':'sfx_booster_tray','magnet':'sfx_booster_magnet','music':'music_skewer_ingame'}
groups={'effects':{},'music':{}};manifest=[]
for key,name in clips.items():
 source=root/'evidence/audio'/(name+'.wav');rate=24000 if key=='music' else 44100
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-ac','1','-ar',str(rate),'-codec:a','libmp3lame','-b:a','64k' if key=='music' else '96k','-write_xing','0','-id3v2_version','0','-f','mp3','pipe:1'])
 groups['music' if key=='music' else 'effects'][key]={'codec':'audio/mpeg','bytes':list(raw)}
 manifest.append({'event':key,'source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sampleRate':rate,'encodedBytes':len(raw)})
for group,bank in groups.items():
 p=out/('audio-'+group+'.js');p.write_text('// Explicit MPEG audio asset bytes; decoded once with Web Audio.\nwindow.SkewerAudioBanks=window.SkewerAudioBanks||{};window.SkewerAudioBanks.'+group+'='+json.dumps(bank,separators=(',',':'))+';\n');print(p.name,p.stat().st_size)
(out/'audio-bank.js').unlink(missing_ok=True)
(root/'evidence/audio_quality.json').write_text(json.dumps(manifest,indent=2))
