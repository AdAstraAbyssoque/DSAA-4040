#!/usr/bin/env python3
"""Render code/terminal snippets to nice PNG cards via freeze + cairosvg."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cairosvg

ROOT = Path(__file__).parent
RAW = ROOT / "assets" / "raw"
FRZ = ROOT / "assets" / "freeze"
FRZ.mkdir(parents=True, exist_ok=True)


@dataclass
class Snippet:
    src: str  # relative to RAW
    out: str  # bare name; .png written into FRZ
    language: str = "bash"
    width: int = 980
    font_size: int = 14
    title: str = "shell"  # window title (used via --config? freeze doesn't expose, ignored)
    background: str = "#0F1420"
    border: str = "#2A2F3A"


SNIPPETS = [
    Snippet("compose_ps.sh",   "term_compose_ps",  width=1080, font_size=13),
    Snippet("curl_health.sh",  "term_health",      width=1000, font_size=14),
    Snippet("redis_cache.sh",  "term_redis",       width=1080, font_size=13),
    Snippet("order_flow.sh",   "term_order",       width=1180, font_size=14),
    Snippet("metrics.sh",      "term_metrics",     width=1080, font_size=13),
    Snippet("psql_books.sh",   "term_psql",        width=1180, font_size=13),

    Snippet("backend_health_books.py", "code_health_books", language="python", width=1100, font_size=13, background="#0E141C"),
    Snippet("backend_place_order.py",  "code_place_order",  language="python", width=1100, font_size=13, background="#0E141C"),
    Snippet("backend_cache.py",        "code_cache",        language="python", width=1100, font_size=13, background="#0E141C"),
    Snippet("vue_setup.js",        "code_vue",      language="javascript", width=1100, font_size=13, background="#0E141C"),

    Snippet("docker_compose.yaml", "code_compose", language="yaml", width=1100, font_size=12, background="#0E141C"),
    Snippet("k8s_postgres.yaml",   "code_postgres",language="yaml", width=1100, font_size=12, background="#0E141C"),
    Snippet("k8s_redis.yaml",      "code_k8s_redis",  language="yaml", width=1100, font_size=12, background="#0E141C"),
    Snippet("k8s_backend.yaml",    "code_k8s_backend",language="yaml", width=1100, font_size=12, background="#0E141C"),
    Snippet("k8s_hpa.yaml",        "code_k8s_hpa",  language="yaml", width=1100, font_size=12, background="#0E141C"),
    Snippet("k8s_ingress.yaml",    "code_k8s_ingress",language="yaml", width=1100, font_size=12, background="#0E141C"),

    Snippet("hey_output.sh",         "term_hey",         width=1100, font_size=13),
    Snippet("kubectl_hpa_watch.sh",  "term_hpa",         width=1180, font_size=13),
    Snippet("kubectl_top_pods.sh",   "term_top_pods",    width=1180, font_size=13),
]


def freeze(snip: Snippet) -> Path:
    src = RAW / snip.src
    if not src.exists():
        raise FileNotFoundError(src)
    svg = FRZ / f"{snip.out}.svg"
    png = FRZ / f"{snip.out}.png"
    cmd = [
        shutil.which("freeze") or "/usr/local/bin/freeze",
        "--output", str(svg),
        "--background", snip.background,
        "--window",
        "--border.radius", "14",
        "--border.width", "1",
        "--border.color", snip.border,
        "--margin", "26",
        "--padding", "26,30",
        "--font.family", "JetBrains Mono",
        "--font.size", str(snip.font_size),
        "--line-height", "1.45",
        "--width", str(snip.width),
        "--language", snip.language,
        "--theme", "dracula",
        str(src),
    ]
    subprocess.run(cmd, stdin=subprocess.DEVNULL, check=True)
    cairosvg.svg2png(url=str(svg), write_to=str(png), scale=2.0)
    return png


def main() -> None:
    for snip in SNIPPETS:
        out = freeze(snip)
        print(f"  {out.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
