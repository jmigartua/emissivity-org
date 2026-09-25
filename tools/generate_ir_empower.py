#!/usr/bin/env python3
"""generate_ir_empower.py — renders _data/ir-empower.yml (single source of truth
for the IR-EMPOWER series) into Quarto includes:

  ir-empower/_editions.qmd          editions table for /ir-empower/
  ir-empower/<year>/_committee.qmd  scientific committee line
  ir-empower/<year>/_programme.qmd  day-by-day programme tables
  ir-empower/<year>/_speakers.qmd   speaker grid (initials; photos when consented)
  ir-empower/<year>/_posters.qmd    posters (consent: public | granted only)

Status labels that depend on the date are emitted as <span data-show-from /
data-show-until> variants; assets/includes/date-windows.html switches them in
the browser, and the variant valid at build time is visible without JS.

Run after editing the YAML, then quarto render (netlify-build.sh runs it).
"""
import datetime as dt
import html
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "_data" / "ir-empower.yml"
TODAY = dt.date.today()
OK = {"public", "granted"}
COMMERCIAL = {"Bruker"}  # the research map lists non-commercial institutions only


def esc(s):
    return html.escape(str(s), quote=True)


def window_active(w, today=TODAY):
    f, u = w.get("from"), w.get("until")
    f = dt.date.fromisoformat(str(f)) if f else None
    u = dt.date.fromisoformat(str(u)) if u else None
    return (f is None or today >= f) and (u is None or today <= u)


def windowed(variants):
    """[{from?, until?, label}] -> inline HTML; only the build-time variant is visible."""
    if len(variants) == 1 and not variants[0].get("from") and not variants[0].get("until"):
        return esc(variants[0]["label"])
    out = []
    for w in variants:
        attrs = ""
        if w.get("from"):
            attrs += f' data-show-from="{w["from"]}"'
        if w.get("until"):
            attrs += f' data-show-until="{w["until"]}"'
        hidden = "" if window_active(w) else " hidden"
        out.append(f'<span class="dw"{attrs}{hidden}>{esc(w["label"])}</span>')
    return "".join(out)


def inst_link(text, net):
    return f"[{text}](/network/{net}.html)" if net else text


def md_cell(s):
    return str(s).replace("|", "\\|")


def initials(name):
    parts = [p for p in name.replace(",", " ").split() if p[0].isupper()]
    return (parts[0][0] + parts[-1][0]) if len(parts) > 1 else name[:2].upper()


def editions_table(cfg):
    rows = ["| Edition | Status | Dates | Venue | Host |", "|---|---|---|---|---|"]
    for e in cfg["editions"]:
        status = windowed(e.get("status_by_date", [{"label": ""}]))
        rows.append(
            f"| **[IR-EMPOWER {e['year']}]({e['page']})** | {status} | {e['dates']} "
            f"| {e['venue_short']} | {e['host_short']} |"
        )
    return "\n".join(rows) + "\n"


def committee(e):
    names = [
        f"[{c['name']}](/network/{c['net']}.html) ({c['inst']}, {c['city']})" if c.get("net")
        else f"{c['name']} ({c['inst']}, {c['city']})"
        for c in e["committee"]
    ]
    return " · ".join(names) + "\n"


def programme(e):
    blocks = []
    for day in e["days"]:
        rows = [f"### {day['label']}", "", "| Time | Session | Speaker |", "|---|---|---|"]
        for it in day["items"]:
            k = it["kind"]
            if k == "session":
                rows.append(f"| | **{md_cell(it['title'])}** | |")
            elif k == "break":
                rows.append(f"| {it['time']} | *{md_cell(it['title'])}* | |")
            else:
                title = md_cell(it["title"])
                if it.get("link"):
                    title = f"[{title}]({it['link']})"
                title = f"**{title}**" + (" *(plenary)*" if k == "plenary" else "")
                who = f"{md_cell(it['speaker'])} · {inst_link(md_cell(it['inst']), it.get('net'))}"
                rows.append(f"| {it['time']} | {title} | {who} |")
        blocks.append("\n".join(rows))
    return "\n\n".join(blocks) + "\n"


def speakers(e):
    def card(it):
        return (f'<div class="speaker-card"><div class="avatar"><span>{esc(initials(it["speaker"]))}</span></div>'
                f'<div class="n">{esc(it["speaker"])}</div><div class="a">{esc(it["inst"])}</div></div>')
    talks = [it for d in e["days"] for it in d["items"] if it["kind"] in ("plenary", "oral")]
    plen = [card(t) for t in talks if t["kind"] == "plenary"]
    orals = [card(t) for t in talks if t["kind"] == "oral"]
    return ("```{=html}\n<h3>Plenary speakers</h3>\n<div class=\"speaker-grid\">\n" + "\n".join(plen)
            + "\n</div>\n<h3>Invited speakers</h3>\n<div class=\"speaker-grid\">\n" + "\n".join(orals)
            + "\n</div>\n```\n")


def posters(e):
    ps = [p for p in e.get("posters", []) if p.get("consent") in OK]
    return "".join(f"- *{p['title']}* — {p['presenter']} ({p['inst']})\n" for p in ps)


def main():
    cfg = yaml.safe_load(DATA.read_text())
    (ROOT / "ir-empower" / "_editions.qmd").write_text(editions_table(cfg))
    for e in cfg["editions"]:
        if "days" not in e:
            continue  # hand-written archive (2024)
        d = ROOT / "ir-empower" / str(e["year"])
        d.mkdir(parents=True, exist_ok=True)
        (d / "_committee.qmd").write_text(committee(e))
        (d / "_programme.qmd").write_text(programme(e))
        (d / "_speakers.qmd").write_text(speakers(e))
        (d / "_posters.qmd").write_text(posters(e))
        # Editorial aid: speaker institutions not yet on the research map.
        missing = sorted({it["inst"] for dd in e["days"] for it in dd["items"]
                          if it["kind"] in ("oral", "plenary") and not it.get("net")
                          and not any(c in it["inst"] for c in COMMERCIAL)})
        print(f"IR-EMPOWER {e['year']}: includes written; research-map candidates: {'; '.join(missing)}")


if __name__ == "__main__":
    main()
