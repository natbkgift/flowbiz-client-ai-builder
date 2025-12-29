"""
Policy Enforcer — FlowBiz AI Builder
Enforce governance policies defined in POLICY.md and CONTROLS.md

ISO 9001 § 8.2 (Requirements)
ISO/IEC 27001 § A.5 (Governance)
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PolicyViolationType(Enum):
    """Policy violation types — audit-safe classification."""
    MISSING_METADATA = "missing_metadata"
    INCOMPLETE_TEMPLATE = "incomplete_template"
    MILESTONE_MAPPING_FAILED = "milestone_mapping_failed"
    SCOPE_EXCEEDED = "scope_exceeded"
    REQUIRED_EVIDENCE_MISSING = "required_evidence_missing"
    CI_CHECKS_FAILING = "ci_checks_failing"
    APPROVAL_PENDING = "approval_pending"
    NON_COMPLIANT_AUTHOR = "non_compliant_author"
    POLICY_MISMATCH = "policy_mismatch"


@dataclass
class PolicyViolation:
    """Audit-traceable policy violation record."""
    violation_type: PolicyViolationType
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to audit-ready dictionary."""
        return {
            "type": self.violation_type.value,
            "severity": self.severity,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "evidence": self.evidence,
            "remediation": self.remediation,
        }


@dataclass
class PolicyCheckResult:
    """Result of a policy compliance check."""
    is_compliant: bool
    violations: List[PolicyViolation] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    
    def add_violation(self, violation: PolicyViolation) -> None:
        """Add violation and mark non-compliant."""
        self.violations.append(violation)
        self.is_compliant = False
        self.failed_checks.append(violation.violation_type.value)
    
    def add_passed(self, check_name: str) -> None:
        """Record passed check."""
        self.passed_checks.append(check_name)
    
    def summary(self) -> str:
        """Compliance summary for logging."""
        status = "COMPLIANT" if self.is_compliant else "NON-COMPLIANT"
        return (
            f"{status} | "
            f"Passed: {len(self.passed_checks)} | "
            f"Failed: {len(self.failed_checks)} | "
            f"Violations: {len(self.violations)}"
        )


