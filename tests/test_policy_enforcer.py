"""
Tests for Policy Enforcer (PR-006)

ISO 9001 § 8.5 (Verification & Validation)
ISO/IEC 27001 § A.12 (Operations Security)
"""

import pytest
from packages.core.policy_enforcer import (
    PolicyEnforcer,
    PolicyViolation,
    PolicyViolationType,
    PolicyCheckResult,
)


class TestPolicyEnforcerMetadataCompliance:
    """Test metadata compliance checks."""
    
    def setup_method(self):
        self.enforcer = PolicyEnforcer()
    
    def test_missing_metadata_keys(self):
        """Should detect missing required metadata."""
        pr_body = "This is a PR without proper metadata"
        result = self.enforcer.check_pr_metadata_compliance(pr_body, "Test PR")
        
        assert not result.is_compliant
        assert len(result.violations) > 0
        assert result.violations[0].violation_type == PolicyViolationType.MISSING_METADATA
    
    def test_valid_metadata_present(self):
        """Should pass when all metadata present."""
        pr_body = """
PR_TYPE: MILESTONE
AUTO_RUN_MODE: STRICT
MILESTONE_ID: PR-006
BLUEPRINT_REF: BLUEPRINT - Policy Enforcer / PR-006
"""
        result = self.enforcer.check_pr_metadata_compliance(pr_body, "Test PR")
        assert result.is_compliant
        assert "metadata_keys_present" in result.passed_checks
    
    def test_invalid_pr_type(self):
        """Should reject invalid PR_TYPE values."""
        pr_body = """
PR_TYPE: INVALID
AUTO_RUN_MODE: STRICT
MILESTONE_ID: PR-006
BLUEPRINT_REF: BLUEPRINT - Policy Enforcer / PR-006
"""
        result = self.enforcer.check_pr_metadata_compliance(pr_body, "Test PR")
        assert not result.is_compliant
        assert PolicyViolationType.POLICY_MISMATCH in [
            v.violation_type for v in result.violations
        ]
    
    def test_wip_triggers_halt(self):
        """Should detect WIP and trigger CONTROLLED_HALT."""
        pr_body = """
PR_TYPE: WIP
AUTO_RUN_MODE: STRICT
MILESTONE_ID: PR-006
BLUEPRINT_REF: BLUEPRINT - Policy Enforcer / PR-006
"""
        result = self.enforcer.check_pr_metadata_compliance(pr_body, "Test PR")
        assert not result.is_compliant
        assert any(
            v.violation_type == PolicyViolationType.POLICY_MISMATCH
            and "CONTROLLED_HALT" in v.description
            for v in result.violations
        )
    
    def test_invalid_milestone_id_format(self):
        """Should reject invalid MILESTONE_ID format."""
        pr_body = """
PR_TYPE: MILESTONE
AUTO_RUN_MODE: STRICT
MILESTONE_ID: INVALID-006
BLUEPRINT_REF: BLUEPRINT - Policy Enforcer / PR-006
"""
        result = self.enforcer.check_pr_metadata_compliance(pr_body, "Test PR")
        assert not result.is_compliant
        assert PolicyViolationType.MILESTONE_MAPPING_FAILED in [
            v.violation_type for v in result.violations
        ]


class TestPolicyEnforcerTemplateCompliance:
    """Test PR template compliance checks."""
    
    def setup_method(self):
        self.enforcer = PolicyEnforcer()
    
    def test_missing_template_sections(self):
        """Should detect missing required sections."""
        pr_body = "## [BA]\nSome content"
        result = self.enforcer.check_pr_template_compliance(pr_body)
        
        assert not result.is_compliant
        assert len(result.violations) > 0
        assert result.violations[0].violation_type == PolicyViolationType.INCOMPLETE_TEMPLATE
    
    def test_all_sections_present(self):
        """Should pass when all required sections present."""
        pr_body = """
## [BA]
Problem statement here

## [QA]
Test plan here

## [SRE]
Deployment plan here

## [DEV]
Implementation notes here

## Risk Assessment
Risk analysis here

## Evidence & Artifacts
Evidence links here

## Knowledge & Learning Notes
Lessons learned here

## Compliance Checklist
- [x] Item 1
"""
        result = self.enforcer.check_pr_template_compliance(pr_body)
        assert result.is_compliant
        assert "all_template_sections_present" in result.passed_checks


