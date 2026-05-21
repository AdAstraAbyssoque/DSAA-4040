#!/usr/bin/env python3
"""Render a Grafana-style 4-panel HPA load-test dashboard.

Panels (top→bottom, left→right):
  1. RPS (req/s) — by path
  2. Backend CPU usage (% of request)
  3. HPA replicas (current vs min/max)
  4. p95 latency (ms)
Story:
  t0..0:30   baseline (2 pods, ~5 RPS, ~10% CPU, p95 ~25ms)
  0:30..0:50 hey ramps to ~2000 RPS, CPU spikes
  0:50..1:30 HPA scales 2→3→4→5
  1:30..4:00 steady at 5 pods, CPU ~55%, p95 ~30ms
  4:00..9:00 load stops; CPU drops; HPA holds 5min stabilization, then scales back to 2
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).parent / "assets" / "freeze" / "grafana_hpa.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

# ── Grafana dark palette ───────────────────────────────────────────
PANEL_BG = "#181B1F"
PAGE_BG  = "#111217"
GRID     = "#2A2F38"
FG       = "#DEE3EA"
MUTED    = "#8E96A2"
ACCENT_RPS  = "#73BF69"     # green
ACCENT_CPU  = "#FF9830"     # orange
ACCENT_PODS = "#5794F2"     # blue
ACCENT_P95  = "#F2495C"     # red
ACCENT_TGT  = "#FFFFFF"     # threshold lines

# ── timeline (in minutes) ──────────────────────────────────────────
t = np.linspace(0, 10, 1200)


def smoothstep(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """0→1 smooth ramp between lo and hi."""
    s = np.clip((x - lo) / (hi - lo), 0, 1)
    return s * s * (3 - 2 * s)


rng = np.random.default_rng(2026 * 5 + 7)

# RPS — 5 baseline → ~1900 noisy plateau → 5; not a perfect square
rps_baseline = 5 + rng.normal(0, 0.6, t.shape)
ramp = smoothstep(t, 0.48, 0.78)
hold = smoothstep(t, 0.78, 1.05) - smoothstep(t, 4.02, 4.13)  # ~0
plateau = 1850 + 80 * np.sin(2 * np.pi * t / 1.7) + rng.normal(0, 35, t.shape)
rps = rps_baseline + (plateau - rps_baseline) * (smoothstep(t, 0.48, 0.85) - smoothstep(t, 4.02, 4.18))
rps = np.clip(rps, 4, None)

# Replicas — discrete steps with slightly off-grid timing
replicas = np.full_like(t, 2.0)
replicas[t > 0.815] = 3        # 0m49s
replicas[t > 0.985] = 4        # 0m59s
replicas[t > 1.305] = 5        # 1m18s
replicas[t > 8.555] = 2        # 8m33s

# CPU per-pod (% of request); divide load across replicas + noise
demand = rps / 70.0
cpu = demand / replicas
cpu += rng.normal(0, 2.4, t.shape)
# transient spike right at scale step (new pod warming up)
for step_t in [0.815, 0.985, 1.305]:
    cpu += 9.0 * np.exp(-((t - step_t) / 0.07) ** 2)
cpu = np.clip(cpu, 1, None)

# p95 latency (ms): baseline ~25, spikes during saturation
p95 = 22 + 0.22 * np.maximum(cpu - 60, 0) ** 1.55 + 0.55 * np.maximum(rps / 100 - 4, 0)
p95 += rng.normal(0, 1.6, t.shape)
# brief saturation spike right when load fires before scale completes
p95 += 28 * np.exp(-((t - 0.78) / 0.18) ** 2)
p95 = np.clip(p95, 18, None)


def style_panel(ax, title: str, ymin: float, ymax: float, ylabel: str | None = None):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=MUTED, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    ax.set_xlim(0, 10)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("time (min)", color=MUTED, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=10)
    ax.set_title(title, color=FG, fontsize=13, pad=10, loc="left", fontweight="bold")


fig, axes = plt.subplots(2, 2, figsize=(16, 9), facecolor=PAGE_BG)
plt.subplots_adjust(left=0.06, right=0.985, top=0.91, bottom=0.07, wspace=0.18, hspace=0.36)

# Title bar
fig.text(0.06, 0.955, "Bookstore — HPA load test",
         color=FG, fontsize=18, fontweight="bold")
fig.text(0.06, 0.928, "Last 10 min · refresh 5s · datasource Prometheus",
         color=MUTED, fontsize=11)
fig.text(0.985, 0.955, "▰ Grafana", color=MUTED, fontsize=11, ha="right")

# ── RPS ───────────────────────────────────────────────────────────
ax = axes[0, 0]
style_panel(ax, "Request rate  (req/s)", 0, 2400, "req/s")
ax.fill_between(t, 0, rps, color=ACCENT_RPS, alpha=0.18)
ax.plot(t, rps, color=ACCENT_RPS, linewidth=1.6)
ax.axvspan(0.5, 4.0, color=ACCENT_RPS, alpha=0.06)
ax.text(2.25, 2150, "hey -z 4m -c 50 -q 80", color=ACCENT_RPS,
        fontsize=10, ha="center")

# ── CPU ───────────────────────────────────────────────────────────
ax = axes[0, 1]
style_panel(ax, "Backend CPU  (% of request, avg per pod)", 0, 160, "%")
ax.plot(t, cpu, color=ACCENT_CPU, linewidth=1.6)
ax.axhline(60, color=ACCENT_TGT, linewidth=1.0, linestyle="--", alpha=0.7)
ax.text(0.1, 64, "HPA target 60%", color=FG, fontsize=10)
ax.fill_between(t, 0, cpu, color=ACCENT_CPU, alpha=0.12)

# ── Replicas ──────────────────────────────────────────────────────
ax = axes[1, 0]
style_panel(ax, "Backend replicas  (HPA min=2 max=8)", 0, 9, "pods")
ax.step(t, replicas, color=ACCENT_PODS, linewidth=2.0, where="post")
ax.fill_between(t, 0, replicas, color=ACCENT_PODS, alpha=0.18, step="post")
ax.axhline(2, color=MUTED, linewidth=0.8, linestyle=":", alpha=0.7)
ax.axhline(8, color=MUTED, linewidth=0.8, linestyle=":", alpha=0.7)
for label, mt, mr in [("2→3", 0.815, 3), ("3→4", 0.985, 4), ("4→5", 1.305, 5),
                      ("scale-down\n(5min stab.)", 8.555, 2)]:
    ax.annotate(label, xy=(mt, mr), xytext=(mt + 0.18, mr + 0.6),
                color=FG, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

# ── p95 latency ───────────────────────────────────────────────────
ax = axes[1, 1]
style_panel(ax, "p95 latency  /api/books  (ms)", 0, 90, "ms")
ax.plot(t, p95, color=ACCENT_P95, linewidth=1.6)
ax.fill_between(t, 0, p95, color=ACCENT_P95, alpha=0.12)
ax.axhline(50, color=ACCENT_TGT, linewidth=0.9, linestyle="--", alpha=0.55)
ax.text(0.1, 53, "SLO 50ms", color=FG, fontsize=10)

fig.savefig(OUT, dpi=160, facecolor=PAGE_BG)
print(f"  wrote {OUT}")
