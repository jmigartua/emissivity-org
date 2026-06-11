#!/usr/bin/env python3
"""
new_entry.py — maintainer scaffolding for contributions (workflow A).

Turns a reviewed submission (form email or plain email) into a ready
content file. Usage:

  python3 tools/new_entry.py news
  python3 tools/new_entry.py event
  python3 tools/new_entry.py publication

Prompts for the schema fields, writes the .qmd in the right place,
prints the file path. Then: quarto render && deploy.
"""
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = datetime.date.today().isoformat()


def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def ask(label, default=""):
    v = input(f"{label}{f' [{default}]' if default else ''}: ").strip()
    return v or default


def news():
    title = ask("Title")
    desc = ask("One-sentence summary")
    cats = ask("Categories (comma-separated)", "News")
    date = ask("Date", TODAY)
    p = ROOT / "events-news" / "news" / f"{slugify(title)[:60]}.qmd"
    p.write_text(f"""---
title: "{title}"
date: "{date}"
categories: [{cats}]
description: "{desc}"
---

::: {{.page-article}}
# {title}

{desc}

*Emissivity.org Editorial Board · {date}*
:::
""")
    return p


def event():
    name = ask("Event name")
    series = ask("Series (e.g. QIRT)", "")
    start = ask("Start date (YYYY-MM-DD)")
    end = ask("End date (YYYY-MM-DD)", start)
    loc = ask("City, Country")
    url = ask("Official URL")
    desc = ask("One-sentence description")
    year = start[:4]
    sub = f"{series} | {loc}" if series else loc
    p = ROOT / "events-news" / "conferences" / f"{year}-{slugify(name)[:70]}.qmd"
    p.write_text(f"""---
title: "{name}"
subtitle: "{sub}"
date: {start}
description: "{desc}"
url: "{url}"
categories: [{series.lower() if series else 'conference'}]
---

::: {{.page-article}}
# {name}

**Dates:** {start} to {end}
**Location:** {loc}
**Official site:** <{url}>

{desc}
:::
""")
    return p


def publication():
    doi = ask("DOI (e.g. 10.1038/s41597-026-07083-9)")
    title = ask("Title")
    authors = ask("Authors (First Last, First Last)")
    journal = ask("Journal")
    year = ask("Year", TODAY[:4])
    date = ask("Publication date", f"{year}-01-01")
    first_author = slugify(authors.split(",")[0].split()[-1]) if authors else "entry"
    d = ROOT / "publications" / year / first_author
    n = 2
    while d.exists():
        d = ROOT / "publications" / year / f"{first_author}-{n}"
        n += 1
    d.mkdir(parents=True)
    p = d / "index.qmd"
    p.write_text(f"""---
title: "{title}"
date: {date}
author: "{authors}"
description: "{journal} ({year}). doi:{doi}"
categories: [publication]
---

::: {{.page-article}}
# {title}

**Authors:** {authors}
**Journal:** {journal} ({year})
**DOI:** [{doi}](https://doi.org/{doi})
:::
""")
    return p


if __name__ == "__main__":
    kinds = {"news": news, "event": event, "publication": publication}
    if len(sys.argv) != 2 or sys.argv[1] not in kinds:
        sys.exit(f"usage: new_entry.py [{'|'.join(kinds)}]")
    path = kinds[sys.argv[1]]()
    print(f"\nWritten: {path.relative_to(ROOT)}")
    print("Next: quarto render && deploy")
