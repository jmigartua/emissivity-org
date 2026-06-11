#!/usr/bin/env python3
"""generate_featured.py — renders _data/featured.yml into _featured-band.qmd,
included by the homepage. Run after editing featured.yml, then quarto render."""
import html
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_featured-band.qmd"


def main():
    cfg = yaml.safe_load((ROOT / "_data" / "featured.yml").read_text())["featured"]
    if not cfg.get("enabled"):
        OUT.write_text("")  # band disabled
        print("featured band: disabled (empty include written)")
        return

    links = " ".join(
        f'<a href="{l["url"]}">{html.escape(l["label"])}</a> <span class="sep">·</span>'
        for l in cfg.get("links", [])
    ).rsplit('<span class="sep">·</span>', 1)[0]

    OUT.write_text(f"""```{{=html}}
<section class="featured-band" aria-label="Featured announcement">
  <div class="wrap featured-grid">
    <div class="featured-main">
      <div class="featured-kicker">{html.escape(cfg["kicker"])}</div>
      <h2 class="featured-title">{html.escape(cfg["title"])}
        <span class="featured-sub">{html.escape(cfg.get("subtitle", ""))}</span></h2>
      <p class="featured-body">{html.escape(cfg["body"].strip())}</p>
      <p class="featured-links">{links}</p>
    </div>
    <div class="featured-when">
      <div class="d">{html.escape(cfg["date_text"])}</div>
      <div class="l">{html.escape(cfg["location"])}</div>
      <div class="c mono" id="featured-countdown" data-until="{cfg["countdown_to"]}"></div>
    </div>
  </div>
</section>
<script>
(function () {{
  var el = document.getElementById("featured-countdown");
  if (!el) return;
  var days = Math.ceil((new Date(el.dataset.until) - new Date()) / 864e5);
  if (days > 1) el.textContent = "in " + days + " days";
  else if (days >= 0) el.textContent = "this week";
}})();
</script>
```
""")
    print("featured band: written")


if __name__ == "__main__":
    main()
