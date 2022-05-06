import os
from github import Github, GithubIntegration

# ID of the GitHub integration
app_id = os.environ["APP_ID"]

# Path to the bot certificate
bot_key_path = os.environ["BOT_KEY_PATH"]

# Base URL for the GitHub API
base_url = "https://api.github.com"

# Header for the GitHub API
accept_header = "application/vnd.github.v3+json"

# file for storing temporary access tokens
token_fp = "access_tokens.json"

# Dict of valid App install IDs
installation_ids = {
    "Python Programming II": 25476585,
    "Test": 25500143,
}

# Dict of valid commands
cmds = ["hello", "help"]

# Read the bot certificate
try:
    app_key = os.environ["BOT_KEY"]
except KeyError:
    with open(os.path.normpath(os.path.expanduser(bot_key_path)), "r") as cert_file:
        app_key = cert_file.read()


# Create a GitHub integration instance
git_integration = GithubIntegration(integration_id=app_id, private_key=app_key)
