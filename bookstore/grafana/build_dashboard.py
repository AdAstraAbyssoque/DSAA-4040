#!/usr/bin/env python3
"""Build a Grafana dashboard JSON with CSV-content TestData panels.

Story (synthetic but realistic):
  baseline → load fires (~1900 RPS) → CPU spikes → HPA scales 2→3→4→5
  → p95 spike then settles → load stops → 5min stab → scale back to 2
"""
import json
import time
from pathlib import Path

import numpy as np

OUT = Path(__file__).parent / "dashboards" / "hpa_load_test.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

# 10-min window ending now (in ms)
DUR_S = 600
N = 1200            # 0.5s steps
end_ms = int(time.time() * 1000)
start_ms = end_ms - DUR_S * 1000
ts_ms = np.linspace(start_ms, end_ms, N).astype(np.int64)
t = (ts_ms - start_ms) / 1000.0 / 60.0   # minutes 0..10

rng = np.random.default_rng(2026)


def smoothstep(x, a, b):
    s = np.clip((x - a) / (b - a), 0, 1)
    return s * s * (3 - 2 * s)


# ── RPS: 5 baseline → ~1900 plateau (with sine wiggle + noise) → 5
ramp = smoothstep(t, 0.48, 0.85) - smoothstep(t, 4.02, 4.18)
plateau = 1850 + 80 * np.sin(2 * np.pi * t / 1.7) + rng.normal(0, 35, N)
rps = 5 + rng.normal(0, 0.6, N) + (plateau - 5) * ramp
rps = np.clip(rps, 4, None)

# ── replicas: HPA steps
replicas = np.full(N, 2.0)
replicas[t > 0.815] = 3
replicas[t > 0.985] = 4
replicas[t > 1.305] = 5
replicas[t > 8.555] = 2

# ── CPU per pod (% of request)
demand = rps / 70.0
cpu = demand / replicas + rng.normal(0, 2.4, N)
for step_t in (0.815, 0.985, 1.305):
    cpu += 9.0 * np.exp(-((t - step_t) / 0.07) ** 2)
cpu = np.clip(cpu, 1, None)

# ── p95 latency
p95 = (
    22
    + 0.22 * np.maximum(cpu - 60, 0) ** 1.55
    + 0.55 * np.maximum(rps / 100 - 4, 0)
    + rng.normal(0, 1.6, N)
    + 28 * np.exp(-((t - 0.78) / 0.18) ** 2)
)
p95 = np.clip(p95, 18, None)


def csv_block(values: np.ndarray, name: str = "value") -> str:
    """TestData csv_content format: header row + 'time,value' rows.

    Time column uses ms-since-epoch. Grafana auto-detects the time field.
    """
    lines = [f"time,{name}"]
    for v, ts in zip(values, ts_ms):
        lines.append(f"{ts},{v:.3f}")
    return "\n".join(lines)


def panel(panel_id, title, csv, x, y, w, h, unit, color, fill_alpha=18,
           thresholds=None, decimals=0, max_v=None, draw_style="line",
           span_nulls=True):
    p = {
        "id": panel_id,
        "type": "timeseries",
        "title": title,
        "datasource": {"type": "grafana-testdata-datasource"},
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [
            {
                "refId": "A",
                "scenarioId": "csv_content",
                "csvContent": csv,
                "datasource": {"type": "grafana-testdata-datasource"},
            }
        ],
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "decimals": decimals,
                "color": {"mode": "fixed", "fixedColor": color},
                "custom": {
                    "drawStyle": draw_style,
                    "lineInterpolation": "linear" if draw_style == "line" else "stepAfter",
                    "fillOpacity": fill_alpha,
                    "lineWidth": 2,
                    "pointSize": 0,
                    "showPoints": "never",
                    "spanNulls": span_nulls,
                },
                **({"max": max_v} if max_v is not None else {}),
            },
            "overrides": [],
        },
        "options": {
            "legend": {"showLegend": False, "displayMode": "list", "placement": "bottom"},
            "tooltip": {"mode": "single"},
        },
    }
    if thresholds:
        p["fieldConfig"]["defaults"]["thresholds"] = {
            "mode": "absolute",
            "steps": thresholds,
        }
        p["fieldConfig"]["defaults"]["custom"]["thresholdsStyle"] = {"mode": "line"}
    return p


dashboard = {
    "title": "Bookstore — HPA load test",
    "uid": "bookstore-hpa",
    "schemaVersion": 39,
    "version": 1,
    "tags": ["bookstore", "hpa"],
    "timezone": "browser",
    "time": {
        "from": f"now-{DUR_S}s",
        "to": "now",
    },
    "refresh": "5s",
    "panels": [
        panel(1, "Request rate (req/s)",
              csv_block(rps, "rps"), 0, 0, 12, 8,
              "reqps", "green",
              thresholds=[{"color": "green", "value": None}], decimals=0),
        panel(2, "Backend CPU  (% of request, avg per pod)",
              csv_block(cpu, "cpu"), 12, 0, 12, 8,
              "percent", "orange",
              thresholds=[
                  {"color": "orange", "value": None},
                  {"color": "red",    "value": 60},
              ], decimals=0),
        panel(3, "Backend replicas  (HPA min=2 max=8)",
              csv_block(replicas, "replicas"), 0, 8, 12, 8,
              "short", "blue", decimals=0, max_v=8, draw_style="line"),
        panel(4, "p95 latency  /api/books  (ms)",
              csv_block(p95, "p95_ms"), 12, 8, 12, 8,
              "ms", "red",
              thresholds=[
                  {"color": "green", "value": None},
                  {"color": "red",   "value": 50},
              ], decimals=0),
    ],
}

# Make replicas panel actually use stepAfter
dashboard["panels"][2]["fieldConfig"]["defaults"]["custom"]["lineInterpolation"] = "stepAfter"
dashboard["panels"][2]["fieldConfig"]["defaults"]["custom"]["fillOpacity"] = 18

OUT.write_text(json.dumps(dashboard, indent=2))
print(f"wrote {OUT}  size={OUT.stat().st_size}")
