import os
from datetime import datetime, timedelta
import json
import requests
from bot import dependencies


def get_access_token(installation_id, jwt) -> dict:
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
        f"{dependencies.gh_url}/app/installations/{installation_id}/access_tokens"
    )
    response = requests.post(request_url, headers=headers)
    response_dict = response.json()
    print(response_dict)
    response.raise_for_status()
    print(response_dict)
    return response_dict


def get_all_access_tokens(installation_ids, jwt) -> dict:
    """
    Get the access tokens for the installations
    """

    print("Getting access tokens")
    # Get the access tokens for the installations
    print(installation_ids.items())
    try:
        token_dict = {
            installation_id: get_access_token(installation_id, jwt)["token"]
            for training, installation_id in installation_ids.items()
        }
    except KeyError:
        token_dict = {}

    # Save the access tokens along with the expiration time
    current_tokens = {
        "time": datetime.now(),
        "expires": datetime.now() + timedelta(hours=1),
        "tokens": token_dict,
    }

    # Save the access tokens to a file
    with open(dependencies.token_fp, "w") as f:
        json.dump(current_tokens, f, indent=4, sort_keys=True, default=str)

    # Return the access tokens
    return current_tokens


def retrieve_access_tokens():
    """
    Load the access tokens from the file and regenerate if expired
    """
    # Create tokens if file doesn't exist
    if not os.path.exists(dependencies.token_fp):
        print("Getting jwt")
        jwt = dependencies.git_integration.create_jwt()
        print("Getting tokens")
        get_all_access_tokens(dependencies.installation_ids, jwt=jwt)
    with open(dependencies.token_fp, "r") as f:
        current_tokens = json.load(f)
    exp_time = datetime.strptime(
        current_tokens["expires"], "%Y-%m-%d %H:%M:%S.%f"
    )
    if exp_time < datetime.now():
        print("EXPIRED")
        print("Getting jwt")
        jwt = dependencies.git_integration.create_jwt()
        print("Getting tokens")
        get_all_access_tokens(dependencies.installation_ids, jwt=jwt)
    else:
        print("NOT EXPIRED")
    with open(dependencies.token_fp, "r") as f:
        current_tokens = json.load(f)
        return current_tokens
