import os
from pydantic import BaseSettings
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
workflow_filename = "tests.yml"
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
    "Test": 25533349,
    "Skill Assessment Tutorial (Python)": 25630785,
    "Skill Assessment Tutorial (R)": 25901888,
    "Python Programming I": 25616884,
    "R Programming I": 25958132,
    "Python Programming II": 25476585,
    "R Programming II": 25520792,
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


BADGE_IDs = {
    "Skill Assessment Tutorial (R)": "zS91nadxSQCchE_ahLFgvw",
    "Skill Assessment Tutorial (Python)": "MMuVRwluTd6cI33-0ILs3w",
    "Python Programming I": "rfT_GJApRoavmHi_TemqqQ",
    "Python Programming II": "5xCf5xpRQqOhRCykbITuLA",
    "R Programming I": "v0CU877hR5qI8OtDN7EYTg",
    "R Programming II": "h3lCNmoHRjmqNI5D5Q6a-g",
    "Test": "OcVxPZEORASs4dBL0h5mOw",
}


## Get secrets

class Settings(BaseSettings):
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_BUCKET: str
    AWS_REGION: str

print(os.environ.get("APP_ENV") )
if os.environ.get("APP_ENV") == "development":
    print("Loading development settings")
    settings = Settings(_env_file=".dev.env", _env_file_encoding="utf-8")
elif os.environ.get("APP_ENV") == "production":
    print("Loading production settings")
    settings = Settings(_env_file=".prod.env", _env_file_encoding="utf-8")
elif os.environ.get("APP_ENV") == "testing":
    print("Loading testing settings")
    settings = Settings(_env_file=".test.env", _env_file_encoding="utf-8")
else: # pragma: no cover
    print("Loading default settings (testing)")
    settings = Settings(_env_file=".test.env", _env_file_encoding="utf-8")
