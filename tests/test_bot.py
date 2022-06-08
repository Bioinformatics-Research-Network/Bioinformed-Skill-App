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
