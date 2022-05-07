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


def test_check():
    """
    Test the bot's check command
    """
    payload["comment"]["body"] = "@brnbot check"
    assert bot.process_cmd(payload) == "Checking assessment. 🤔"


# def test_check_no_init():
#     """
#     Test the bot's check command
#     """
#     payload["comment"]["body"] = "@brnbot check"
#     assert bot.process_cmd(payload) == "Assessment not initialized. Please run @brnbot init."


# def test_check_init():
#     """
#     Test the bot's check command
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     payload["comment"]["body"] = "@brnbot check"
#     assert bot.process_cmd(payload) == "Assessment check in progress. 🔥"


# def test_check_invalid():
#     """
#     Test the bot's check command with invalid user
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     payload["sender"]["login"] = "invalid_user"
#     payload["comment"]["body"] = "@brnbot check"
#     assert bot.process_cmd(payload) == "There is no record of @invalid_user in the BRN database. Please sign up at https://bioresnet.org/signup."


# def test_check_invalid_install():
#     """
#     Test the bot's check command with invalid installation (non-BRN installation)
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     payload["installation"]["id"] = 1
#     payload["comment"]["body"] = "@brnbot check"
#     assert bot.process_cmd(payload) == "This is not a Bioinformatics Research Network installation. Please contact the installation's administrator."



