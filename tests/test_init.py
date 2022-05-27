from distutils.command.config import config
from time import sleep
import pytest
import requests
import copy
from bot import bot, utils, const, schemas

# instantiate the bot
bot = bot.Bot()

init_request = schemas.InitBotRequest(
    name="Test",
    install_id=25533349,
    repo_prefix="test--",
    github_org="brn-test-assessment",
    latest_release="v0.0.1a",
    template_repo="Skill-Assessment-Tutorial-R",
    username="bioresnet",
    review_required=True,
)


def test_init_bot():
    """
    Test the bot's init command
    """
    access_token = bot.current_tokens["tokens"][str(init_request.install_id)]

    repo_name = init_request.repo_prefix + init_request.username
    url = f"https://api.github.com/repos/{init_request.github_org}/{repo_name}"
    print(url)
    # Check if repo exosts
    response = requests.get(
        url=url,
        headers={"Authorization": f"token {access_token}"},
    )
    if response.status_code == 200:
        print("Repo exists")
        # Delete the repo 
        request_url = f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}"
        sleep(1)
        response = requests.delete(
            request_url,
            headers={"Authorization": f"token {access_token}"},
        )
        response.raise_for_status()
        print("Deleted repo")


    resp = bot.process_init_payload(init_request)

    assert resp

