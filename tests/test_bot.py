from distutils.command.config import config
import pytest
import requests
import copy
from bot import bot, utils, const

# instantiate the bot
bot = bot.Bot()

# Payload for test repo
# https://github.com/Bioinformatics-Research-Network/test-bot/pull/1
payload = {
    "number": 1,
    "pull_request": {
        "url": "https://api.github.com/repos/brn-test-assessment/test-millerh1/pulls/1",
        "head": {
            "sha": "OIJSADJSAODJASJDOJASD",
        },
    },
    "sender": {
        "login": "millerh1",
    },
    "comment": {
        "body": "@brnbot hello",
    },
    "installation": {
        "id": 25533349,
    },
    "issue": {
        "number": 1,
        "pull_request": {
            "url": "https://api.github.com/repos/brn-test-assessment/test-millerh1/pulls/1"
        },
    },
    "repository": {
        "owner": {
            "login": "brn-test-assessment",
        },
        "name": "test-millerh1",
    },
}


def test_hello():
    """
    Test the bot's hello command
    """
    kwarg_dict = bot.parse_comment_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == f"Hello, @{kwarg_dict['sender']}! 😊"


def test_invalid():
    """
    Test invalid bot command
    """
    payload["comment"]["body"] = "@brnbot invalid"
    kwarg_dict = bot.parse_comment_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == "Invalid command. Try @brnbot help"


def test_help():
    """
    Test the bot's help command
    """
    payload["comment"]["body"] = "@brnbot help"
    kwarg_dict = bot.parse_comment_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == "Available commands: \n" + "\n".join(bot.cmds)


def test_view():
    """
    Test the bot's view command
    """

    # Initialize the assessment if needed
    try:
        payload["comment"]["body"] = "@brnbot init"
        bot.process_cmd(payload)
    except:
        pass

    ## Successful view command
    payload["comment"]["body"] = "@brnbot view"
    response = bot.process_cmd(payload)
    assert response.status_code == 200
    assert response.json()["user_id"] == 3
    # Confirm the latest comment is the output of the view command
    response2 = utils.get_recent_comments(**bot.parse_comment_payload(payload))
    assert response.json()["latest_commit"] in response2.json()[-1]["body"]
    # Confirm the sender is correct
    assert payload["sender"]["login"] in response2.json()[-1]["body"]


def test_update():
    """
    Test the bot's update command
    """

    # Initialize the assessment if needed
    try:
        payload["comment"]["body"] = "@brnbot init"
        bot.process_cmd(payload)
    except:
        pass

    ## Successful update command
    payload["comment"]["body"] = "@brnbot update Hello world!"
    kwarg_dict = bot.parse_comment_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert (
        response.json()[-1]["body"]
        == "Assessment entry updated with message: \nHello world!"
    )
    # Confirm update
    payload["comment"]["body"] = "@brnbot view"
    response = bot.process_cmd(payload)
    assert response.json()["log"][-1]["message"] == "Hello world!"


def test_delete():
    """
    Test the bot's delete command
    """

    # Initialize the assessment if needed
    try:
        payload["comment"]["body"] = "@brnbot init"
        bot.process_cmd(payload)
    except:
        pass

    ## Successful delete command
    # Delete the assessment
    payload["comment"]["body"] = "@brnbot delete"
    response = bot.process_cmd(payload)
    assert response.status_code == 200
    assert response.json() == {"Entry deleted": True}
    # Confirm cannot view
    payload["comment"]["body"] = "@brnbot view"
    with pytest.raises(requests.exceptions.HTTPError):
        bot.process_cmd(payload)
    # Confirm cannot delete again
    payload["comment"]["body"] = "@brnbot delete"
    with pytest.raises(requests.exceptions.HTTPError):
        bot.process_cmd(payload)


def test_init():
    """
    Test the bot's init command
    """

    # delete the assessment if needed
    try:
        payload["comment"]["body"] = "@brnbot delete"
        bot.process_cmd(payload)
    except:
        pass

    ## Init the assessment
    payload["comment"]["body"] = "@brnbot init"
    kwarg_dict = bot.parse_comment_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == "Initialized assessment. 🚀"
    # Confirm cannot init again
    payload["comment"]["body"] = "@brnbot init"
    with pytest.raises(requests.exceptions.HTTPError):
        bot.process_cmd(payload)


def test_update_on_commit():
    """
    Test the bot's update command on a commit
    """

    # Initialize the assessment if needed
    try:
        payload["comment"]["body"] = "@brnbot delete"
        bot.process_cmd(payload)
    except:
        pass
    try:
        payload["comment"]["body"] = "@brnbot init"
        bot.process_cmd(payload)
    except:
        pass

    ## Successful update command
    response = bot.process_commit(payload)
    kwarg_dict = bot.parse_commit_payload(payload)
    assert response.json()
    assert response.status_code == 200
    # Confirm the latest comment is the output of the command
    response2 = utils.get_recent_comments(**kwarg_dict)
    assert kwarg_dict["last_commit"] in response2.json()[-1]["body"]


def test_check():
    """
    Test the bot's check command
    """

    # Initialize the assessment if needed
    try:
        payload["comment"]["body"] = "@brnbot delete"
        bot.process_cmd(payload)
    except:
        pass
    try:
        payload["comment"]["body"] = "@brnbot init"
        bot.process_cmd(payload)
    except:
        pass

    ## Successful check command
    payload["comment"]["body"] = "@brnbot check"
    kwarg_dict = bot.parse_comment_payload(payload)
    assert bot.process_cmd(payload)

    ## Second person on the repo can request a check
    payload2 = copy.deepcopy(payload)
    payload2["sender"]["login"] = "bioresnet"
    assert bot.process_cmd(payload2)


def test_review():
    """
    Test the bot's review command
    """

    # Initialize the assessment if needed
    try:
        print("Delete")
        payload["comment"]["body"] = "@brnbot delete"
        bot.process_cmd(payload)
    except:
        pass
    try:
        print("Init")
        payload["comment"]["body"] = "@brnbot init"
        bot.process_cmd(payload)
    except:
        pass

    # Set the assessment to be passing checks using the update command
    kwarg_dict = bot.parse_comment_payload(payload)
    request_url = f"{const.settings.CRUD_APP_URL}/api/check"
    latest_commit = utils.get_last_commit(
        owner=kwarg_dict["owner"],
        repo_name=kwarg_dict["repo_name"],
        access_token=kwarg_dict["access_token"],
    )["sha"]
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
    kwarg_dict = bot.parse_comment_payload(payload)
    response = bot.process_cmd(payload)
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


def test_approve():
    """
    Test the bot's approve command
    """
    # Initialize the assessment if needed
    try:
        payload["comment"]["body"] = "@brnbot delete"
        bot.process_cmd(payload)
    except:
        pass
    try:
        payload["comment"]["body"] = "@brnbot init"
        bot.process_cmd(payload)
    except:
        pass

    # Ensure passing checks
    payload["comment"]["body"] = "@brnbot check"
    assert bot.process_cmd(payload)

    # Ensure it is under review
    payload["comment"]["body"] = "@brnbot review"
    response = bot.process_cmd(payload)
    assert response.status_code == 200

    # Successful approve command
    payload["comment"]["body"] = "@brnbot approve"
    payload2 = copy.deepcopy(payload)
    payload2["sender"]["login"] = "bioresnet"
    response = bot.process_cmd(payload2)
    assert response.status_code == 200
    assert response.json() == {"Assessment Approved": True}
