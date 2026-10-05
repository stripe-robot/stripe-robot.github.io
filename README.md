# STRIPE project page

Static project page for *Sim-to-Real Image Translation for Real-to-Sim Policy Evaluation*.
No build step: `index.html` + `static/`.

## Preview locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Deploy on GitHub Pages

1. Create a public repo (this one is `tongmiaoxu/stripe-web`, served at https://tongmiaoxu.github.io/stripe-web/).
2. `git remote add origin git@github.com:<user>/<repo>.git && git push -u origin main`
3. Repo Settings > Pages > Source: *Deploy from a branch*, branch `main`, folder `/ (root)`.

## Updating content

- **Paper / arXiv / Code buttons**: in `index.html`, set each `href` and remove the `disabled` class.
- **Teaser video**: `python scripts/make_rollout_videos.py --project ~/Documents/lerobot_pi05`
  (Shelve Book, ACT 20k, episode 8: raw render | STRIPE | real).
  Its real-world clip and the Shelve Book grid's real column both come from
  `scripts/real_clips.py` (slowed by `REAL_SLOWDOWN` = 1.5, cached in `build/`).
- **Baseline rollout grids** (one per task, 5 columns x 2 cameras):
  `python scripts/make_baseline_grids.py --data-video ~/Documents/lerobot_pi05/data_video --project ~/Documents/lerobot_pi05`.
  Sources and checkpoints are documented in the README of
  [sim2real-rollout-videos](https://github.com/tongmiaoxu/sim2real-rollout-videos);
  per-task captions live in `ROLLOUTS` in `static/js/main.js`.
- **After rebuilding any video**, bump `VIDEO_VERSION` in `static/js/main.js` and the
  `?v=` on the two `<video>` tags in `index.html`, or browsers may keep playing a cached copy.
- **Slider images**: `static/images/slider/<task>_<camera>_{raw,stripe,real}.png`, copied from `lerobot_pi05/viz_site/data/dino_align_ours/` (frame 000015).
- **Figures**: exported from the paper's `images/*.pdf`.

## Visibility

The page is unlisted while the paper is under double-blind review: `robots.txt` and the
`noindex` meta tag in `index.html` keep search engines out. Remove both to make it indexable.
