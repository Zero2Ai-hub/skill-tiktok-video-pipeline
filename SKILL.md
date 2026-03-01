---
name: skill-tiktok-video-pipeline
version: 1.0.0
description: End-to-end TikTok ad video pipeline. Product image → base video (Runway/Veo) → slowmo stretch → animated caption overlay → final MP4. One command, full automation.
metadata:
  openclaw:
    requires: { bins: ["uv"] }
---

# skill-tiktok-video-pipeline

Full pipeline orchestrator for TikTok product ads. Takes a product image and outputs a publish-ready short-form video with animated pill captions.

## Dependencies

Both skills must be installed at the same `skills/` level:
- `skill-runway-video-gen` — video generation
- `skill-tiktok-ads-video` — caption overlay

## Usage

```bash
uv run scripts/pipeline.py \
  --product rain_cloud \
  --image product.jpg \
  --output final.mp4
```

### Full options

```bash
uv run scripts/pipeline.py \
  --product rain_cloud \
  --image product.jpg \
  --output final.mp4 \
  --style subtitle_talk \
  --engine auto \
  --extend-to 12 \
  --prompt "water mist floating, cinematic, slow motion"
```

## Args

| Arg | Default | Description |
|---|---|---|
| `--product` | required | `rain_cloud` \| `hydro_bottle` \| `mini_cam` |
| `--image` | required | Source product image path |
| `--output` | required | Final MP4 output path |
| `--style` | `subtitle_talk` | `subtitle_talk` \| `phrase_slam` \| `random` |
| `--engine` | `auto` | `runway` \| `veo` \| `auto` |
| `--extend-to` | `12` | Target video duration in seconds |
| `--prompt` | auto | Motion description for video generation |

## Products

| Key | Product |
|---|---|
| `rain_cloud` | Rain Cloud Humidifier |
| `hydro_bottle` | Hydrogen Water Bottle |
| `mini_cam` | Mini Clip Camera |

## Engine Decision Tree

```
--engine auto
├── Try Veo first (skill-veo3-video-gen)
│   ├── Success → use Veo output
│   └── 429 / failure → fallback to Runway
└── --engine runway → always use Runway Gen4 Turbo
```

Veo produces higher quality but has per-minute rate limits. Runway is the reliable fallback.

## Pipeline steps

```
Step 1  Generate base video (Runway or Veo)         ~60–120s
Step 2  Stretch to --extend-to seconds at 0.83x     ~10s
Step 3  Apply caption overlay (pill-style)           ~15s
──────────────────────────────────────────────────────────
Output  Final branded MP4 ready to post
```

## Example commands per product

### Rain Cloud Humidifier
```bash
uv run scripts/pipeline.py \
  --product rain_cloud \
  --image rain_cloud.jpg \
  --output rain_cloud_tiktok.mp4 \
  --style subtitle_talk \
  --engine runway
```

### Hydrogen Water Bottle
```bash
uv run scripts/pipeline.py \
  --product hydro_bottle \
  --image hydro_bottle.jpg \
  --output hydro_bottle_tiktok.mp4 \
  --style phrase_slam
```

### Mini Clip Camera
```bash
uv run scripts/pipeline.py \
  --product mini_cam \
  --image mini_cam.jpg \
  --output mini_cam_tiktok.mp4 \
  --style random
```
