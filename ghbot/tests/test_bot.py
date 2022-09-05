import random
import string
import requests
import copy

# Set the app environment to "testing" using os
import os

os.environ["APP_ENV"] = "testing"

# Import the modules
from bot import bot, utils, dependencies, auth, schemas
settings = dependencies.get_settings()

seed = random.randint(0, 100000)
print(f"Seed: {seed}")
random.seed(seed)

# instantiate the bot
bot = bot.Bot(settings=settings)

# Get the tokens
access_tokens = auth.retrieve_access_tokens()

# Create init request
init_request = schemas.InitBotRequest(
    name="Test",
    install_id=26363998,
    repo_prefix="test-assessment--",
    github_org="brn-test-assessment",
    latest_release="v0.0.4a",
    template_repo="Skill-Assessment-Tutorial-Python",
    username="bioresnet",
    review_required=True,
)

random.seed(seed)
random_string = "".join(
        random.choice(
            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        for i in range(6)
    )
repo_name = init_request.repo_prefix + random_string + "--" + init_request.username
print(repo_name)

# Payload for test repo
payload = {
    "number": 1,
    "pull_request": {
        "url": f"https://api.github.com/repos/brn-test-assessment/{repo_name}/pulls/1",
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
            "url": f"https://api.github.com/repos/brn-test-assessment/{repo_name}/pulls/1"
        },
    },
    "repository": {
        "owner": {
            "login": "brn-test-assessment",
        },
        "name": repo_name,
    },
}


# Delete request
delete_request = schemas.DeleteBotRequest(
    name="Test",
    username="bioresnet",
    install_id=26363998,
    repo_name=repo_name,
    github_org="brn-test-assessment",
)


def test_init():
    """
    Test the bot's init command
    """

    # Set the assessment tracker entry to initiated state
    # NOTE: This requires that the assessment tracker entry already exists
    #       in the database. It may be necessary to manually create the entry.
    body = {
        "username": "bioresnet",
        "assessment_name": "Test",
        "latest_commit": payload["pull_request"]["head"]["sha"],
        "log": {},
        "status": "Initiated",
    }
    response = requests.patch(
        f"{bot.CRUD_APP_URL}/api/update",
        json=body,
    )
    response.raise_for_status()
    access_token = access_tokens["tokens"][str(init_request.install_id)]
    url = f"https://api.github.com/repos/{init_request.github_org}/{repo_name}"
    # Check if repo exists
    response = requests.get(
        url=url,
        headers={"Authorization": f"token {access_token}"},
    )
    if response.status_code == 200:
        print("Repo exists... deleting")
        assert bot.process_delete_repo(
            delete_request, access_tokens=access_tokens
        )

    resp = bot.process_init_payload(init_request, access_tokens=access_tokens, seed=seed)

    assert resp


## Test utils


def test_get_assessment_name():
    """
    Test the bot's get_assessment_name command
    """
    assessment_name = utils.get_assessment_name(payload)
    # Assessment should be "test" for the test repo
    assert assessment_name == "Test"


def test_is_for_bot():
    """
    Test the bot's forbot command
    """
    assert utils.is_for_bot(payload)
    payload["comment"]["body"] = "@brnbottt"
    assert not utils.is_for_bot(payload)


def test_get_recent_comments():
    """
    Test the bot's post_comment command
    """
    # Success
    kwarg_dict = bot.parse_comment_payload(payload, access_tokens=access_tokens)
    text = "test " + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=20)
    )
    response = utils.post_comment(text=text, **kwarg_dict)
    # Comment should be posted to the test repo
    assert response.status_code == 201
    # Comment should be "test" for the test repo
    assert response.json()["body"] == text
    # Get last comment and check if it is the same as the one we posted
    comments = utils.get_recent_comments(**kwarg_dict)
    assert comments.json()[-1]["body"] == text

    # Confirm ordering of comments is correct
    kwarg_dict = bot.parse_comment_payload(payload, access_tokens=access_tokens)
    text = "test 1 " + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=20)
    )
    utils.post_comment(text=text, **kwarg_dict)
    text2 = "test 2 " + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=20)
    )
    utils.post_comment(text=text2, **kwarg_dict)

    # Get last comment and check if it is the same as the one we posted
    comments = utils.get_recent_comments(**kwarg_dict)
    assert comments.status_code == 200
    assert comments.json()[-1]["body"] == text2
    assert comments.json()[-2]["body"] == text


def test_delete_comment():
    """
    Test the bot's delete_comment command
    """
    # Success
    kwarg_dict = bot.parse_comment_payload(payload, access_tokens=access_tokens)
    text = "del " + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=20)
    )
    response = utils.post_comment(text=text, **kwarg_dict)
    comment_id = response.json()["id"]
    # Check if the comment was posted
    comments = utils.get_comment_by_id(comment_id, **kwarg_dict)
    assert comments.status_code == 404
    # Delete the comment
    response = utils.delete_comment(comment_id, **kwarg_dict)
    assert response.status_code == 204
    # Check if the comment is deleted
    comments = utils.get_comment_by_id(comment_id, **kwarg_dict)
    assert comments.status_code == 404

    # Failure to delete because comment does not exist
    response = utils.delete_comment(comment_id, **kwarg_dict)
    assert response.status_code == 404


## Test bot commands


def test_hello():
    """
    Test the bot's hello command
    """
    print(access_tokens)
    print(os.environ["APP_ENV"])

    payload["comment"]["body"] = "@brnbot hello"
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

    # Successful update command
    response = bot.process_commit(payload, access_tokens=access_tokens)
    kwarg_dict = bot.parse_commit_payload(
        payload, access_tokens=access_tokens
    )
    assert response.json()
    assert response.status_code == 200
    # Confirm the latest comment is the output of the command
    response2 = utils.get_recent_comments(**kwarg_dict)
    assert kwarg_dict["last_commit"] in response2.json()[-1]["body"]


def test_check():
    """
    Test the bot's check command
    """

    # Successful check command
    payload["comment"]["body"] = "@brnbot check"
    assert bot.process_cmd(payload, access_tokens=access_tokens)

    # Second person on the repo can request a check
    payload2 = copy.deepcopy(payload)
    payload2["sender"]["login"] = "brnbot2"
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
    request_url = f"{settings.CRUD_APP_URL}/api/check"
    body = {"latest_commit": latest_commit, "passed": True}
    print(body)
    print(request_url)
    response = requests.post(
        request_url,
        json=body,
    )
    response.raise_for_status()

    # Successful review command
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