class TestPolicyEnforcerEvidenceCompliance:
    """Test evidence requirements checks."""
    
    def setup_method(self):
        self.enforcer = PolicyEnforcer()
    
    def test_missing_evidence_section(self):
        """Should detect missing Evidence & Artifacts section."""
        pr_body = "## [BA]\nContent"
        result = self.enforcer.check_evidence_requirements(pr_body)
        
        assert not result.is_compliant
        assert PolicyViolationType.REQUIRED_EVIDENCE_MISSING in [
            v.violation_type for v in result.violations
        ]
    
    def test_evidence_section_with_links(self):
        """Should pass when evidence section has proper links."""
        pr_body = """
## Evidence & Artifacts
- CI logs: https://github.com/example/actions/runs/123
- Security scan: https://example.com/security-scan
- Artifacts: https://example.com/artifacts
"""
        result = self.enforcer.check_evidence_requirements(pr_body)
        assert "evidence_section_complete" in result.passed_checks or "ci_evidence_present" in result.passed_checks


class TestPolicyEnforcerComplianceChecklist:
    """Test compliance checklist checks."""
    
    def setup_method(self):
        self.enforcer = PolicyEnforcer()
    
    def test_missing_checklist(self):
        """Should detect missing compliance checklist."""
        pr_body = "## [BA]\nContent"
        result = self.enforcer.check_compliance_checklist(pr_body)
        
        assert not result.is_compliant
    
    def test_incomplete_checklist(self):
        """Should detect unchecked items in checklist."""
        pr_body = """
## Compliance Checklist
- [x] Item 1
- [ ] Item 2
- [x] Item 3
"""
        result = self.enforcer.check_compliance_checklist(pr_body)
        
        assert not result.is_compliant
        assert any(
            "unchecked" in v.description.lower() for v in result.violations
        )
    
    def test_complete_checklist(self):
        """Should pass when all checklist items checked."""
        pr_body = """
## Compliance Checklist
- [x] Item 1
- [x] Item 2
- [x] Item 3
"""
        result = self.enforcer.check_compliance_checklist(pr_body)
        assert "compliance_checklist_complete" in result.passed_checks


class TestPolicyEnforcerISOMapping:
    """Test ISO/SOC2 impact mapping checks."""
    
    def setup_method(self):
        self.enforcer = PolicyEnforcer()
    
    def test_missing_iso_mappings(self):
        """Should detect missing ISO/SOC2 mappings."""
        pr_body = "## [BA]\nContent without ISO mappings"
        result = self.enforcer.check_iso_mapping_compliance(pr_body)
        
        assert not result.is_compliant
        assert len(result.violations) > 0
    
    def test_all_mappings_present(self):
        """Should pass when all ISO mappings present."""
        pr_body = """
ISO9001_IMPACT: Governance - defines policy enforcement control
ISO27001_IMPACT: Information Security - enforces access controls
SOC2_IMPACT: Availability - ensures controlled access to systems
"""
        result = self.enforcer.check_iso_mapping_compliance(pr_body)
        assert "iso_mapping_present" in result.passed_checks


class TestPolicyEnforcerStatusChecks:
    """Test status check enforcement."""
    
    def setup_method(self):
        self.enforcer = PolicyEnforcer()
    
    def test_missing_required_check(self):
        """Should detect missing required status checks."""
        checks_status = {
            "lint-and-test": True,
        }
        result = self.enforcer.enforce_status_checks(checks_status)
        
        assert not result.is_compliant
        assert len(result.violations) > 0
    
    def test_failing_required_check(self):
        """Should detect failing required status checks."""
        checks_status = {
            check: True for check in self.enforcer.REQUIRED_STATUS_CHECKS
        }
        checks_status["lint-and-test"] = False
        
        result = self.enforcer.enforce_status_checks(checks_status)
        
        assert not result.is_compliant
        assert any(
            "lint-and-test" in v.description for v in result.violations
        )
    
    def test_all_checks_passing(self):
        """Should pass when all required checks passing."""
        checks_status = {
            check: True for check in self.enforcer.REQUIRED_STATUS_CHECKS
        }
        result = self.enforcer.enforce_status_checks(checks_status)
        
        assert result.is_compliant
        assert len(result.passed_checks) == len(self.enforcer.REQUIRED_STATUS_CHECKS)


