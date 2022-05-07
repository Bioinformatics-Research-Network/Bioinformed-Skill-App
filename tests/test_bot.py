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


def test_hello():
    """
    Test the bot's hello command
    """
    assert bot.process_cmd(payload) == "Hello, @botuser! 😊"


def test_invalid():
    """
    Test invalid bot command
    """
    payload["comment"]["body"] = "@brnbot invalid"
    assert bot.process_cmd(payload) == "Invalid command. Try @brnbot help"


def test_help():
    """
    Test the bot's help command
    """
    payload["comment"]["body"] = "@brnbot help"
    assert bot.process_cmd(payload) == "Available commands: \n" + "\n".join(cmds)


def test_init():
    """
    Test the bot's init command
    """
    payload["comment"]["body"] = "@brnbot init"
    assert bot.process_cmd(payload) == "Initialized assessment. 🚀"


def test_init_again():
    """
    Test the bot's init command again
    """
    payload["comment"]["body"] = "@brnbot init"
    assert bot.process_cmd(payload) == "Assessment already initialized."


def test_init_invalid():
    """
    Test the bot's init command with invalid repo
    """
    payload["sender"]["login"] = "invalid_user"
    payload["comment"]["body"] = "@brnbot init"
    assert bot.process_cmd(payload) == "There is no record of @invalid_user in the BRN database. Please sign up at https://bioresnet.org/signup."


def test_init_invalid_install():
    """
    Test the bot's init command with invalid installation (non-BRN installation)
    """
    payload["installation"]["id"] = 1
    payload["comment"]["body"] = "@brnbot init"
    assert bot.process_cmd(payload) == "This is not a Bioinformatics Research Network installation. Please contact the installation's administrator."


def test_check_no_init():
    """
    Test the bot's check command
    """
    payload["comment"]["body"] = "@brnbot check"
    assert bot.process_cmd(payload) == "Assessment not initialized. Please run @brnbot init."


def test_check_init():
    """
    Test the bot's check command
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["comment"]["body"] = "@brnbot check"
    assert bot.process_cmd(payload) == "Assessment check in progress. 🔥"


def test_check_invalid():
    """
    Test the bot's check command with invalid user
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["sender"]["login"] = "invalid_user"
    payload["comment"]["body"] = "@brnbot check"
    assert bot.process_cmd(payload) == "There is no record of @invalid_user in the BRN database. Please sign up at https://bioresnet.org/signup."


def test_check_invalid_install():
    """
    Test the bot's check command with invalid installation (non-BRN installation)
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["installation"]["id"] = 1
    payload["comment"]["body"] = "@brnbot check"
    assert bot.process_cmd(payload) == "This is not a Bioinformatics Research Network installation. Please contact the installation's administrator."


def test_review_no_init():
    """
    Test the bot's review command
    """
    payload["comment"]["body"] = "@brnbot review"
    assert bot.process_cmd(payload) == "Assessment not initialized. Please run @brnbot init."


def test_review_init_no_check():
    """
    Test the bot's review command
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["comment"]["body"] = "@brnbot review"
    assert bot.process_cmd(payload) == "Assessment check not completed. You must first run @brnbot check and pass all tests."


def test_review_init_check_pass():
    """
    Test the bot's review command
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    bot.update_status(payload, "pass")
    payload["comment"]["body"] = "@brnbot review"
    assert bot.process_cmd(payload) == "Assessment review in progress. 🔥"


def test_review_init_check_fail():
    """
    Test the bot's review command
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    bot.update_check_status(payload, "fail")
    payload["comment"]["body"] = "@brnbot review"
    assert bot.process_cmd(payload) == "Review command unavailable. You must first run @brnbot check and pass all tests before running @brnbot review."


def test_review_invalid():
    """
    Test the bot's review command with invalid user
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    bot.update_status(payload, "pass")
    payload["sender"]["login"] = "invalid_user"
    payload["comment"]["body"] = "@brnbot review"
    assert bot.process_cmd(payload) == "There is no record of @invalid_user in the BRN database. Please sign up at https://bioresnet.org/signup."


def test_review_invalid_install():
    """
    Test the bot's review command with invalid installation (non-BRN installation)
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    bot.update_status(payload, "pass")
    payload["installation"]["id"] = 1
    payload["comment"]["body"] = "@brnbot review"
    assert bot.process_cmd(payload) == "This is not a Bioinformatics Research Network installation. Please contact the installation's administrator."


