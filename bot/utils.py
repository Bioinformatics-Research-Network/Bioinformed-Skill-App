import os
import requests
import json
from .const import *
from datetime import datetime, timedelta
from github import Github, GithubIntegration


def get_access_token(installation_id, jwt):
    """
    Get the access token for the installation

    Args:
        installation_id: The installation ID
        jwt: The JWT

    Returns:
        The response from the GitHub API with the access token
    """
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Accept": "application/vnd.github.v3+json",
    }
    request_url = (
        f"{base_url}/app/installations/{installation_id}/access_tokens"
    )
    response = requests.post(request_url, headers=headers)

    response_dict = response.json()
    return response_dict


def get_all_access_tokens(installation_ids, jwt):
    """
    Get the access tokens for the installations
    """

    print("Getting access tokens")
    # Get the access tokens for the installations
    token_dict = {
        installation_id: get_access_token(
            installation_id, jwt
        )["token"]
        for training, installation_id in installation_ids.items()
    }

    # Save the access tokens along with the expiration time
    current_tokens = {
        "time": datetime.now(),
        "expires": datetime.now() + timedelta(hours=1),
        "tokens": token_dict,
    }

    # Save the access tokens to a file
    with open(token_fp, "w") as f:
        json.dump(current_tokens, f, indent=4, sort_keys=True, default=str)

    # Return the access tokens
    return current_tokens
