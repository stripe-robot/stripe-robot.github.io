"""Build the per-task baseline comparison clips shown on the project page.

Each clip is a 2x5 grid: rows are the side (stationary) and wrist cameras, columns
are Raw Render, Classical Color Alignment, Pix2Pix, STRIPE and the real robot.
Every column is a separate closed-loop rollout of the same checkpoint from the same
initial configuration. Shorter streams hold their last frame until the longest one
ends.

Sources are the per-baseline videos in ``lerobot_pi05/data_video`` (the same files
published at https://tongmiaoxu.github.io/sim2real-rollout-videos/, see that repo's
README for checkpoints, episodes and real-world playback speeds).

Usage:
    python scripts/make_baseline_grids.py --data-video /home/tina/Documents/lerobot_pi05/data_video \
        --project /home/tina/Documents/lerobot_pi05
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_clips import real_clip  # noqa: E402

SITE_ROOT = Path(__file__).resolve().parent.parent

# output name -> data_video task folder
TASKS = {
    "place_mug": "place_mug",
    "pick_shoe": "pick_shoe",
    "shelve_book": "book_shelving",
    "pour_liquid": "pouring",
}
COLUMNS = ["raw_sim", "kaifeng", "pix2pix", "turbo", "real_world"]
CAMERAS = ["stationary", "wrist"]
CAM_STEMS = {"stationary": "cam_high", "wrist": "cam_wrist"}

# Tasks whose real-world column is re-cut from data_real by real_clips.py (shared
# with the teaser) instead of using the speed-adjusted copy in data_video.
# output name -> (task id, policy token, checkpoint, episode)
REAL_FROM_SOURCE = {
    "shelve_book": ("book_shelving", "act", "020000", 8),
}
CELL_W, CELL_H = 320, 240


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def build(data_video: Path, project: Path, name: str, task: str, out_dir: Path) -> None:
    paths = []
    for cam in CAMERAS:
        for col in COLUMNS:
            if col == "real_world" and name in REAL_FROM_SOURCE:
                paths.append(real_clip(project, *REAL_FROM_SOURCE[name], CAM_STEMS[cam]))
            else:
                paths.append(data_video / task / col / f"{cam}.mp4")
    total = max(duration(p) for p in paths)

    filters = [
        f"[{i}:v]fps=30,scale={CELL_W}:{CELL_H},setsar=1,"
        f"tpad=stop_mode=clone:stop_duration={total:.3f}[v{i}]"
        for i in range(len(paths))
    ]
    n = len(COLUMNS)
    filters.append("".join(f"[v{i}]" for i in range(n)) + f"hstack={n}[top]")
    filters.append("".join(f"[v{i}]" for i in range(n, 2 * n)) + f"hstack={n}[bot]")
    filters.append("[top][bot]vstack=2[out]")

    out = out_dir / f"{name}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p in paths:
        cmd += ["-i", str(p)]
    cmd += [
        "-filter_complex", ";".join(filters), "-map", "[out]", "-t", f"{total:.3f}",
        "-c:v", "libx264", "-preset", "slow", "-crf", "25", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "-an", str(out),
    ]
    subprocess.run(cmd, check=True)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB, {total:.1f}s)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-video", type=Path, required=True, help="lerobot_pi05/data_video")
    parser.add_argument("--project", type=Path, required=True, help="lerobot_pi05 repo root (for data_real)")
    parser.add_argument("--out", type=Path, default=SITE_ROOT / "static" / "videos")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name, task in TASKS.items():
        build(args.data_video.resolve(), args.project.resolve(), name, task, args.out)


if __name__ == "__main__":
    main()
