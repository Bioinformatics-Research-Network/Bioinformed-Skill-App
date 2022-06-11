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

    # Set the assessment tracker entry to initiated state
    body = {
        "username": "bioresnet",
        "assessment_name": "Test",
        "latest_commit": payload["pull_request"]["head"]["sha"],
        "log": {},
        "status": "Initiated",
    }
    print("Posting update")
    print( f"{bot.CRUD_APP_URL}/api/update")
    print(body)
    response = requests.patch(
        f"{bot.CRUD_APP_URL}/api/update",
        json=body,
    )
    response.raise_for_status()
    print(response.json())

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
    # Get last commit 
    latest_commit = utils.get_last_commit(
        owner=kwarg_dict["owner"],
        repo_name=kwarg_dict["repo_name"],
        access_token=kwarg_dict["access_token"],
    )["sha"]
    # Update the assessment tracker to this commit
    request_url = f"{bot.CRUD_APP_URL}/api/update"
    body = {
        "username": kwarg_dict["sender"],
        "assessment_name": utils.get_assessment_name(payload),
        "latest_commit": latest_commit,
        "log": {"message": "Test message"},
    }
    response = requests.patch(
        request_url,
        json=body,
    )
    # Set checks as passing    
    request_url = f"{const.settings.CRUD_APP_URL}/api/check"
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
    assert response.json()["reviewer_username"] != "bioresnet"
    # Confirm the reviewer is correct
    reviewer_response = utils.get_reviewer(**kwarg_dict)
    assert (
        reviewer_response.json()["users"][0]["login"]
        == response.json()["reviewer_username"]
    )


def test_approve():
    """
    Test the bot's approve command
    """
    # Successful approve command
    payload["comment"]["body"] = "@brnbot approve"
    payload2 = copy.deepcopy(payload)
    payload2["sender"]["login"] = "millerh1"
    response = bot.process_cmd(payload2, access_tokens=access_tokens)
    assert response.status_code == 200
    assert response.json() == {"Assessment Approved": True}
