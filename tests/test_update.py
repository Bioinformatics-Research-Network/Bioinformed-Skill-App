from bot.const import *
from bot.utils import *
from bot.bot import *

# instantiate the bot
bot = Bot()

# Payload for test repo
# https://github.com/Bioinformatics-Research-Network/test-bot/pull/1
payload = {
    "sender": {
        "login": "Nicole_Cayer3",
    },
    "comment": {
        "body": "@brnbot hello",
    },
    "installation": {
        "id": 25500143,
    },
    "issue": {
        "number": 1,
    },
    "repository": {
        "owner": {
            "login": "Bioinformatics-Research-Network",
        },
        "name": "test-bot",
    },
}


def test_update():
    """
    Test the bot's update command
    """
    response = bot.update(
        log={
            "hello": "world",
        },
        payload=payload,
    )
    assert response.status_code == 200


# def test_update_status_no_init():
#     """
#     Test the bot's update_status command
#     """
#     bot.update_status(payload, "some_status")
#     assert bot.process_cmd(payload) == "Assessment not initialized. Please run @brnbot init."


# def test_update_status_init_invalid():
#     """
#     Test the bot's update_status command with invalid user
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     payload["sender"]["login"] = "invalid_user"
#     assert bot.update_status(payload, "some_status") == "There is no record of @invalid_user in the BRN database. Cannot update status."


# def test_update_status_init_invalid_install():
#     """
#     Test the bot's update_status command with invalid installation (non-BRN installation)
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     payload["installation"]["id"] = 1
#     assert bot.update_status(payload, "some_status") == "This is not a Bioinformatics Research Network installation. Cannot update status."


# def test_update_status_valid():
#     """
#     Test the bot's update_status command with valid user and installation
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     assert bot.update_status(payload, "some_status") == "Status updated."