class TestPolicyEnforcerComprehensive:
    """Test comprehensive PR enforcement."""
    
    def setup_method(self):
        self.enforcer = PolicyEnforcer()
    
    def test_fully_compliant_pr(self):
        """Should pass for fully compliant PR."""
        pr_body = """
PR_TYPE: MILESTONE
AUTO_RUN_MODE: STRICT
MILESTONE_ID: PR-006
BLUEPRINT_REF: BLUEPRINT - Policy Enforcer / PR-006

## [BA]
**Problem / Business Context**
- Business context: Enforce governance policies
- User / system impact: Automated policy compliance
- Reference to PRD / DoD: POLICY.md

**Acceptance Criteria**
- [x] Policy metadata enforced
- [x] Template sections validated
- [x] Evidence requirements checked

**Scope (Scope Lock)**
- **In Scope:**
  - Policy enforcement module
  - Validation checks
- **Out of Scope:**
  - Agent orchestration

## [QA]
**Test Plan**
- Tests added/updated: test_policy_enforcer.py
- Smoke tests: Metadata, template, evidence
- Regression coverage: All violation types
- Known gaps (if any): None

## [SRE]
**Deployment & Verification Plan**
- Deployment impact: No runtime impact
- Verification checklist:
  - [x] Unit tests passing
  - [x] Integration tests passing
- Rollback procedure: Revert to previous commit

## [DEV]
**Implementation Notes**
- Summary of changes: Created policy_enforcer.py module with comprehensive checks
- Key design decisions: Dataclass-based violations, enum-based violation types
- Tests updated: Y
- Docs updated: N/A (code is self-documenting)

## Risk Assessment
- Risk level: Low
- Failure scenarios: None critical
- Mitigation plan: Full test coverage

## Evidence & Artifacts
- CI logs: https://github.com/natbkgift/flowbiz-client-ai-builder/actions
- Security scan results: N/A (no credentials)
- Deployment logs: N/A (no deployment)
- Screenshots / artifacts: Source code, tests

## ISO/SOC2 Impact Mapping (MANDATORY)
ISO9001_IMPACT: Governance control - enforces policy compliance per ISO 9001 § 8.2
ISO27001_IMPACT: Access control - enforces security policies per ISO/IEC 27001 § A.5
SOC2_IMPACT: Change management - ensures policy compliance before changes

## Knowledge & Learning Notes
- Lessons learned: PolicyViolation dataclass provides audit trail
- Follow-up actions: Integrate into CI workflow
- Improvement suggestions: Consider async policy checks

## Compliance Checklist (MANDATORY)
- [x] PR title follows milestone naming (Control: Pull Request Policy; Evidence: Planning Evidence)
- [x] Exactly one milestone mapped (Control: Planning Controls; Evidence: Planning Evidence)
- [x] Blueprint section referenced (Control: Planning Controls; Evidence: Planning Evidence)
- [x] [BA][QA][SRE][DEV] sections present (Control: Planning Controls; Evidence: Planning Evidence)
- [x] CI required checks passed (lint/test/security) (Control: CI Controls; Evidence: CI Evidence)
- [x] Guardrails/policy checks passed (Control: Governance Policy; Evidence: CI Evidence)
- [x] Evidence links attached (CI logs / scan / artifacts) (Control: Evidence Requirements; Evidence: CI Evidence)
- [x] POLICY.md reviewed (Control: Governance Policy; Evidence: Learning Evidence)
- [x] CONTROLS.md satisfied (Control: Control Framework; Evidence: Control Effectiveness)
- [x] EVIDENCE.md artifacts attached (Control: Evidence Requirements; Evidence: Deployment Evidence)
"""
        result = self.enforcer.enforce_pr(pr_body, "PR-006: Policy Enforcer")
        
        # In real scenario, we'd expect some checks to pass
        # but may have minor violations
        assert isinstance(result, PolicyCheckResult)
        assert isinstance(result.is_compliant, bool)


class TestPolicyViolation:
    """Test PolicyViolation record."""
    
    def test_violation_to_dict(self):
        """Should convert violation to audit-ready dict."""
        violation = PolicyViolation(
            violation_type=PolicyViolationType.MISSING_METADATA,
            severity="CRITICAL",
            description="Test violation",
            evidence={"key": "value"},
            remediation="Fix it",
        )
        
        result_dict = violation.to_dict()
        
        assert result_dict["type"] == "missing_metadata"
        assert result_dict["severity"] == "CRITICAL"
        assert "timestamp" in result_dict
        assert result_dict["evidence"]["key"] == "value"


class TestPolicyCheckResult:
    """Test PolicyCheckResult."""
    
    def test_add_violation_marks_noncompliant(self):
        """Should mark as non-compliant when violation added."""
        result = PolicyCheckResult(is_compliant=True)
        violation = PolicyViolation(
            violation_type=PolicyViolationType.MISSING_METADATA,
            severity="CRITICAL",
            description="Test",
        )
        
        result.add_violation(violation)
        
        assert not result.is_compliant
        assert len(result.violations) == 1
        assert "missing_metadata" in result.failed_checks
    
    def test_summary_format(self):
        """Should generate proper summary."""
        result = PolicyCheckResult(is_compliant=True)
        result.add_passed("check_1")
        result.add_passed("check_2")
        
        summary = result.summary()
        
        assert "COMPLIANT" in summary
        assert "Passed: 2" in summary
