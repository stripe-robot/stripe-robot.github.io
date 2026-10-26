// Tab groups: mark the clicked button active and run a callback with it.
function bindTabs(groupId, onSelect) {
  const group = document.getElementById(groupId);
  group.addEventListener("click", (e) => {
    const btn = e.target.closest(".tab");
    if (!btn) return;
    group.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b === btn));
    onSelect(btn);
  });
}

// ---------- raw render vs. STRIPE slider ----------
const slider = { task: "book_shelving", cam: "stationary" };

function updateSliderImages() {
  const base = `static/images/slider/${slider.task}_${slider.cam}`;
  document.getElementById("cmp-raw").src = `${base}_raw.png`;
  document.getElementById("cmp-stripe").src = `${base}_stripe.png`;
  document.getElementById("cmp-real").src = `${base}_real.png`;
}

function setSliderPosition(pct) {
  document.getElementById("cmp-top").style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
  document.getElementById("cmp-handle").style.left = `${pct}%`;
}

bindTabs("slider-task-tabs", (btn) => { slider.task = btn.dataset.task; updateSliderImages(); });
bindTabs("slider-cam-tabs", (btn) => { slider.cam = btn.dataset.cam; updateSliderImages(); });
document.getElementById("cmp-range").addEventListener("input", (e) => setSliderPosition(e.target.value));
updateSliderImages();
setSliderPosition(50);

// ---------- rollout videos ----------
// Bump together with the ?v= on the <video> tags in index.html after rebuilding
// videos, so browsers fetch the new files instead of a cached copy.
const VIDEO_VERSION = 2;

const ROLLOUTS = {
  place_mug: "ACT, 20k-step checkpoint.",
  pick_shoe: "&pi;<sub>0.5</sub>, 1k-step checkpoint.",
  shelve_book: "ACT, 20k-step checkpoint.",
  pour_liquid: "Diffusion Policy, 8k-step checkpoint.",
};

function showRollout(clip) {
  const video = document.getElementById("rollout-video");
  video.src = `static/videos/${clip}.mp4?v=${VIDEO_VERSION}`;
  video.play().catch(() => {});
  document.getElementById("rollout-caption").innerHTML = ROLLOUTS[clip];
}

bindTabs("rollout-tabs", (btn) => showRollout(btn.dataset.clip));
document.getElementById("rollout-caption").innerHTML = ROLLOUTS.shelve_book;

// ---------- BibTeX copy ----------
document.getElementById("copy-bib")?.addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  try {
    await navigator.clipboard.writeText(document.getElementById("bibtex").innerText);
    btn.querySelector("span").textContent = "Copied";
  } catch {
    btn.querySelector("span").textContent = "Select to copy";
  }
  setTimeout(() => (btn.querySelector("span").textContent = "Copy"), 1600);
});
