"""Tests for knowledge artifact schemas."""

from packages.core.schemas.knowledge import (
    AutomationSuggestion,
    DeployNotes,
    FeatureSummary,
    KnowledgeBundle,
    LessonsLearned,
    TestGaps,
)


def test_feature_summary_creation():
    """Test feature summary creation."""
    summary = FeatureSummary(
        feature_name="Performance optimization",
        squad_id="squad-001",
        pr_number=123,
        summary="Improved database query performance",
        problem_solved="Slow API responses",
        solution_approach="Added indexes and caching",
        key_decisions=["Use Redis for caching", "Add composite indexes"],
    )
    assert summary.feature_name == "Performance optimization"
    assert len(summary.key_decisions) == 2


def test_lessons_learned_creation():
    """Test lessons learned creation."""
    lessons = LessonsLearned(
        feature_name="Performance optimization",
        squad_id="squad-001",
        pr_number=123,
        what_went_well=["Clear requirements", "Good test coverage"],
        what_could_improve=["More profiling upfront"],
        surprises=["Cache invalidation was tricky"],
        recommendations=["Profile before optimizing"],
    )
    assert len(lessons.what_went_well) == 2
    assert len(lessons.recommendations) == 1


def test_test_gaps_creation():
    """Test test gaps creation."""
    gaps = TestGaps(
        feature_name="Performance optimization",
        squad_id="squad-001",
        pr_number=123,
        untested_areas=["Cache invalidation edge cases"],
        flaky_tests=["test_concurrent_access"],
        missing_test_types=["Load tests"],
        recommendations=["Add load testing suite"],
    )
    assert len(gaps.untested_areas) == 1
    assert len(gaps.missing_test_types) == 1


def test_deploy_notes_creation():
    """Test deploy notes creation."""
    notes = DeployNotes(
        feature_name="Performance optimization",
        squad_id="squad-001",
        pr_number=123,
        deployment_steps=["Deploy to staging", "Run smoke tests", "Deploy to prod"],
        environment_changes=["Added REDIS_URL env var"],
        monitoring_setup=["Added response time metric"],
        rollback_tested=True,
    )
    assert len(notes.deployment_steps) == 3
    assert notes.rollback_tested is True


def test_knowledge_bundle_creation():
    """Test knowledge bundle creation."""
    bundle = KnowledgeBundle(
        squad_id="squad-001",
        feature_name="Performance optimization",
        pr_number=123,
        feature_summary=FeatureSummary(
            feature_name="Performance optimization",
            squad_id="squad-001",
            pr_number=123,
            summary="Improved performance",
            problem_solved="Slow responses",
            solution_approach="Caching",
        ),
        lessons_learned=LessonsLearned(
            feature_name="Performance optimization",
            squad_id="squad-001",
            pr_number=123,
        ),
        test_gaps=TestGaps(
            feature_name="Performance optimization", squad_id="squad-001", pr_number=123
        ),
        deploy_notes=DeployNotes(
            feature_name="Performance optimization",
            squad_id="squad-001",
            pr_number=123,
            deployment_steps=["Deploy"],
            rollback_tested=True,
        ),
    )
    assert bundle.squad_id == "squad-001"
    assert bundle.pr_number == 123


def test_automation_suggestion_creation():
    """Test automation suggestion creation."""
    suggestion = AutomationSuggestion(
        task_description="Manual deployment approval",
        times_repeated=5,
        estimated_time_per_occurrence=10,
        automation_approach="Implement auto-approval for low-risk changes",
        priority="high",
    )
    assert suggestion.times_repeated == 5
    assert suggestion.priority == "high"
