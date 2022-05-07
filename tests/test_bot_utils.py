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


def test_get_last_commit():
    """
    Test the bot's get_last_commit command
    """
    kwarg_dict = bot.parse_payload(payload)
    last_commit = get_last_commit(
        owner=kwarg_dict["owner"], 
        repo_name=kwarg_dict["repo_name"],
        access_token=kwarg_dict["access_token"]
    )
    # Commit should be "a7e221639bd8766ec83d832052655d9c03260e5b" for the test repo
    assert last_commit == "a7e221639bd8766ec83d832052655d9c03260e5b"


def test_get_assessment_name():
    """
    Test the bot's get_assessment_name command
    """
    assessment_name = get_assessment_name(payload)
    # Assessment should be "test" for the test repo
    assert assessment_name == "Test"


def test_forbot():
    """
    Test the bot's forbot command
    """
    assert forbot(payload)
    payload["comment"]["body"] = "@brnbottt"
    assert not forbot(payload)

