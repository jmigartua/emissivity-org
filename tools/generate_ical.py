#!/usr/bin/env python3
"""generate_ical.py — renders _data/calendar.yml into a valid iCalendar feed
(RFC 5545: CRLF line endings, folded lines, UID + DTSTAMP per event) at
files/ical/emissivity-conferences.ics. Run after editing calendar.yml."""
import datetime as dt
import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "files" / "ical" / "emissivity-conferences.ics"


def esc(s):
    return (str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\n", "\\n"))


def fold(line):
    b = line.encode("utf-8")
    if len(b) <= 75:
        return line
    parts, cur = [], b""
    for ch in line:
        c = ch.encode("utf-8")
        if len(cur) + len(c) > (75 if not parts else 74):
            parts.append(cur.decode("utf-8")); cur = b""
        cur += c
    parts.append(cur.decode("utf-8"))
    return "\r\n ".join(parts)


def main():
    evs = yaml.safe_load((ROOT / "_data" / "calendar.yml").read_text())["events"]
    stamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//emissivity.org//Community calendar//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:emissivity.org — community calendar",
             "X-WR-CALDESC:Conferences\\, workshops and schools on emissivity and thermal radiation"]
    for e in sorted(evs, key=lambda x: str(x["start"])):
        s, t = str(e["start"]).replace("-", ""), str(e["end"]).replace("-", "")
        uid = hashlib.sha1(f'{e["title"]}|{s}'.encode()).hexdigest()[:16] + "@emissivity.org"
        lines += ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{s}", f"DTEND;VALUE=DATE:{t}",
                  f"SUMMARY:{esc(e['title'])}"]
        if e.get("location"):
            lines.append(f"LOCATION:{esc(e['location'])}")
        if e.get("description"):
            lines.append(f"DESCRIPTION:{esc(e['description'])}")
        if e.get("kind"):
            lines.append(f"CATEGORIES:{esc(e['kind'])}")
        if e.get("url"):
            lines.append(f"URL:{e['url']}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(("\r\n".join(fold(l) for l in lines) + "\r\n").encode("utf-8"))
    print(f"ical: {len(evs)} events -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
