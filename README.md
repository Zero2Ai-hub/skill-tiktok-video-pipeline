# skill-tiktok-video-pipeline

End-to-end TikTok ad video pipeline. Product script → Veo 3 base video → animated caption overlay → audio mix → final MP4. One command, full automation.

## Pipeline

```
script_text + product_id
      ↓
Step 1: Veo 3 base video generation (9:16, ~8s)
      ↓
Step 2: Caption overlay + logo watermark
      ↓
Step 3: Background audio mix
      ↓
final.mp4 (publish-ready)
```

## Usage

```bash
uv run scripts/pipeline.py \
  --product rain_cloud \
  --script "Stop waking everyone up. This humidifier runs whisper-quiet all night." \
  --output final.mp4 \
  --audio bg_music.mp3
```

## Requirements

- Python 3.10+ with `uv`
- `ffmpeg` installed
- `node` (for Veo generation step)
- `GEMINI_API_KEY` env var

## Part of the [Zero2Ai-hub](https://github.com/Zero2Ai-hub) skills ecosystem.