class PolicyEnforcer:
    """
    Enforce governance policies on PRs, branches, and workflows.
    
    Implements:
    - POLICY.md § 4 (Automation Policy)
    - POLICY.md § 5 (Pull Request Policy)
    - CONTROLS.md § 2.1 (Planning Controls)
    """
    
    # Required metadata keys (POLICY.md § 7)
    REQUIRED_METADATA_KEYS = [
        "PR_TYPE",
        "AUTO_RUN_MODE",
        "MILESTONE_ID",
        "BLUEPRINT_REF",
    ]
    
    # Required PR template sections (POLICY.md § 6)
    REQUIRED_SECTIONS = [
        "[BA]",
        "[QA]",
        "[SRE]",
        "[DEV]",
        "Risk Assessment",
        "Evidence & Artifacts",
        "Knowledge & Learning Notes",
        "Compliance Checklist",
    ]
    
    # Required evidence subsections (EVIDENCE.md)
    REQUIRED_EVIDENCE_SUBSECTIONS = [
        "Planning evidence",
        "CI evidence",
        "Deployment evidence",
        "Learning evidence",
    ]
    
    # Required status checks (CODEX_AUTORUN_PROMPT § 3.2)
    REQUIRED_STATUS_CHECKS = [
        "lint-and-test",
        "check-guardrails",
        "enforce-pr-body",
        "evidence-links-present",
        "iso-mapping-confirmed",
        "agent-next-pr-ready",
    ]
    
    def __init__(self):
        self.logger = logger
    
    def check_pr_metadata_compliance(
        self, pr_body: str, pr_title: str
    ) -> PolicyCheckResult:
        """
        Check PR metadata compliance.
        
        POLICY.md § 5: "Every PR must map to exactly one approved milestone"
        POLICY.md § 7: "Mandatory PR metadata (ISO / Audit)"
        """
        result = PolicyCheckResult(is_compliant=True)
        
        # Check metadata keys
        missing_keys = []
        for key in self.REQUIRED_METADATA_KEYS:
            if key not in pr_body:
                missing_keys.append(key)
        
        if missing_keys:
            violation = PolicyViolation(
                violation_type=PolicyViolationType.MISSING_METADATA,
                severity="CRITICAL",
                description=f"Missing required metadata keys: {', '.join(missing_keys)}",
                evidence={"missing_keys": missing_keys, "pr_body_length": len(pr_body)},
                remediation=(
                    f"Add the following keys to PR body: {', '.join(missing_keys)}"
                ),
            )
            result.add_violation(violation)
        else:
            result.add_passed("metadata_keys_present")
        
        # Check PR_TYPE validity
        if "PR_TYPE:" in pr_body:
            pr_type_line = [
                line for line in pr_body.split("\n") if "PR_TYPE:" in line
            ][0]
            pr_type = pr_type_line.split("PR_TYPE:")[-1].strip()
            
            if pr_type not in ["MILESTONE", "WIP", "HOTFIX"]:
                violation = PolicyViolation(
                    violation_type=PolicyViolationType.POLICY_MISMATCH,
                    severity="HIGH",
                    description=f"Invalid PR_TYPE: {pr_type}. Must be MILESTONE|WIP|HOTFIX",
                    evidence={"pr_type": pr_type},
                    remediation="Set PR_TYPE to one of: MILESTONE, WIP, HOTFIX",
                )
                result.add_violation(violation)
            elif pr_type == "WIP":
                violation = PolicyViolation(
                    violation_type=PolicyViolationType.POLICY_MISMATCH,
                    severity="CRITICAL",
                    description="PR_TYPE=WIP triggers CONTROLLED_HALT per POLICY.md",
                    evidence={"pr_type": "WIP"},
                    remediation="Change PR_TYPE to MILESTONE or HOTFIX",
                )
                result.add_violation(violation)
            else:
                result.add_passed("pr_type_valid")
        
        # Check MILESTONE_ID format
        if "MILESTONE_ID:" in pr_body:
            milestone_line = [
                line for line in pr_body.split("\n") if "MILESTONE_ID:" in line
            ][0]
            milestone_id = milestone_line.split("MILESTONE_ID:")[-1].strip()
            
            if not milestone_id.startswith("PR-") or not milestone_id[3:].isdigit():
                violation = PolicyViolation(
                    violation_type=PolicyViolationType.MILESTONE_MAPPING_FAILED,
                    severity="HIGH",
                    description=f"Invalid MILESTONE_ID format: {milestone_id}. Must be PR-###",
                    evidence={"milestone_id": milestone_id},
                    remediation="Set MILESTONE_ID to PR-### format (e.g., PR-006)",
                )
                result.add_violation(violation)
            else:
                result.add_passed("milestone_id_format_valid")
        
        return result
    
    def check_pr_template_compliance(self, pr_body: str) -> PolicyCheckResult:
        """
        Check PR template section compliance.
        
        POLICY.md § 6: "PR WORKING MODEL — MULTI-ROLE EVIDENCE (MANDATORY)"
        """
        result = PolicyCheckResult(is_compliant=True)
        
        missing_sections = []
        for section in self.REQUIRED_SECTIONS:
            if section not in pr_body:
                missing_sections.append(section)
        
        if missing_sections:
            violation = PolicyViolation(
                violation_type=PolicyViolationType.INCOMPLETE_TEMPLATE,
                severity="CRITICAL",
                description=f"Missing required PR template sections: {', '.join(missing_sections)}",
                evidence={"missing_sections": missing_sections},
                remediation=(
                    f"Add the following sections to PR body: {', '.join(missing_sections)}"
                ),
            )
            result.add_violation(violation)
        else:
            result.add_passed("all_template_sections_present")
        
        return result
    
    def check_evidence_requirements(self, pr_body: str) -> PolicyCheckResult:
        """
        Check evidence requirements.
        
        EVIDENCE.md § 3: "Evidence Requirements"
        POLICY.md § 6: "Evidence & Artifacts (MANDATORY)"
        """
        result = PolicyCheckResult(is_compliant=True)
        
        evidence_section_present = "Evidence & Artifacts" in pr_body
        if not evidence_section_present:
            violation = PolicyViolation(
                violation_type=PolicyViolationType.REQUIRED_EVIDENCE_MISSING,
                severity="CRITICAL",
                description="Evidence & Artifacts section missing from PR",
                evidence={"section_found": False},
                remediation="Add Evidence & Artifacts section with links to CI logs, scans, and artifacts",
            )
            result.add_violation(violation)
        else:
            # Check for evidence links
            evidence_lines = pr_body.split("Evidence & Artifacts")[1].split("##")[0]
            has_ci_logs = "CI logs:" in evidence_lines or "ci-run" in evidence_lines
            has_scan_results = "security" in evidence_lines.lower()
            
            if not has_ci_logs:
                violation = PolicyViolation(
                    violation_type=PolicyViolationType.REQUIRED_EVIDENCE_MISSING,
                    severity="HIGH",
                    description="CI logs link missing from Evidence section",
                    evidence={"has_ci_logs": False},
                    remediation="Add link to CI logs in Evidence & Artifacts section",
                )
                result.add_violation(violation)
            else:
                result.add_passed("ci_evidence_present")
            
            if has_ci_logs and has_scan_results:
                result.add_passed("evidence_section_complete")
        
        return result
    
    def check_compliance_checklist(self, pr_body: str) -> PolicyCheckResult:
        """
        Check Compliance Checklist completion.
        
        BLUEPRINT.md § 3: "PR Compliance Requirements"
        """
        result = PolicyCheckResult(is_compliant=True)
        
        if "Compliance Checklist" not in pr_body:
            violation = PolicyViolation(
                violation_type=PolicyViolationType.INCOMPLETE_TEMPLATE,
                severity="CRITICAL",
                description="Compliance Checklist section missing",
                evidence={},
                remediation="Add Compliance Checklist section from PR template",
            )
            result.add_violation(violation)
            return result
        
        # Extract checklist section
        checklist_section = pr_body.split("Compliance Checklist")[1].split("##")[0]
        
        # Count checked items ([ ])
        total_items = checklist_section.count("- [")
        checked_items = checklist_section.count("- [x]") + checklist_section.count("- [X]")
        
        if checked_items < total_items:
            unchecked_count = total_items - checked_items
            violation = PolicyViolation(
                violation_type=PolicyViolationType.INCOMPLETE_TEMPLATE,
                severity="HIGH",
                description=f"Compliance Checklist incomplete: {unchecked_count}/{total_items} items unchecked",
                evidence={"checked_items": checked_items, "total_items": total_items},
                remediation=f"Complete all {unchecked_count} unchecked items in Compliance Checklist",
            )
            result.add_violation(violation)
        else:
            result.add_passed("compliance_checklist_complete")
        
        return result
    
    def check_iso_mapping_compliance(self, pr_body: str) -> PolicyCheckResult:
        """
        Check ISO/SOC2 Impact Mapping.
        
        BLUEPRINT.md § 12: "ISO Mapping Checklist (SUMMARY)"
        """
        result = PolicyCheckResult(is_compliant=True)
        
        required_mappings = [
            "ISO9001_IMPACT:",
            "ISO27001_IMPACT:",
            "SOC2_IMPACT:",
        ]
        
        missing_mappings = []
        for mapping in required_mappings:
            if mapping not in pr_body:
                missing_mappings.append(mapping)
        
        if missing_mappings:
            violation = PolicyViolation(
                violation_type=PolicyViolationType.INCOMPLETE_TEMPLATE,
                severity="HIGH",
                description=f"Missing ISO/SOC2 impact mappings: {', '.join(missing_mappings)}",
                evidence={"missing_mappings": missing_mappings},
                remediation=f"Add these mappings to PR body: {', '.join(missing_mappings)}",
            )
            result.add_violation(violation)
        else:
            result.add_passed("iso_mapping_present")
        
        return result
    
    def enforce_pr(self, pr_body: str, pr_title: str) -> PolicyCheckResult:
        """
        Comprehensive PR enforcement check.
        
        Runs all policy checks in sequence.
        """
        result = PolicyCheckResult(is_compliant=True)
        
        # Run all checks
        checks = [
            self.check_pr_metadata_compliance(pr_body, pr_title),
            self.check_pr_template_compliance(pr_body),
            self.check_evidence_requirements(pr_body),
            self.check_compliance_checklist(pr_body),
            self.check_iso_mapping_compliance(pr_body),
        ]
        
        # Merge results
        for check in checks:
            result.violations.extend(check.violations)
            result.passed_checks.extend(check.passed_checks)
            result.failed_checks.extend(check.failed_checks)
            if not check.is_compliant:
                result.is_compliant = False
        
        return result
    
    def require_status_check(
        self, check_name: str, is_present: bool, is_passing: bool
    ) -> Optional[PolicyViolation]:
        """
        Enforce required status check.
        
        CODEX_AUTORUN_PROMPT § 3.2: "Required status checks (Ruleset: main)"
        """
        if not is_present:
            return PolicyViolation(
                violation_type=PolicyViolationType.CI_CHECKS_FAILING,
                severity="CRITICAL",
                description=f"Required status check not found: {check_name}",
                evidence={"check": check_name, "present": False},
                remediation=f"Configure {check_name} as a required check in branch protection rules",
            )
        
        if not is_passing:
            return PolicyViolation(
                violation_type=PolicyViolationType.CI_CHECKS_FAILING,
                severity="CRITICAL",
                description=f"Required status check failing: {check_name}",
                evidence={"check": check_name, "passing": False},
                remediation=f"Fix the {check_name} check failure and re-run CI",
            )
        
        return None
    
    def enforce_status_checks(
        self, checks_status: Dict[str, bool]
    ) -> PolicyCheckResult:
        """
        Enforce all required status checks.
        
        checks_status: dict of {check_name: is_passing}
        """
        result = PolicyCheckResult(is_compliant=True)
        
        for required_check in self.REQUIRED_STATUS_CHECKS:
            is_present = required_check in checks_status
            is_passing = checks_status.get(required_check, False)
            
            violation = self.require_status_check(
                required_check, is_present, is_passing
            )
            if violation:
                result.add_violation(violation)
            else:
                result.add_passed(f"status_check_{required_check}")
        
        return result
