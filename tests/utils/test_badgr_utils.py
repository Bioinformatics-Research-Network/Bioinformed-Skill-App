from app.utils import badgr_utils
from app.config import badgr_config_test

# # TODO: Should this go here?
# # Get the bearer token
# brearer_token = badgr_utils.get_bearer_token(badgr_config_test)


# def test_issue_badge():
#     """
#     Test the issue_badge function
#     """

#     # Issue the badge
#     issue_badge_response = badgr_utils.issue_badge(
#         user_email="tests@bioresnet.org",
#         user_first="Test",
#         user_last="User",
#         assessment_name="Python Programming I",
#         bearer_token=brearer_token,
#         config=badgr_config_test,
#     )

#     # Wrangle the response
#     recip = issue_badge_response.json()["result"][0]["recipient"]

#     # Assert that the badge was issued correctly
#     assert issue_badge_response.status_code == 201
#     assert issue_badge_response.json()["status"]["success"]
#     assert recip["plaintextIdentity"] == "tests@bioresnet.org"


# def test_get_assertion():
#     """
#     Test the get_badge_json function
#     """

#     # Get the badge JSON
#     badge_assertion = badgr_utils.get_assertion(
#         assessment_name="Python Programming I",
#         user_email="tests@bioresnet.org",
#         bearer_token=brearer_token,
#         config=badgr_config_test,
#     )

#     # Wrangle the badge JSON
#     result = badge_assertion.json()["result"]
#     recip = result[0]["recipient"]["plaintextIdentity"]
#     assessment_name = result[0]["badgeclass"]

#     # Assert that the badge JSON is correct
#     assert badge_assertion.status_code == 200
#     assert badge_assertion.json()["status"]["success"]
#     assert recip == "tests@bioresnet.org"
#     assert assessment_name == badgr_config_test["BADGE_IDs"]["Python Programming I"]


# def test_get_all_assertions():
#     """
#     Test the get_all_assertions function
#     """

#     # Get the badge JSON
#     badge_assertions = badgr_utils.get_all_assertions(
#         assessment_name="Python Programming I",
#         bearer_token=brearer_token,
#         config=badgr_config_test,
#     )

#     # Wrangle the badge JSON
#     print(badge_assertions.json())
#     result = badge_assertions.json()["result"]
#     recip = result[0]["recipient"]["plaintextIdentity"]
#     assessment_name = result[0]["badgeclass"]

#     # Assert that the badge JSON is correct
#     assert badge_assertions.status_code == 200
#     assert badge_assertions.json()["status"]["success"]

