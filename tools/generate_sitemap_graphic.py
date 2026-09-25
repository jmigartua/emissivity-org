#!/usr/bin/env python3
"""generate_sitemap_graphic.py — draws "emissivity.org at a glance", the site
map infographic, as an inline SVG, with every figure counted from the site's
own data files at build time (so it never goes stale).

Writes:
  assets/images/site-map.svg   standalone file (downloadable / printable)
  about/_site-map.qmd          the same SVG inline, for the About page

Palette and type follow assets/styles/theme.css (ink, blue, brass; Source
Serif 4 / Source Sans 3 / IBM Plex Mono). Every panel links to its section.
"""
import datetime as dt
import html
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INK, SOFT, FAINT, LINE, TINT, PAPER = "#1d2630", "#4a5662", "#74808c", "#d9dee6", "#f5f7f9", "#ffffff"
BLUE, BLUE2, BRASS = "#1b3a6b", "#2c5d9e", "#9a6f0b"
SERIF = "'Source Serif 4', Georgia, serif"
SANS = "'Source Sans 3', -apple-system, 'Segoe UI', sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, monospace"


def e(s):
    return html.escape(str(s), quote=True)


def fmt(n):
    return f"{n:,}"


# ---------------------------------------------------------------- counts ----
def is_draft(p):
    head = p.read_text(errors="ignore").split("---", 2)
    return len(head) > 2 and re.search(r"^draft:\s*true", head[1], re.M) is not None


def counts():
    inst = yaml.safe_load((ROOT / "_data/institutions.yml").read_text())["institutions"]
    nets = (yaml.safe_load((ROOT / "_data/networks.yml").read_text()) or {}).get("networks", [])
    cal = yaml.safe_load((ROOT / "_data/calendar.yml").read_text())["events"]
    irx = yaml.safe_load((ROOT / "_data/ir-empower.yml").read_text())["editions"]
    data_idx = (ROOT / "data/index.qmd").read_text()
    m = re.search(r"([\d][\d\s,  ]*)\s*curves\s*·\s*(\d+)\s*publications", data_idx)
    curves = int(re.sub(r"\D", "", m.group(1))) if m else None
    pubs_ekhi = int(m.group(2)) if m else None
    libraries = data_idx.count('class="res-row"')
    news = [p for p in (ROOT / "events-news/news").glob("*.qmd") if not is_draft(p)]
    schools = [p for p in (ROOT / "events-news/schools").glob("*.qmd") if not is_draft(p)]
    pubs = [p for p in (ROOT / "publications").glob("*/*/index.qmd") if not is_draft(p)]
    insights = [p for p in (ROOT / "insights/posts").glob("*.qmd") if not is_draft(p)]
    talks26 = sum(1 for ed in irx if ed.get("days") for d in ed["days"] for it in d["items"]
                  if it["kind"] in ("oral", "plenary"))
    return {
        "institutions": len(inst),
        "countries": len({i["country"] for i in inst}),
        "tiers": len({i["tier"] for i in inst}),
        "ecosystems": len({x for i in inst for x in (i.get("ecosystems") or [])}),
        "networks": len(nets),
        "network_names": [n["name"] for n in nets],
        "curves": curves, "ekhi_pubs": pubs_ekhi,
        "external_libraries": max(libraries - 1, 0),
        "calendar": len(cal),
        "schools": len(schools),
        "news": len(news),
        "publications": len(pubs),
        "insights": len(insights),
        "editions": len(irx),
        "talks_latest": talks26,
    }


# ---------------------------------------------------------------- drawing ---
def text(x, y, s, size=14, fill=SOFT, family=SANS, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{extra}>{e(s)}</text>')


def card(x, y, w, h, href, title, number, number_label, lines, accent=BLUE, tag=""):
    out = [f'<a href="{href}" class="sm-card"><g>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{LINE}"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="3" fill="{accent}"/>',
           text(x + 20, y + 32, title, 19, INK, SERIF, 600)]
    if tag:
        out.append(text(x + w - 20, y + 31, tag, 11, FAINT, MONO, 400, "end", ' letter-spacing="0.06em"'))
    yy = y + 32
    if number is not None:
        out.append(text(x + 20, y + 76, number, 36, accent, SERIF, 600))
        out.append(text(x + 20, y + 98, number_label, 13.5, SOFT))
        yy = y + 98
    for ln in lines:
        yy += 21
        out.append(text(x + 20, yy, ln, 13.5, SOFT))
    out.append(text(x + w - 20, y + h - 16, "→", 16, accent, SANS, 600, "end"))
    out.append("</g></a>")
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label="", color=FAINT, lx=None, ly=None, anchor="start"):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.3" '
           f'stroke-dasharray="4 3" marker-end="url(#sm-arrow)"/>']
    if label:
        out.append(text(lx if lx is not None else x1 + 8, ly if ly is not None else (y1 + y2) / 2 + 4,
                        label, 12, FAINT, SANS, 400, anchor, ' font-style="italic"'))
    return "\n".join(out)


