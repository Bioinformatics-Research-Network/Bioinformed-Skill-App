from app.db.models import (
    Users,
    Reviewers,
    Assessments,
    AssessmentTracker,
    Badges,
)

# Create database with test data
test_users = [
    Users(
        username="millerh1",
        first_name="test",
        last_name="user",
        email="none@none.com",
    ),
    Users(
        username="bioresnet",
        first_name="test2",
        last_name="user2",
        email="none2@none.com",
    ),
    Users(
        username="henrymiller2024",
        first_name="test3",
        last_name="user3",
        email="none3@none.com",
    ),
]

test_reviewers = [
    Reviewers(
        id=1,
        user_id=1,
    ),
    Reviewers(
        id=2,
        user_id=2,
    ),
]

test_assessments = [
    Assessments(
        id=1,
        name="Test",
        description="Test",
        github_org="brn-test-assessment",
        repo_prefix="test-assessment--",
        install_id=25533349,
    ),
]

test_at = [
    AssessmentTracker(
        id=1,
        user_id=1,
        assessment_id=1,
        status="Initiated",
        latest_commit="921839128wj91826w7g",
        repo_owner="brn-test-assessment",
        repo_name="test-assessment--bioresnet",
        pr_number=1,
    ),
]


test_badges = [
    Badges(entityId="OcVxPZEORASs4dBL0h5mOw", name="Test"),
]
