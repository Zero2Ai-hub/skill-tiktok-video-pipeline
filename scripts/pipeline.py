#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["moviepy>=2.0"]
# ///
"""
TikTok Video Pipeline — full orchestrator
Product image → base video (Runway/Veo) → slowmo stretch → caption overlay → final MP4
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile


SKILLS_BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
RUNWAY_SCRIPT = os.path.join(SKILLS_BASE, "skill-runway-video-gen", "scripts", "generate_video.py")
OVERLAY_SCRIPT = os.path.join(SKILLS_BASE, "skill-tiktok-ads-video", "scripts", "overlay.py")

PRODUCTS_JSON = os.path.join(os.path.dirname(__file__), "..", "config", "products.json")


def load_products():
    with open(PRODUCTS_JSON) as f:
        return json.load(f)


def get_video_duration(path):
    from moviepy import VideoFileClip
    clip = VideoFileClip(path)
    dur = clip.duration
    clip.close()
    return dur


def apply_slowmo(input_path, output_path, target_duration):
    from moviepy import VideoFileClip
    from moviepy import vfx
    print(f"[pipeline] Stretching to {target_duration}s ...")
    clip = VideoFileClip(input_path)
    speed = clip.duration / target_duration
    slow = clip.with_effects([vfx.MultiplySpeed(speed)])
    slow.write_videofile(output_path, fps=30, logger=None)
    clip.close()
    slow.close()
    print(f"[pipeline] Slowmo done → {output_path}")


def run_runway(image, prompt, output, duration=10, ratio="720:1280"):
    print(f"[pipeline] Step 1: Generating video via Runway Gen4 Turbo ...")
    cmd = [
        "uv", "run", RUNWAY_SCRIPT,
        "--image", image,
        "--prompt", prompt,
        "--output", output,
        "--duration", str(duration),
        "--ratio", ratio,
    ]
    result = subprocess.run(cmd, check=True)
    return result.returncode == 0


def run_veo(image, prompt, output):
    """Try Veo via veo3-video-gen skill. Falls back to Runway on 429."""
    veo_script = os.path.join(SKILLS_BASE, "veo3-video-gen", "scripts", "generate.py")
    if not os.path.exists(veo_script):
        print("[pipeline] Veo script not found, falling back to Runway ...")
        return False
    print(f"[pipeline] Step 1: Generating video via Veo ...")
    cmd = ["uv", "run", veo_script, "--image", image, "--prompt", prompt, "--output", output]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        return True
    print("[pipeline] Veo failed (429 or error) — falling back to Runway ...")
    return False


def run_overlay(video, product, style, output):
    print(f"[pipeline] Step 3: Applying caption overlay ({style}) ...")
    cmd = [
        "uv", "run", "--with", "moviepy", "--with", "pillow",
        OVERLAY_SCRIPT,
        "--video", video,
        "--product", product,
        "--style", style,
        "--output", output,
    ]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="TikTok Video Pipeline — full end-to-end")
    parser.add_argument("--product", required=True, choices=["rain_cloud", "hydro_bottle", "mini_cam"])
    parser.add_argument("--image", required=True, help="Source product image path")
    parser.add_argument("--output", required=True, help="Final output MP4 path")
    parser.add_argument("--style", default="subtitle_talk", choices=["subtitle_talk", "phrase_slam", "random"])
    parser.add_argument("--engine", default="auto", choices=["runway", "veo", "auto"])
    parser.add_argument("--extend-to", type=float, default=12.0, dest="extend_to", help="Target duration in seconds (default: 12)")
    parser.add_argument("--prompt", default="", help="Motion description for video generation")
    args = parser.parse_args()

    products = load_products()
    product = products[args.product]
    print(f"\n[pipeline] === TikTok Video Pipeline ===")
    print(f"[pipeline] Product: {product['name']} | Style: {args.style} | Engine: {args.engine}")
    print(f"[pipeline] Target duration: {args.extend_to}s\n")

    with tempfile.TemporaryDirectory() as tmp:
        base_video = os.path.join(tmp, "base.mp4")
        stretched_video = os.path.join(tmp, "stretched.mp4")

        # Step 1 — Generate base video
        prompt = args.prompt or f"product in action, cinematic, smooth motion, {product['name']}"

        if args.engine == "runway":
            run_runway(args.image, prompt, base_video)
        elif args.engine == "veo":
            if not run_veo(args.image, prompt, base_video):
                run_runway(args.image, prompt, base_video)
        else:  # auto
            if not run_veo(args.image, prompt, base_video):
                run_runway(args.image, prompt, base_video)

        if not os.path.exists(base_video):
            print("[pipeline] ERROR: Base video generation failed", file=sys.stderr)
            sys.exit(1)

        # Step 2 — Slowmo stretch if needed
        dur = get_video_duration(base_video)
        print(f"[pipeline] Step 2: Base video duration = {dur:.1f}s")
        if args.extend_to > dur:
            apply_slowmo(base_video, stretched_video, args.extend_to)
            caption_input = stretched_video
        else:
            print(f"[pipeline] No stretch needed ({dur:.1f}s >= {args.extend_to}s)")
            caption_input = base_video

        # Step 3 — Caption overlay
        run_overlay(caption_input, args.product, args.style, args.output)

    print(f"\n[pipeline] ✅ Final video saved: {args.output}")


if __name__ == "__main__":
    main()
