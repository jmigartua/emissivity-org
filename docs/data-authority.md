# Data Authority

## Current Decisions

- Institution authority belongs in `sites/final-website/_data/institutions.yml`.
- Conference authority remains page-based for the final site for now.

## Why

The institution map is still a strong candidate for structured-data ownership because:

- it describes relatively stable entities
- it benefits from centralized metadata
- it is already maintained in YAML form in the legacy site

Conferences remain page-based for now because the final site already has detailed
event pages under `events-news/conferences/`, and a second conference authority
in YAML would reintroduce the split-source problem we just isolated.

## Transitional State

- `sites/legacy-site/data/institutions.yml` is now an archival predecessor
  to the final-site authority.
- `sites/legacy-site/data/conferences.yml` remains an archival reference file
  only, until or unless the final site is intentionally redesigned around a
  structured conference data model again.