def test_update_status_no_init():
    """
    Test the bot's update_status command
    """
    bot.update_status(payload, "some_status")
    assert bot.process_cmd(payload) == "Assessment not initialized. Please run @brnbot init."


def test_update_status_init_invalid():
    """
    Test the bot's update_status command with invalid user
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["sender"]["login"] = "invalid_user"
    assert bot.update_status(payload, "some_status") == "There is no record of @invalid_user in the BRN database. Cannot update status."


def test_update_status_init_invalid_install():
    """
    Test the bot's update_status command with invalid installation (non-BRN installation)
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["installation"]["id"] = 1
    assert bot.update_status(payload, "some_status") == "This is not a Bioinformatics Research Network installation. Cannot update status."


def test_update_status_valid():
    """
    Test the bot's update_status command with valid user and installation
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    assert bot.update_status(payload, "some_status") == "Status updated."


def test_check_status_no_init():
    """
    Test the bot's check_status command
    """
    assert bot.check_status(payload) == "Assessment not initialized. Please run @brnbot init."


def test_check_status_init_invalid():
    """
    Test the bot's check_status command with invalid user
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["sender"]["login"] = "invalid_user"
    assert bot.check_status(payload) == "There is no record of @invalid_user in the BRN database. Cannot check status. Please sign up at https://bioresnet.org/signup."


def test_check_status_init_invalid_install():
    """
    Test the bot's check_status command with invalid installation (non-BRN installation)
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["installation"]["id"] = 1
    assert bot.check_status(payload) == "This is not a Bioinformatics Research Network installation. Cannot check status. Please contact the installation's administrator."


def test_check_status_valid():
    """
    Test the bot's check_status command with valid user and installation
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    assert bot.check_status(payload) == "Assessment initialized. Use @brnbot check to run automated tests."


def test_check_status_valid_pass():
    """
    Test the bot's check_status command with valid user and installation
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    bot.update_status(payload, "pass")
    assert bot.check_status(payload) == "Assessment check completed. Use @brnbot review to trigger manual review."


def test_approve_no_auth():
    """
    Test the bot's approve command without authentication
    """
    assert bot.approve(payload) == "You must be a registered BRN reviewer to use this command."


def test_approve_auth():
    """
    Test the bot's approve command with authentication
    """
    payload["sender"]["login"] = "brn_reviewer"
    bot.update_status(payload, "pass")
    assert bot.approve(payload) == "Assessment approved. 🎉 Your badge will be electronically delivered to you shortly. 🔥 You can also view your badges at https://bioresnet.org/certificate."


def test_approve_invalid():
    """
    Test the bot's approve command with invalid user
    """
    payload["sender"]["login"] = "invalid_user"
    assert bot.approve(payload) == "There is no record of @invalid_user in the BRN database. Cannot approve assessment."


def test_approve_invalid_install():
    """
    Test the bot's approve command with invalid installation (non-BRN installation)
    """
    payload["sender"]["login"] = "brn_reviewer"
    payload["installation"]["id"] = 1
    assert bot.approve(payload) == "This is not a Bioinformatics Research Network installation. Cannot approve assessment."


def test_approve_invalid_status():
    """
    Test the bot's approve command with invalid status
    """
    payload["sender"]["login"] = "brn_reviewer"
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    assert bot.approve(payload) == "Assessment not approved. Please use @brnbot check to run automated tests, then @brnbot review to trigger manual review, then @brnbot approve to approve the assessment."


def test_update_log_no_init():
    """
    Test the bot's update_log command
    """
    assert bot.update_log(payload) == "Assessment not initialized. Please run @brnbot init."


def test_update_log_init_invalid():
    """
    Test the bot's update_log command with invalid user
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["sender"]["login"] = "invalid_user"
    assert bot.update_log(payload) == "There is no record of @invalid_user in the BRN database. Cannot update log."


def test_update_log_init_invalid_install():
    """
    Test the bot's update_log command with invalid installation (non-BRN installation)
    """
    payload["comment"]["body"] = "@brnbot init"
    bot.process_cmd(payload)
    payload["installation"]["id"] = 1
    assert bot.update_log(payload) == "This is not a Bioinformatics Research Network installation. Cannot update log."