def svg(c, today):
    W, H = 1200, 800
    cx = [40, 420, 800]
    cw = 360
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
             f'aria-labelledby="sm-title sm-desc" class="site-map-graphic" style="width:100%;height:auto;display:block">',
             '<title id="sm-title">emissivity.org at a glance</title>',
             f'<desc id="sm-desc">Map of the emissivity.org website: the research map of {c["institutions"]} '
             f'institutions in {c["countries"]} countries and {c["networks"]} research networks; the EKHI open '
             f'database with {fmt(c["curves"] or 0)} curves; publications, insights and reference guides; the '
             f'community calendar, schools and news; the IR-EMPOWER workshop archive; and the contribution forms '
             f'that feed them.</desc>',
             '<defs><marker id="sm-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{FAINT}"/></marker></defs>',
             f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>',
             f'<rect x="0" y="0" width="{W}" height="4" fill="{BLUE}"/>',
             text(40, 58, "emissivity.org", 30, INK, SERIF, 600),
             text(250, 58, "at a glance", 30, FAINT, SERIF, 400),
             text(40, 84, "The common reference point for the thermal radiative properties of materials", 15, SOFT),
             text(W - 40, 58, f"FIGURES AS OF {today.strftime('%d %b %Y').upper()}", 11, FAINT, MONO, 400, "end",
                  ' letter-spacing="0.08em"'),
             text(W - 40, 80, "Every panel opens its section", 12.5, FAINT, SANS, 400, "end", ' font-style="italic"'),
             f'<line x1="40" y1="104" x2="{W-40}" y2="104" stroke="{INK}" stroke-width="1"/>']
    for x, lab in zip(cx, ["WHO WORKS ON IT", "WHAT IS KNOWN", "WHAT IS HAPPENING"]):
        parts.append(text(x, 134, lab, 12, BRASS, MONO, 500, "start", ' letter-spacing="0.1em"'))

    nets = " · ".join(c["network_names"])
    # column 1 — who
    parts.append(card(cx[0], 150, cw, 280, "/network/index.html", "Research map", fmt(c["institutions"]),
                      f"institutions in {c['countries']} countries",
                      [f"{c['tiers']} tiers · {c['ecosystems']} thematic ecosystems",
                       "a source-verified profile for each lab",
                       "published inclusion methodology",
                       f"{c['networks']} research networks:",
                       nets], tag="NETWORK"))
    parts.append(card(cx[0], 470, cw, 150, "/ir-empower/index.html", "IR-EMPOWER workshop",
                      str(c["editions"]), "editions archived: Bilbao 2024 · Würzburg 2026",
                      [f"{c['talks_latest']} talks in 2026, citable as BibTeX"], accent=BRASS, tag="SERIES"))
    parts.append(arrow(cx[0] + 60, 470, cx[0] + 60, 432, "talks count as evidence for the map",
                       lx=cx[0] + 72, ly=455))
    # column 2 — what is known
    parts.append(card(cx[1], 150, cw, 170, "/data/index.html", "EKHI open database",
                      fmt(c["curves"]) if c["curves"] else "EKHI", f"curves from {c['ekhi_pubs']} publications",
                      [f"+ {c['external_libraries']} external spectral libraries indexed"], tag="DATA"))
    parts.append(card(cx[1], 360, cw, 120, "/publications.html", "Publications",
                      str(c["publications"]), f"papers indexed · {c['insights']} insight articles", [],
                      tag="PUBLICATIONS"))
    parts.append(arrow(cx[1] + 60, 322, cx[1] + 60, 358, "every curve traced to its paper",
                       lx=cx[1] + 72, ly=344))
    parts.append(card(cx[1], 500, cw, 120, "/methods/index.html", "Reference guides", None, "",
                      ["what emissivity is · methods & instruments", "standards & protocols · applications"],
                      tag="REFERENCE"))
    # column 3 — what is happening
    parts.append(card(cx[2], 150, cw, 170, "/events-news/conferences.html", "Community calendar",
                      str(c["calendar"]), "conferences, workshops and schools",
                      ["one iCal feed to subscribe to"], tag="EVENTS"))
    parts.append(card(cx[2], 360, cw, 120, "/events-news/schools.html", "Schools & courses",
                      str(c["schools"]), ("training school listed, from Hendaye 2026" if c["schools"] == 1 else "training schools listed, since Hendaye 2026"), [], tag="EVENTS"))
    parts.append(card(cx[2], 500, cw, 120, "/news/index.html", "News", str(c["news"]),
                      "announcements, theses and publications", [], tag="NEWS"))

    # contribute band
    by = 690
    parts.append(f'<a href="/contribute/index.html" class="sm-card"><g>'
                 f'<rect x="40" y="{by}" width="{W-80}" height="70" fill="{TINT}" stroke="{LINE}"/>'
                 f'<rect x="40" y="{by}" width="4" height="70" fill="{BRASS}"/>'
                 + text(64, by + 30, "Contribute", 19, INK, SERIF, 600)
                 + text(64, by + 52, "join the map · submit data · suggest an event · suggest a publication — "
                        "every submission is reviewed and credited", 13.5, SOFT)
                 + text(W - 60, by + 42, "→", 16, BRASS, SANS, 600, "end") + '</g></a>')
    for x, lab in zip(cx, ["join the map", "submit data", "announce events"]):
        parts.append(arrow(x + cw - 60, by - 2, x + cw - 60, 624, lab, lx=x + cw - 72, ly=660, anchor="end"))

    parts.append(text(W / 2, H - 12, "CC BY 4.0 · emissivity.org · hosted at EHU, the University of the Basque Country",
                      11, FAINT, MONO, 400, "middle", ' letter-spacing="0.04em"'))
    parts.append('</svg>')
    return "\n".join(parts)


def main():
    c = counts()
    today = dt.date.today()
    s = svg(c, today)
    (ROOT / "assets/images").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets/images/site-map.svg").write_text(s)
    (ROOT / "about/_site-map.qmd").write_text(
        "```{=html}\n<figure class=\"site-map-figure\">\n" + s +
        "\n<figcaption>The site at a glance. Figures are counted from the site's data files at every "
        "build. <a href=\"/assets/images/site-map.svg\" download>Download the graphic (SVG)</a>.</figcaption>\n"
        "</figure>\n```\n")
    print("site map graphic:", {k: v for k, v in c.items() if k != "network_names"})


if __name__ == "__main__":
    main()
