"""Build the teaser clip shown at the top of the project page.

Each clip is a grid with rows (side camera, wrist camera) and columns (raw MuJoCo
render, optionally the STRIPE-translated observation that the policy receives,
and the real-world rollout) for one task / policy checkpoint / initial
configuration. The STRIPE column is only available for episodes recorded with
``*_turbo_all_steps.mp4``. Sim and real
streams come from the same checkpoint and the same episode index, so they start
from the same initial object configuration.

Usage (from any directory):
    python scripts/make_rollout_videos.py --project /home/tina/Documents/lerobot_pi05
"""

import argparse
import subprocess
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

# (output name, task id, policy token, checkpoint, episode)
CLIPS = [
    ("teaser", "book_shelving", "act", "020000", 8),
]

CELL_W, CELL_H = 384, 288


def build(project: Path, name: str, task: str, policy: str, ckpt: str, episode: int, out_dir: Path) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from real_clips import real_clip  # noqa: E402

    stripe_dir = project / "data_sim_turbo_mujoco" / f"data_sim_eval_{task}_{policy}_{ckpt}" / f"episode_{episode:03d}"
    with_stripe = (stripe_dir / "cam_high_turbo_all_steps.mp4").is_file()
    suffixes = ["", "_turbo_all_steps"] if with_stripe else [""]
    cols = len(suffixes) + 1

    inputs: list[list[str]] = []
    durations: list[float] = []
    for cam in ("cam_high", "cam_wrist"):
        for suffix in suffixes:
            path = stripe_dir / f"{cam}{suffix}.mp4"
            inputs.append(["-i", str(path)])
            durations.append(_duration(path))
        real = real_clip(project, task, policy, ckpt, episode, cam)
        inputs.append(["-i", str(real)])
        durations.append(_duration(real))

    # Pad every stream to the longest one by holding its last frame.
    filters = []
    for i in range(len(inputs)):
        filters.append(
            f"[{i}:v]fps=30,scale={CELL_W}:{CELL_H}:force_original_aspect_ratio=decrease,"
            f"pad={CELL_W}:{CELL_H}:(ow-iw)/2:(oh-ih)/2,setsar=1,tpad=stop_mode=clone:stop_duration=60[v{i}]"
        )
    top = "".join(f"[v{i}]" for i in range(cols))
    bot = "".join(f"[v{i}]" for i in range(cols, 2 * cols))
    filters.append(f"{top}hstack={cols}[top]")
    filters.append(f"{bot}hstack={cols}[bot]")
    filters.append("[top][bot]vstack=2[out]")
    total = max(durations)

    out = out_dir / f"{name}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for args in inputs:
        cmd += args
    cmd += [
        "-filter_complex", ";".join(filters), "-map", "[out]", "-t", f"{total:.3f}",
        "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "-an", str(out),
    ]
    subprocess.run(cmd, check=True)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")


def _duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, required=True, help="lerobot_pi05 repo root")
    parser.add_argument("--out", type=Path, default=SITE_ROOT / "static" / "videos")
    parser.add_argument("--only", default=None, help="Build only this clip name")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for clip in CLIPS:
        if args.only and clip[0] != args.only:
            continue
        build(args.project.resolve(), *clip, out_dir=args.out)


if __name__ == "__main__":
    main()
