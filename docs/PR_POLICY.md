# PR Policy

This document outlines the pull request policy for the FlowBiz Client AI Builder project, enforcing the Human-Inspired Engineering Model defined in BLUEPRINT.md.

## Core Principles

1. **One PR = One Milestone**: Each PR must address exactly one milestone from the BLUEPRINT.md PR Index
2. **Evidence-Based Approval**: All PRs must include evidence from all four roles (BA/QA/SRE/DEV)
3. **No Merge Without CI Green**: All PRs must pass CI checks before merge
4. **Scope Lock**: PR scope must not drift from the milestone definition

## PR Structure Requirements

### Title Format
```
PR ###: <milestone name from BLUEPRINT.md>
```

### Required PR Body Sections

Every PR must include ALL four role sections:

#### 1. Feature / Problem [BA]
- Clear problem statement or feature description
- Current state vs. desired state
- Acceptance criteria (from milestone definition)

#### 2. Test Impact [QA]
- Tests added or updated
- Smoke/Regression coverage confirmation
- Test execution results

#### 3. Deploy / Verify Notes [SRE]
- Deployment impact assessment
- Verification steps
- Rollback procedure (if applicable)

#### 4. Automation & Quality [DEV]
- Implementation notes
- Code quality checks passed
- Security scan results
- Local testing confirmation

### Required Metadata

```
MILESTONE_ID: PR ###
BLUEPRINT_REF: Section 11 / PR ### (from BLUEPRINT.md)
```

## PR Workflow

### 1. Opening a PR

- **Always use ready_for_review**: Do NOT open PRs as drafts unless explicitly documenting a pause state
- **Enable auto-merge**: PRs should be configured to auto-merge when all checks pass
- **Link to milestone**: Ensure MILESTONE_ID and BLUEPRINT_REF are present

### 2. CI Checks

All PRs must pass:
- ✅ Linting (ruff)
- ✅ Type checking
- ✅ Unit tests (pytest)
- ✅ Security scans (if applicable)

### 3. Review Process

- **Code review**: Automated or manual review required
- **All comments addressed**: PR cannot merge with unresolved comments
- **Approvals**: At least one approval from a maintainer or AUTO_RUN system

### 4. Merge Requirements

- ✅ All CI checks green
- ✅ All review comments resolved
- ✅ All four role sections complete
- ✅ No merge conflicts
- ✅ Branch up to date with base

### 5. Post-Merge

- **Main must stay green**: If merge breaks main, FAIL_SAFE_HOTFIX_TRIGGER activates
- **Continue to next milestone**: After successful merge + main green, proceed to next PR in index

## Forbidden Actions

### ❌ DO NOT:

1. **Merge without CI green**
2. **Skip any role section** [BA/QA/SRE/DEV]
3. **Drift from milestone scope** - stay within BLUEPRINT.md definition
4. **Open empty PRs** - must have meaningful code changes (except for documented pause states)
5. **Force push** after review starts
6. **Modify BLUEPRINT.md PR Index** without explicit human authorization

## AUTO_RUN Mode Specifics

When operating in AUTO_RUN mode:

### Normal Flow
1. ✅ Work on current unchecked milestone from PR Index
2. ✅ Open PR with complete [BA][QA][SRE][DEV] sections
3. ✅ Set PR to **ready_for_review** (NOT draft)
4. ✅ Enable auto-merge
5. ✅ Wait for CI to complete
6. ✅ Address any CI failures or review comments
7. ✅ After merge + main green → continue to next milestone

### Pause States

#### WAIT STATE
- **When**: Workflows are queued/in_progress
- **Action**: Monitor workflow status, do not proceed until complete

#### HUMAN_APPROVAL_REQUIRED
- **When**: GitHub requires manual approval for workflows (action_required)
- **Action**: Document status, pause ONLY for approval
- **Resume**: Immediately continue after approval granted

### FAIL_SAFE_HOTFIX_TRIGGER
- **When**: Main branch CI fails after merge
- **Action**: Create emergency hotfix PR to restore main to green
- **Priority**: HIGHEST - all other work pauses

## Scope Lock

Once a PR is opened:
- ✅ Bug fixes in existing scope
- ✅ Test improvements for current scope
- ✅ Documentation for current changes
- ❌ New features not in milestone
- ❌ Refactoring unrelated code
- ❌ Adding dependencies not required by milestone

## Checklist for PR Authors

Before opening a PR:
- [ ] Title follows format: `PR ###: <milestone name>`
- [ ] All four role sections [BA][QA][SRE][DEV] complete
- [ ] MILESTONE_ID and BLUEPRINT_REF metadata present
- [ ] Local tests pass (`pytest -q`)
- [ ] Linting passes (`ruff check .`)
- [ ] Health endpoints respond if applicable
- [ ] Docker compose up works if applicable
- [ ] PR is marked **ready_for_review** (not draft)
- [ ] Auto-merge is enabled
- [ ] Changes stay within milestone scope

## Examples

### ✅ Good PR Title
```
PR #9: Foundation + Human Model + PR Policy (Template)
```

### ❌ Bad PR Title
```
Add health endpoints
```

### ✅ Good PR Body
```markdown
## Feature / Problem [BA]
<clear description with acceptance criteria>

## Test Impact [QA]
- [x] Tests added for health endpoints
- [x] All tests pass

## Deploy / Verify Notes [SRE]
- [x] No deployment impact (local testing only)

## Automation & Quality [DEV]
- [x] Linting passes
- [x] Tests pass locally

MILESTONE_ID: PR #9
BLUEPRINT_REF: Section 11 / PR #9
```

### ❌ Bad PR Body
```markdown
Added some health endpoints
```

## Violations & Consequences

| Violation | Consequence |
|-----------|-------------|
| Merge without CI green | Revert + FAIL_SAFE_HOTFIX |
| Missing role section | PR blocked, must update |
| Scope drift | PR rejected, create new PR for correct milestone |
| Empty PR | Close PR, investigate AUTO_RUN blocker |
| Skip milestone order | PR rejected, follow PR Index sequence |

## Questions & Exceptions

- **Q: What if milestone is blocked?**
  - A: Document blocker in PR description, set Status = HUMAN_APPROVAL_REQUIRED

- **Q: Can I combine milestones?**
  - A: No. One PR = One Milestone (scope lock)

- **Q: Emergency hotfix needed?**
  - A: Use FAIL_SAFE_HOTFIX_TRIGGER process, bypass normal flow

- **Q: Milestone definition unclear?**
  - A: Pause, request clarification, do NOT guess

---

**Version**: 1.0  
**Last Updated**: 2025-12-27  
**Authority**: BLUEPRINT.md Section 11 (PR Index)
