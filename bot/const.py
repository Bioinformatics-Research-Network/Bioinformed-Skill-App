import os
from github import GithubIntegration

# ID of the GitHub integration
app_id = os.environ["APP_ID"]

# Path to the bot certificate
bot_key_path = os.environ["BOT_KEY_PATH"]

# Base URL for the GitHub API
gh_url = "https://api.github.com"

# Base HTTP URL for GitHub.com
gh_http = "https://github.com"

# Base URL for the BRN CRUD API
brn_url = "http://localhost:2000"

# Header for the GitHub API
accept_header = "application/vnd.github.v3+json"

# Filename for all actions workflows
workflow_filename = "checks.yml"
# workflow_filename = 1

# ref for all trainee git
git_ref = "main"

# file for storing temporary access tokens
token_fp = "access_tokens.json"

# BRN bot name
bot_name = "brn-bot[bot]"

# Admin usernames
admins = ["millerh1", "itchytummy", "bioresnet"]

# Dict of valid App install IDs
installation_ids = {
    "Python Programming II": 25476585,
    "Test": 25533349,
    "Skill Assessment Tutorial (Python)": 25630785,
    "Skill Assessment Tutorial (R)": 25901888,
    "Python Programming": 25616884,
}

# Dict of valid commands
cmds = ["hello", "help", "init", "view", "delete", "review", "approve"]

# Read the bot certificate
try:
    app_key = os.environ["BOT_KEY"]
except KeyError:  # pragma: no cover
    with open(os.path.normpath(os.path.expanduser(bot_key_path)), "r") as cert_file:
        app_key = cert_file.read()


# Create a GitHub integration instance
git_integration = GithubIntegration(integration_id=app_id, private_key=app_key)
