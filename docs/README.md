# Server Monitor Documentation

This directory is the single source of truth for project documentation. Keep it organized and up-to-date.

## Structure

- Getting Started
  - docs/getting-started/ (install, quick start, dev env)
  - CUSTOM-DOMAIN-GUIDE.md (custom domain deployment, reverse proxy, mon.go7s.net)
- Architecture
  - ARCHITECTURE.md (system design, components, data flow)
- Features
  - PROJECT_SPECIFICATION.md (feature list and definitions)
  - I18N_GUIDE.md (localization)
- API
  - openapi.yaml (HTTP API)
- Frontend (Next.js)
  - WORKFLOWS.md / WORKFLOWS_EN.md
- Backend (Python)
  - IMPLEMENTATION_SUMMARY.md
- Security
  - SECURITY.md, SECURITY_SCANNING.md
- Deployment & Ops
  - INSTALLER.md, STAGING_CHECKLIST.md, RELEASE_PROCESS.md
  - HTTPS-SETUP.md (at repo root, referenced here)
- Testing & QA
  - TEST_GUIDE.md (root), FULL_REVIEW_GUIDE.md, MANUAL_REVIEW_WORKFLOW_GUIDE.md
- Roadmap & Releases
  - ROADMAP.md (root), CHANGELOG.md (root)

## Rules

- Do not add new root-level Markdown files. Place docs here.
- Update this index when adding/moving docs.
- Prefer consolidating duplicated content into a single canonical document.
- Keep titles, dates, and versions accurate.

## Editing Guidance

- Use concise, actionable language; avoid redundancy.
- Add diagrams where helpful (plantuml/mermaid where supported).
- Link to code (paths, modules) for quick navigation.

## Cleanup Targets (Proposed)

The following root-level files appear overlapping and should be consolidated into docs/ after review:

- README-MULTI-SERVER.md → docs/getting-started/
- ENTERPRISE_ROADMAP.md → merge into ROADMAP.md or docs/roadmap/
- VIETNAMESE_SUMMARY.md → summarize into README.md + docs/release notes
- Legacy summaries (PHASE*, IMPLEMENTATION\_*): merge into IMPLEMENTATION_SUMMARY.md or archive under docs/archive/

Before deletion, migrate any unique content and update links.
