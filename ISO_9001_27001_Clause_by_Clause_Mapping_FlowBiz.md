# 📊 ISO 9001 & ISO/IEC 27001 Clause-by-Clause Mapping
## FlowBiz AI Builder — Audit Reference Table

This document maps **every ISO clause** to concrete implementations,
controls, and evidence within the FlowBiz AI Builder system.

---

# PART A — ISO 9001:2015 (Quality Management System)

## Clause 4 — Context of the Organization
| Clause | Requirement | FlowBiz Implementation | Evidence |
|---|---|---|---|
| 4.1 | Understanding org & context | BLUEPRINT roadmap & scope | BLUEPRINT.md |
| 4.2 | Interested parties | Repo stakeholders, reviewers | PR approvals |
| 4.3 | QMS scope | In-scope repos defined | POLICY.md |
| 4.4 | QMS processes | Gate framework | CONTROLS.md |

## Clause 5 — Leadership
| 5.1 | Leadership & commitment | Mandatory governance | POLICY.md |
| 5.2 | Quality policy | Engineering policy | POLICY.md |
| 5.3 | Roles & authorities | Feature Squad model | BLUEPRINT.md |

## Clause 6 — Planning
| 6.1 | Risks & opportunities | Planning Gate | Gate 0 evidence |
| 6.2 | Quality objectives | Milestone success metrics | BLUEPRINT.md |
| 6.3 | Change planning | One PR = one milestone | PR metadata |

## Clause 7 — Support
| 7.1 | Resources | CI/CD infra | Workflows |
| 7.2 | Competence | Agent role separation | BLUEPRINT.md |
| 7.3 | Awareness | PR templates | PR history |
| 7.4 | Communication | CI notifications | Logs |
| 7.5 | Documented info | Versioned markdown docs | Git history |

## Clause 8 — Operation
| 8.1 | Operational planning | Gate framework | CONTROLS.md |
| 8.2 | Requirements | BA section in PR | PR template |
| 8.3 | Design & dev | Controlled PR workflow | PRs |
| 8.4 | External providers | Template guardrails | BLUEPRINT.md |
| 8.5 | Production | CI / CD | CI logs |
| 8.6 | Release | Production Gate | Deploy evidence |
| 8.7 | Nonconforming outputs | FAIL_SAFE & HOTFIX | Incident PRs |

## Clause 9 — Performance Evaluation
| 9.1 | Monitoring | CI metrics | CI history |
| 9.2 | Internal audit | Audit pack review | Audit reports |
| 9.3 | Management review | Post-run analyzer | Reports |

## Clause 10 — Improvement
| 10.1 | Continual improvement | Learning Gate | Lessons docs |
| 10.2 | Nonconformity & action | HOTFIX PRs | PR history |
| 10.3 | Improvement | Prompt tuning | BLUEPRINT.md |

---

# PART B — ISO/IEC 27001:2022 (Information Security)

## Annex A — Organizational Controls (A.5)
| Clause | Requirement | FlowBiz Implementation | Evidence |
|---|---|---|---|
| A.5.1 | ISMS policies | Security policy | POLICY.md |
| A.5.2 | Roles & responsibilities | Access control model | Repo settings |
| A.5.3 | Segregation of duties | Agent roles | BLUEPRINT.md |

## Annex A — People Controls (A.6)
| A.6.1 | Screening | Repo access control | GitHub logs |
| A.6.2 | Awareness | PR checklist | PR template |
| A.6.3 | Disciplinary | Access revocation | Audit logs |

## Annex A — Physical Controls (A.7)
| A.7.1 | Physical security | Cloud provider scope | Out of scope |
| A.7.2 | Secure areas | N/A | N/A |

## Annex A — Technological Controls (A.8–A.10)
| Clause | Requirement | FlowBiz Implementation | Evidence |
|---|---|---|---|
| A.8.1 | Asset inventory | Evidence registry | EVIDENCE.md |
| A.8.2 | Data classification | Repo-based scope | POLICY.md |
| A.8.3 | Media handling | Artifact retention | CI artifacts |
| A.9.1 | Access control | GitHub RBAC | Repo settings |
| A.9.2 | Authentication | GitHub auth | Audit logs |
| A.10.1 | Cryptography | GitHub secrets | Secrets config |

## Annex A — Operations Security (A.12)
| A.12.1 | Operating procedures | CI workflows | Workflows |
| A.12.2 | Change mgmt | PR process | PR history |
| A.12.3 | Capacity mgmt | CI limits | Metrics |
| A.12.4 | Logging | CI logs | Logs |

## Annex A — System Acquisition (A.14)
| A.14.1 | Secure dev policy | PR policy | POLICY.md |
| A.14.2 | Dev lifecycle | Gate framework | CONTROLS.md |
| A.14.3 | Test data | CI tests | Test logs |

## Annex A — Incident Management (A.16)
| A.16.1 | Incident response | FAIL_SAFE | Incident PR |
| A.16.2 | Improvement | Learning Gate | Lessons |

## Annex A — Business Continuity (A.17)
| A.17.1 | Continuity planning | Rollback automation | Deploy logs |
| A.17.2 | Redundancy | CI reruns | CI history |

## Annex A — Compliance (A.18)
| A.18.1 | Legal compliance | Policy enforcement | POLICY.md |
| A.18.2 | Security review | Audit pack | Audit reports |

---

## Auditor Usage Notes
- Each clause is traceable to a document, control, and evidence
- Sampling PRs validates operational effectiveness
- This table supports ISO 9001 & ISO/IEC 27001 audits directly
