# emissivity.org

Source repository for **[emissivity.org](https://emissivity.org)** — the
common reference point for laboratories and research groups working on the
measurement, modelling, and engineering of the thermal radiative properties
of materials. Hosted at the University of the Basque Country (EHU).

## Stack

Static site, rendered with [Quarto](https://quarto.org). No server-side code.
Deployed continuously by Netlify from this repository (`netlify.toml` →
`tools/netlify-build.sh` installs Quarto in CI, runs the generators, renders).

## Architecture: data drives pages

| Source of truth | Generates |
|---|---|
| `_data/institutions.yml` | Research-map directory, world-map markers (`labs.json`), institution profiles, homepage stats — via `tools/generate_network.py` |
| `_data/images.yml` | Profile photographs + credits (files fetched by `tools/fetch_images.sh`) |
| `_data/featured.yml` | Homepage featured-announcement band — via `tools/generate_featured.py` |
| `_data/calendar.yml` | Conference iCal feed — feeds `tools/generate_ical.py` → `files/ical/emissivity-conferences.ics` |
| `_data/changelog.yml` | What's new page — feeds `tools/generate_changelog.py` → `changelog.qmd` and the "Last updated" stamp in `assets/includes/site-footer.html` |
| `_data/releases.yml` | Release notes for maintainers — feeds `tools/generate_changelog.py` → `about/release-notes.qmd` |
| `training/items/*.qmd` | Training section (courses, tutorials, workshops) — listed by `training/index.qmd` together with `events-news/schools/*.qmd`; template in `training/items/_template.qmd` |
| `events-news/news/*.qmd`, `events-news/conferences/*.qmd` | News/Events pages and the homepage listings (EJS templates in `assets/listings/`) |

Editorial principles: every number exact, dated, and sourced; every
institution profile traceable to public sources (see `network/methodology`);
no stock or AI-generated imagery — institutional photographs with credit only.

## Routine maintenance

```bash
# accept a contribution (arrives via the site forms or email):
python3 tools/new_entry.py news|event|publication

# add/edit an institution: edit _data/institutions.yml, then
python3 tools/generate_network.py

# after ANY addition (page, news, dataset, map entry, feature): add an entry to
# _data/changelog.yml; for a feature or build change also add a release to
# _data/releases.yml; then
python3 tools/generate_changelog.py   # writes changelog.qmd, about/release-notes.qmd, footer stamp

# change the featured announcement: edit _data/featured.yml, then
python3 tools/generate_featured.py

# preview locally
quarto preview

# publish
git add -A && git commit -m "…" && git push   # Netlify deploys automatically
```

## Contributions

Community submissions arrive through the structured forms under
`/contribute/` (Netlify Forms) or by email, and are reviewed by the editorial
board before publication.

## History

This repository was extracted 2026-06-11 from the working repository
`jmigartua/20260102_emissivityorg` (which remains the archive of the legacy
site, design audits, and redesign history).
