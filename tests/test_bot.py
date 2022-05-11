import pytest
import requests
from bot import bot, const, utils

# instantiate the bot
bot = bot.Bot()

# Payload for test repo
# https://github.com/Bioinformatics-Research-Network/test-bot/pull/1
payload = {
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
    kwarg_dict = bot.parse_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == f"Hello, @{kwarg_dict['sender']}! 😊"


def test_invalid():
    """
    Test invalid bot command
    """
    payload["comment"]["body"] = "@brnbot invalid"
    kwarg_dict = bot.parse_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == "Invalid command. Try @brnbot help"


def test_help():
    """
    Test the bot's help command
    """
    payload["comment"]["body"] = "@brnbot help"
    kwarg_dict = bot.parse_payload(payload)
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
    except: pass

    ## Successful view command
    payload["comment"]["body"] = "@brnbot view"
    response = bot.process_cmd(payload)
    assert response.status_code == 200
    assert response.json()["user_id"] == 1
    # Confirm the latest comment is the output of the view command
    response2 = utils.get_recent_comments(**bot.parse_payload(payload))
    assert response.json()['latest_commit'] in response2.json()[-1]["body"]
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
    except: pass

    ## Successful update command
    payload["comment"]["body"] = "@brnbot update Hello world!"
    kwarg_dict = bot.parse_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == "Assessment entry updated with message: \nHello world!"
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
    except: pass

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
    except: pass

    ## Init the assessment
    payload["comment"]["body"] = "@brnbot init"
    kwarg_dict = bot.parse_payload(payload)
    assert bot.process_cmd(payload)
    response = utils.get_recent_comments(**kwarg_dict)
    assert response.json()[-1]["body"] == "Initialized assessment. 🚀"
    # Confirm cannot init again
    payload["comment"]["body"] = "@brnbot init"
    with pytest.raises(requests.exceptions.HTTPError):
        bot.process_cmd(payload)
    





