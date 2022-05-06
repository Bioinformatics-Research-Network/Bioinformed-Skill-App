import os
import requests

from flask import Flask, request
from github import Github, GithubIntegration


app = Flask(__name__)
# MAKE SURE TO CHANGE TO YOUR APP NUMBER!!!!!
app_id = '197981'
bot_key_path = '~/.certs/github/brn_bot.pem'
# Read the bot certificate
with open(
        os.path.normpath(os.path.expanduser(bot_key_path)),
        'r'
) as cert_file:
    app_key = cert_file.read()

# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)


def bot_check(payload):
    """
    Check if the payload is for the bot
    """
    return payload['comment']['body'].startswith('@brnbot')


def get_current_issue(payload):
    """
    Get the current issue from the payload
    """
    owner = payload['repository']['owner']['login']
    repo_name = payload['repository']['name']
    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id
        ).token
    )
    repo = git_connection.get_repo(f"{owner}/{repo_name}")
    issue = repo.get_issue(number=payload['issue']['number'])
    return issue


@app.route("/", methods=['POST'])
def bot():
    # Get the event payload
    payload = request.json
    print(bot_check(payload))
    if bot_check(payload):
        # Get the current issue
        issue = get_current_issue(payload)
        # send the comment
        issue.create_comment(f"Hello {payload['sender']['login']}!")

    # # Check if the event is a GitHub PR creation event
    # if not all(k in payload.keys() for k in ['action', 'pull_request']) and \
    #         payload['action'] == 'opened':
    #     return "ok"

    return "ok"




app.run(debug=True, port=5000)    
