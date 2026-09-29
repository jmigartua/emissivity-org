#!/usr/bin/env python3
"""generate_hero_figure.py — renders _data/hero-spectrum.yml into
_hero-spectrum.qmd, the measured spectrum shown on the homepage.

The figure is an inline SVG in the site's spectrum style (mono labels, navy
curve, light reference band) so it inherits the page fonts and colours. Every
point drawn is a measured value from the cited EKHI record; nothing is
smoothed or invented. Edit the YAML, rerun, then quarto render.

Usage:
    python3 tools/generate_hero_figure.py            # writes _hero-spectrum.qmd
    python3 tools/generate_hero_figure.py --svg out.svg   # also a standalone SVG
"""
import html
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_data" / "hero-spectrum.yml"
OUT = ROOT / "_hero-spectrum.qmd"

# Geometry shared with the previous hand-drawn figure so the panel size is unchanged.
W, H = 460, 300
X0, X1 = 48, 446          # plot area, px
Y0, Y1 = 22, 230
NAVY, GRID, AXIS, INK, INK_FAINT = "#1b3a6b", "#e8ecf1", "#74808c", "#4a5662", "#74808c"
MONO = "IBM Plex Mono, monospace"


def load():
    d = yaml.safe_load(SRC.read_text())
    xs, ys = d["wavelength_um"], d["emissivity"]
    if len(xs) != len(ys):
        sys.exit(f"hero-spectrum.yml: {len(xs)} wavelengths but {len(ys)} emissivities")
    if any(not 0.0 <= y <= 1.0 for y in ys):
        sys.exit("hero-spectrum.yml: emissivity outside [0, 1]")
    if xs != sorted(xs):
        sys.exit("hero-spectrum.yml: wavelengths must be ascending")
    return d


def svg(d):
    xa, xb = d["x_range_um"]
    px = lambda x: X0 + (x - xa) / (xb - xa) * (X1 - X0)
    py = lambda y: Y1 - y * (Y1 - Y0)            # full 0–1 emissivity axis
    fmt = lambda v: f"{v:.1f}"

    y_ticks = [i / 5 for i in range(6)]          # 0.0 … 1.0
    x_ticks = d["x_ticks_um"]
    xs, ys = d["wavelength_um"], d["emissivity"]
    band = d.get("band")

    o = []
    o.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
             f'aria-label="{html.escape(aria(d))}">')
    # grid
    o.append(f'<g stroke="{GRID}" stroke-width="1">')
    for t in y_ticks[1:]:
        o.append(f'<line x1="{X0}" y1="{py(t):.1f}" x2="{X1}" y2="{py(t):.1f}"/>')
    for t in x_ticks:
        o.append(f'<line x1="{px(t):.1f}" y1="{Y0}" x2="{px(t):.1f}" y2="{Y1}"/>')
    o.append("</g>")
    # axes
    o.append(f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="{AXIS}" stroke-width="1"/>')
    o.append(f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}" stroke="{AXIS}" stroke-width="1"/>')
    # reference band
    if band:
        bx0, bx1 = px(band["from_um"]), px(band["to_um"])
        o.append(f'<rect x="{bx0:.1f}" y="{Y0}" width="{bx1 - bx0:.1f}" height="{Y1 - Y0}" '
                 f'fill="{NAVY}" fill-opacity="0.05"/>')
        o.append(f'<text x="{(bx0 + bx1) / 2:.1f}" y="{Y0 + 16}" font-family="{MONO}" font-size="9" '
                 f'fill="{NAVY}" text-anchor="middle">{html.escape(band["label"])}</text>')
    # measured curve: straight segments between measured points, plus the points
    path = " ".join(f"{'M' if i == 0 else 'L'} {px(x):.1f},{py(y):.1f}" for i, (x, y) in enumerate(zip(xs, ys)))
    o.append(f'<path d="{path}" fill="none" stroke="{NAVY}" stroke-width="1.8" stroke-linejoin="round"/>')
    o.append(f'<g fill="{NAVY}" stroke="#ffffff" stroke-width="0.8">')
    for x, y in zip(xs, ys):
        o.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="1.9"/>')
    o.append("</g>")
    # tick labels
    o.append(f'<g font-family="{MONO}" font-size="9.5" fill="{INK_FAINT}">')
    for t in y_ticks:
        o.append(f'<text x="{X0 - 7}" y="{py(t) + 3:.1f}" text-anchor="end">{fmt(t)}</text>')
    for t in x_ticks:
        o.append(f'<text x="{px(t):.1f}" y="{Y1 + 17}" text-anchor="middle">{fmt(t)}</text>')
    o.append("</g>")
    # axis titles
    o.append(f'<text x="{(X0 + X1) / 2:.0f}" y="270" font-family="{MONO}" font-size="10" fill="{INK}" '
             f'text-anchor="middle">wavelength λ / µm</text>')
    o.append(f'<text x="14" y="{(Y0 + Y1) / 2:.0f}" font-family="{MONO}" font-size="10" fill="{INK}" '
             f'text-anchor="middle" transform="rotate(-90 14 {(Y0 + Y1) / 2:.0f})">emissivity ε</text>')
    # in-plot label: material and temperature
    o.append(f'<text x="{X1 - 6}" y="{Y0 + 16}" font-family="{MONO}" font-size="9.5" fill="{NAVY}" '
             f'text-anchor="end">{html.escape(d["material"])}, {d["temperature_k"]} K</text>')
    o.append("</svg>")
    return "\n".join(o)


def aria(d):
    s = d["source"]
    return (f'{d["property"].capitalize()} of {d["material"]} at {d["temperature_k"]} kelvin, '
            f'measured by {s["author"]} ({s["year"]}), {len(d["wavelength_um"])} points from '
            f'{d["wavelength_um"][0]} to {d["wavelength_um"][-1]} micrometres')


def caption(d):
    e = html.escape
    s = d["source"]
    doi_url = f"https://doi.org/{s['doi']}"
    return (
        f'{e(d["property"].capitalize())} of {e(d["material"])} at {d["temperature_k"]}&nbsp;K '
        f'({e(d["geometry"])}), {len(d["wavelength_um"])} measured points, '
        f'{d["wavelength_um"][0]}–{d["wavelength_um"][-1]}&nbsp;µm.<br/>'
        f'{e(s["author"])}, <em>{e(s["journal"])}</em> {s["volume"]} ({s["year"]}) {e(s["pages"])}, '
        f'<a href="{doi_url}">doi:{e(s["doi"])}</a>. '
        f'Data served by <a href="{e(s["ekhi_url"])}">EKHI</a>, record {e(s["ekhi_record_id"])}.'
    )


def main():
    d = load()
    body = svg(d)
    OUT.write_text(
        "<!-- Generated by tools/generate_hero_figure.py from _data/hero-spectrum.yml. Do not edit. -->\n"
        "```{=html}\n"
        '<figure class="spectrum">\n'
        f"{body}\n"
        f"<figcaption>\n{caption(d)}\n</figcaption>\n"
        "</figure>\n"
        "```\n"
    )
    print(f"wrote {OUT.relative_to(ROOT)} ({len(d['wavelength_um'])} points)")
    if len(sys.argv) == 3 and sys.argv[1] == "--svg":
        Path(sys.argv[2]).write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + body)
        print(f"wrote {sys.argv[2]}")


if __name__ == "__main__":
    main()
