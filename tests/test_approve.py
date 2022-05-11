
from bot.const import *
from bot.utils import *
from bot.bot import *

# instantiate the bot
bot = Bot()

# Payload for test repo
# https://github.com/Bioinformatics-Research-Network/test-bot/pull/1
payload = {
    "sender": {
        "login": "botuser",
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


def test_approve():
    """
    Test the bot's approve command
    """
    payload["comment"]["body"] = "@brnbot approve"
    payload["sender"]["login"] = "Steven_Shortridge89"
    assert bot.process_cmd(payload) == "Assessment approved. 🤘"


# def test_approve_no_auth():
#     """
#     Test the bot's approve command without authentication
#     """
#     assert bot.approve(payload) == "You must be a registered BRN reviewer to use this command."


# def test_approve_auth():
#     """
#     Test the bot's approve command with authentication
#     """
#     payload["sender"]["login"] = "brn_reviewer"
#     bot.update_status(payload, "pass")
#     assert bot.approve(payload) == "Assessment approved. 🎉 Your badge will be electronically delivered to you shortly. 🔥 You can also view your badges at https://bioresnet.org/certificate."


# def test_approve_invalid():
#     """
#     Test the bot's approve command with invalid user
#     """
#     payload["sender"]["login"] = "invalid_user"
#     assert bot.approve(payload) == "There is no record of @invalid_user in the BRN database. Cannot approve assessment."


# def test_approve_invalid_install():
#     """
#     Test the bot's approve command with invalid installation (non-BRN installation)
#     """
#     payload["sender"]["login"] = "brn_reviewer"
#     payload["installation"]["id"] = 1
#     assert bot.approve(payload) == "This is not a Bioinformatics Research Network installation. Cannot approve assessment."


# def test_approve_invalid_status():
#     """
#     Test the bot's approve command with invalid status
#     """
#     payload["sender"]["login"] = "brn_reviewer"
#     payload["comment"]["body"] = "@brnbot init"
#     bot.process_cmd(payload)
#     assert bot.approve(payload) == "Assessment not approved. Please use @brnbot check to run automated tests, then @brnbot review to trigger manual review, then @brnbot approve to approve the assessment."

