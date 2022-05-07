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


def test_review():
    """
    Test the bot's review command
    """
    payload["comment"]["body"] = "@brnbot review"
    assert bot.process_cmd(payload) == "Finding a reviewer. 🔍 This may take up to 48 hours. If you do not receive a reviewer by then, please contact the BRN reviewer team on Slack."


# def test_review_no_init():
#     """
#     Test the bot's review command
#     """
#     payload["comment"]["body"] = "@brnbot review"
#     assert bot.process_cmd(payload) == "Assessment not initialized. Please run @brnbot init."


# def test_review_init_no_check():
#     """
#     Test the bot's review command
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     payload["comment"]["body"] = "@brnbot review"
#     assert bot.process_cmd(payload) == "Assessment check not completed. You must first run @brnbot check and pass all tests."


# def test_review_init_check_pass():
#     """
#     Test the bot's review command
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     bot.update_status(payload, "pass")
#     payload["comment"]["body"] = "@brnbot review"
#     assert bot.process_cmd(payload) == "Assessment review in progress. 🔥"


# def test_review_init_check_fail():
#     """
#     Test the bot's review command
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     bot.update_check_status(payload, "fail")
#     payload["comment"]["body"] = "@brnbot review"
#     assert bot.process_cmd(payload) == "Review command unavailable. You must first run @brnbot check and pass all tests before running @brnbot review."


# def test_review_invalid():
#     """
#     Test the bot's review command with invalid user
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     bot.update_status(payload, "pass")
#     payload["sender"]["login"] = "invalid_user"
#     payload["comment"]["body"] = "@brnbot review"
#     assert bot.process_cmd(payload) == "There is no record of @invalid_user in the BRN database. Please sign up at https://bioresnet.org/signup."


# def test_review_invalid_install():
#     """
#     Test the bot's review command with invalid installation (non-BRN installation)
#     """
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     bot.update_status(payload, "pass")
#     payload["installation"]["id"] = 1
#     payload["comment"]["body"] = "@brnbot review"
#     assert bot.process_cmd(payload) == "This is not a Bioinformatics Research Network installation. Please contact the installation's administrator."

