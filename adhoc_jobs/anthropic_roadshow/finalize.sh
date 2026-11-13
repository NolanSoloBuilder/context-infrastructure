#!/bin/zsh
set -eu
cd /Users/xuhao/Documents/Other/context-infrastructure
p=contexts/source_materials/anthropic_roadshow_2026_11_10
mv "$p/anthropic_roadshow.full.mp4" "$p/anthropic_roadshow.mp4"
ffmpeg -hide_banner -loglevel warning -i "$p/anthropic_roadshow.mp4" -i "$p/anthropic_roadshow.zh.srt" -i "$p/anthropic_roadshow.en.srt" -map 0:v -map 0:a -map 1 -map 2 -c copy -c:s mov_text -metadata:s:s:0 language=zho -metadata:s:s:0 handler_name='简体中文' -metadata:s:s:1 language=eng -metadata:s:s:1 handler_name='English' -disposition:s:0 default -disposition:s:1 0 -movflags +faststart "$p/anthropic_roadshow.with_subtitles.mp4"
swift adhoc_jobs/anthropic_roadshow/check_avfoundation.swift "$p/anthropic_roadshow.with_subtitles.mp4" > "$p/verification/avfoundation.json"
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 adhoc_jobs/anthropic_roadshow/verify_frames.py
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 adhoc_jobs/anthropic_roadshow/visual_checks.py
