import requests
import copy
from time import sleep

# Set the app environment to "testing" using os
import os
os.environ["APP_ENV"] = "testing"

# Import the modules
from bot import bot, utils, const, auth, schemas

# instantiate the bot
bot = bot.Bot()

# Get the tokens
access_tokens = auth.retrieve_access_tokens()

# Payload for test repo
# https://github.com/Bioinformatics-Research-Network/test-bot/pull/1
payload = {
    "number": 1,
    "pull_request": {
        "url": "https://api.github.com/repos/brn-test-assessment/test--bioresnet/pulls/1",
        "head": {
            "sha": "OIJSADJSAODJASJDOJASD",
        },
    },
    "sender": {
        "login": "bioresnet",
    },
    "comment": {
        "body": "@brnbot hello",
    },
    "installation": {
        "id": 26363998,
    },
    "issue": {
        "number": 1,
        "pull_request": {
            "url": "https://api.github.com/repos/brn-test-assessment/test--bioresnet/pulls/1"
        },
    },
    "repository": {
        "owner": {
            "login": "brn-test-assessment",
        },
        "name": "test--bioresnet",
    },
}


# Create init request
init_request = schemas.InitBotRequest(
    name="Test",
    install_id=26363998,
    repo_prefix="test--",
    github_org="brn-test-assessment",
    latest_release="v0.0.4a",
    template_repo="Skill-Assessment-Tutorial-Python",
    username="bioresnet",
    review_required=True,
)


def test_init_bot():
    """
    Test the bot's init command
    """
    access_token = access_tokens["tokens"][str(init_request.install_id)]

    repo_name = init_request.repo_prefix + init_request.username
    url = f"https://api.github.com/repos/{init_request.github_org}/{repo_name}"
    print(url)
    # Check if repo exists
    response = requests.get(
        url=url,
        headers={"Authorization": f"token {access_token}"},
    )
    if response.status_code == 200:
        print("Repo exists")
        # Delete the repo 
        request_url = f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}"
        sleep(1)
        response = requests.delete(
            request_url,
            headers={"Authorization": f"token {access_token}"},
        )
        response.raise_for_status()
        print("Deleted repo")


    resp = bot.process_init_payload(init_request, access_tokens=access_tokens)

    assert resp


def test_hello():
    """
    Test the bot's hello command
    """
    print(access_tokens)
    print(os.environ["APP_ENV"])
    print(const.settings)
    print(const.token_fp)

    kwarg_dict = bot.parse_comment_payload(payload, access_tokens=access_tokens)
    assert bot.process_cmd(payload, access_tokens=access_tokens)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == f"Hello, @{kwarg_dict['sender']}! 😊"


def test_invalid():
    """
    Test invalid bot command
    """
    payload["comment"]["body"] = "@brnbot invalid"
    kwarg_dict = bot.parse_comment_payload(payload, access_tokens=access_tokens)
    assert bot.process_cmd(payload, access_tokens=access_tokens)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == "Invalid command. Try @brnbot help"


def test_help():
    """
    Test the bot's help command
    """
    payload["comment"]["body"] = "@brnbot help"
    kwarg_dict = bot.parse_comment_payload(payload, access_tokens=access_tokens)
    assert bot.process_cmd(payload, access_tokens=access_tokens)
    response = utils.get_recent_comments(**kwarg_dict)
    assert "Available commands" in response.json()[-1]["body"]



def test_update_on_commit():
    """
    Test the bot's update command on a commit
    """
    
    ## Successful update command
    if utils.check_api_status():
        response = bot.process_commit(payload, access_tokens=access_tokens)
        kwarg_dict = bot.parse_commit_payload(payload, access_tokens=access_tokens)
        assert response.json()
        assert response.status_code == 200
        # Confirm the latest comment is the output of the command
        response2 = utils.get_recent_comments(**kwarg_dict)
        assert kwarg_dict["last_commit"] in response2.json()[-1]["body"]
    else:
        print("API is down. Skipping test.")


def test_check():
    """
    Test the bot's check command
    """

    ## Successful check command
    payload["comment"]["body"] = "@brnbot check"
    assert bot.process_cmd(payload, access_tokens=access_tokens)

    ## Second person on the repo can request a check
    payload2 = copy.deepcopy(payload)
    payload2["sender"]["login"] = "millerh1"
    assert bot.process_cmd(payload2, access_tokens=access_tokens)


def test_review():
    """
    Test the bot's review command
    """

    # Set the assessment to be passing checks using the update command
    kwarg_dict = bot.parse_comment_payload(payload, access_tokens=access_tokens)
    request_url = f"{const.settings.CRUD_APP_URL}/api/check"
    latest_commit = payload['pull_request']['head']['sha']
    body = {"latest_commit": latest_commit, "passed": True}
    print(body)
    print(request_url)
    response = requests.post(
        request_url,
        json=body,
    )
    response.raise_for_status()

    ## Successful review command
    print("Review")
    payload["comment"]["body"] = "@brnbot review"
    kwarg_dict = bot.parse_comment_payload(payload, access_tokens=access_tokens)
    response = bot.process_cmd(payload, access_tokens=access_tokens)
    assert response.status_code == 200
    assert response.json()["reviewer_username"] == "bioresnet"
    # Confirm the reviewer is correct
    reviewer_response = utils.get_reviewer(**kwarg_dict)
    assert (
        reviewer_response.json()["users"][0]["login"]
        == response.json()["reviewer_username"]
    )

    ## Confirm that delete command removes the reviewer
    payload["comment"]["body"] = "@brnbot delete"
    response = bot.process_cmd(payload)
    assert response.status_code == 200
    assert response.json() == {"Entry deleted": True}
    # Confirm no reviewer
    reviewer_response = utils.get_reviewer(**kwarg_dict)
    assert reviewer_response.status_code == 200
    assert reviewer_response.json()["users"] == []


# def test_approve():
#     """
#     Test the bot's approve command
#     """
#     # Initialize the assessment if needed
#     try:
#         payload["comment"]["body"] = "@brnbot delete"
#         bot.process_cmd(payload)
#     except:
#         pass
#     try:
#         payload["comment"]["body"] = "@brnbot init"
#         bot.process_cmd(payload)
#     except:
#         pass

#     # Ensure passing checks
#     payload["comment"]["body"] = "@brnbot check"
#     assert bot.process_cmd(payload)

#     # Ensure it is under review
#     payload["comment"]["body"] = "@brnbot review"
#     response = bot.process_cmd(payload)
#     assert response.status_code == 200

#     # Successful approve command
#     payload["comment"]["body"] = "@brnbot approve"
#     payload2 = copy.deepcopy(payload)
#     payload2["sender"]["login"] = "bioresnet"
#     response = bot.process_cmd(payload2)
#     assert response.status_code == 200
#     assert response.json() == {"Assessment Approved": True}
