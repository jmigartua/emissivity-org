#!/usr/bin/env python3
"""generate_featured.py — renders _data/featured.yml into _featured-band.qmd,
included by the homepage. Run after editing featured.yml, then quarto render.

featured.yml may hold a single announcement (legacy form) or a list of
`variants`, each with optional show_from / show_until dates (YYYY-MM-DD,
inclusive). All variants are emitted; the one valid at build time is visible,
and assets/includes/date-windows.html switches them in the browser between
deploys — so the band changes on the right day without a push.
"""
import datetime as dt
import html
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_featured-band.qmd"
TODAY = dt.date.today()


def active(v):
    f, u = v.get("show_from"), v.get("show_until")
    f = dt.date.fromisoformat(str(f)) if f else None
    u = dt.date.fromisoformat(str(u)) if u else None
    return (f is None or TODAY >= f) and (u is None or TODAY <= u)


def section(v):
    e = html.escape
    links = " ".join(
        f'<a href="{l["url"]}">{e(l["label"])}</a> <span class="sep">·</span>'
        for l in v.get("links", [])
    ).rsplit('<span class="sep">·</span>', 1)[0]
    attrs = ""
    if v.get("show_from"):
        attrs += f' data-show-from="{v["show_from"]}"'
    if v.get("show_until"):
        attrs += f' data-show-until="{v["show_until"]}"'
    hidden = "" if active(v) else " hidden"
    countdown = (f'\n      <div class="c mono featured-countdown" data-until="{v["countdown_to"]}"></div>'
                 if v.get("countdown_to") else
                 (f'\n      <div class="c mono">{e(v["status"])}</div>' if v.get("status") else ""))
    variant = f' featured-band--{v["variant"]}' if v.get("variant") else ""
    return f"""<section class="featured-band{variant}" aria-label="Featured announcement"{attrs}{hidden}>
  <div class="wrap featured-grid">
    <div class="featured-main">
      <div class="featured-kicker">{e(v["kicker"])}</div>
      <h2 class="featured-title">{e(v["title"])}
        <span class="featured-sub">{e(v.get("subtitle", ""))}</span></h2>
      <p class="featured-body">{e(v["body"].strip())}</p>
      <p class="featured-links">{links}</p>
    </div>
    <div class="featured-when">
      <div class="d">{e(v["date_text"])}</div>
      <div class="l">{e(v["location"])}</div>{countdown}
    </div>
  </div>
</section>"""


def main():
    cfg = yaml.safe_load((ROOT / "_data" / "featured.yml").read_text())["featured"]
    if not cfg.get("enabled"):
        OUT.write_text("")  # band disabled
        print("featured band: disabled (empty include written)")
        return
    variants = cfg.get("variants") or [cfg]
    sections = "\n".join(section(v) for v in variants)
    OUT.write_text(f"""```{{=html}}
{sections}
<script>
(function () {{
  document.querySelectorAll(".featured-countdown").forEach(function (el) {{
    var days = Math.ceil((new Date(el.dataset.until) - new Date()) / 864e5);
    if (days > 1) el.textContent = "in " + days + " days";
    else if (days === 1) el.textContent = "tomorrow";
    else if (days === 0) el.textContent = "today";
  }});
}})();
</script>
```
""")
    live = [v["title"] for v in variants if active(v)]
    print(f"featured band: {len(variants)} variant(s) written; visible at build: {live or 'none'}")


if __name__ == "__main__":
    main()
