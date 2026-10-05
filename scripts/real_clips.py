"""Shared real-world clip extraction for the teaser and the baseline grids.

Both page videos that show the same real rollout read the clip produced here, so
they show identical frames at identical playback speed.
"""

import subprocess
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = SITE_ROOT / "build" / "real"

# Real-world playback is slowed by this factor (1.5 -> 0.67x speed) to match the
# pace of the simulated rollouts.
REAL_SLOWDOWN = 1.5


def real_clip(project: Path, task: str, policy: str, ckpt: str, episode: int, cam: str,
              slowdown: float = REAL_SLOWDOWN) -> Path:
    """Return a cached H.264 clip of one real eval episode/camera, slowed by ``slowdown``.

    ``cam`` is ``cam_high`` or ``cam_wrist``.
    """
    out = CACHE_DIR / f"{task}_{policy}_{ckpt}_ep{episode:03d}_{cam}_x{slowdown:g}.mp4"
    if out.is_file():
        return out

    sys.path.insert(0, str(project / "scripts"))
    from make_eval_quad_video import _real_eval_video_path_and_trim  # noqa: E402

    src, ss, dur, _ = _real_eval_video_path_and_trim(project, task, policy, ckpt, episode, cam)
    trim = ["-ss", f"{ss:.4f}", "-t", f"{dur:.4f}"] if ss is not None else []
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *trim, "-i", str(src),
         "-vf", f"setpts={slowdown}*PTS,fps=30", "-c:v", "libx264", "-crf", "16",
         "-pix_fmt", "yuv420p", "-an", str(out)],
        check=True,
    )
    return out
