# Patch Notes — Audit Pack Fixes (v1.1)

## 1) PR Template alignment with CODEX_AUTORUN_PROMPT_v1.1.md
- Replaced numbered sections (1–10) with explicit agent markers:
  - [BA], [QA], [SRE], [DEV]
- Kept Risk / Evidence / Learning / Compliance sections, but moved them into a structure that agents and automation can parse reliably.

## 2) SOC2 Audit Pack reference corrections (targeted)
- Corrected incorrect BLUEPRINT section references flagged by review:
  - Feature Squad model → BLUEPRINT — Feature Squad Accountability
  - Role-based agents → BLUEPRINT — Feature Squad Accountability
  - Change risk → BLUEPRINT — Milestone Traceability

Note: These are **targeted fixes** for the specific mismatches reported. If you want, I can run a full sweep to re-map every BLUEPRINT cross-reference against the latest BLUEPRINT.md headings and regenerate the whole table automatically.
