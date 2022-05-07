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


def test_init():
    """
    Test the bot's init command
    """
    payload["comment"]["body"] = "@brnbot init"
    assert bot.process_cmd(payload) == "Initialized assessment. 🚀"


# def test_init_again():
#     """
#     Test the bot's init command again
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     assert bot.process_cmd(payload) == "Assessment already initialized."


# def test_init_invalid():
#     """
#     Test the bot's init command with invalid repo
#     """
#     payload["sender"]["login"] = "invalid_user"
#     payload["comment"]["body"] = "@brnbot init"
#     assert bot.process_cmd(payload) == "There is no record of @invalid_user in the BRN database. Please sign up at https://bioresnet.org/signup."


# def test_init_invalid_install():
#     """
#     Test the bot's init command with invalid installation (non-BRN installation)
#     """
#     payload["installation"]["id"] = 1
#     payload["comment"]["body"] = "@brnbot init"
#     assert bot.process_cmd(payload) == "This is not a Bioinformatics Research Network installation. Please contact the installation's administrator."

