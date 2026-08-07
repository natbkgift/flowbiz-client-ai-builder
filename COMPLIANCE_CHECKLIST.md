# Compliance Checklist (Canonical v11)

> Derived from `POLICY.md`, `CONTROLS.md`, `BLUEPRINT.md`, and `EVIDENCE.md`.

- [ ] PR title follows milestone naming (Planning Evidence)
- [ ] Exactly one milestone / scope lock mapped (Planning Control)
- [ ] Blueprint semantic reference present (Planning Control)
- [ ] `[BA][QA][SRE][DEV]` evidence sections present where applicable (Planning Evidence)
- [ ] Exact repository and commit SHA resolved (Source Integrity)
- [ ] FlowBiz Runner required checks passed for the exact SHA (CI Control)
- [ ] Security/dependency checks passed where applicable (CI Evidence)
- [ ] Artifact checksum / release evidence attached when a release artifact is produced (CI/Deployment Evidence)
- [ ] Deploy/verify/rollback plan exists for runtime-impacting changes (Production Control)
- [ ] High-risk approval present when required (Approval Control)
- [ ] No production secrets are exposed to Runner jobs (Security Control)
- [ ] No unrestricted AI shell/SSH path is introduced (Security Control)
- [ ] `POLICY.md` reviewed (Governance Control)
- [ ] `CONTROLS.md` satisfied (Control Effectiveness)
- [ ] `EVIDENCE.md` artifacts attached/finalized (Evidence Requirement)

Legacy GitHub Actions checks may be supplemental during migration, but they are not the authoritative v11 CI gate and must not be the only evidence source.
