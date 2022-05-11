import requests
import json
from datetime import datetime, timedelta, timezone
from bot import const

def post_comment(text: str, **kwargs):
    """
    Post a comment to the issue

    Args:
        text: The text to post
        **kwargs: The keyword arguments
    
    Returns:
        The response from the GitHub API
    """
    headers = {
        "Authorization": f"Bearer {kwargs['access_token']}",
        "Accept": const.accept_header,
    }

    request_url = f"{const.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments"
    response = requests.post(
        request_url,
        headers=headers,
        json={"body": text},
    )
    return response


def get_comment_by_id(comment_id, **kwargs):
    """
    Get the comment by ID
    """
    headers = {
        "Authorization": f"Bearer {kwargs['access_token']}",
        "Accept": const.accept_header,
    }
    request_url = f"{const.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments/{comment_id}"
    response = requests.get(request_url, headers=headers)
    return response


def get_recent_comments(delt: timedelta = timedelta(minutes=1), **kwargs):
    """
    Retrieve the last comment
    """
    headers = {
        "Authorization": f"Bearer {kwargs['access_token']}",
        "Accept": const.accept_header,
    }
    request_url = f"{const.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments"
    one_minute_ago = datetime.now(tz=timezone.utc) - delt
    response = requests.get(
        request_url,
        headers=headers,
        params = {
            "since": one_minute_ago.isoformat()
        }
    )
    return response


def delete_comment(comment_id, **kwargs):
    """
    Delete a comment
    """
    headers = {
        "Authorization": f"Bearer {kwargs['access_token']}",
        "Accept": const.accept_header,
    }
    request_url = f"{const.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/comments/{comment_id}"
    response = requests.delete(request_url, headers=headers)
    return response


def get_assessment_name(payload: dict):
    """
    Get the assessment name based on installation ID
    """
    install_id = payload["installation"]["id"]
    assessment = [key for key, value in const.installation_ids.items() if value == install_id][0]
    if assessment is None:
        return "Unknown"
    return assessment


def get_last_commit(owner, repo_name, access_token):
    """
    Get the last commit

    Args:
        owner: The owner of the repository
        repo_name: The name of the repository
        access_token: The access token

    Returns:
        The response from the GitHub API with the last commit SHA
    """
    url = f"{const.gh_url}/repos/{owner}/{repo_name}/commits"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": const.accept_header,
    }
    response = requests.get(url, headers=headers)
    commits = response.json()
    if len(commits) > 0:
        commit = commits[0]
        commit_sha = commit["sha"]
        return commit_sha
    else:
        return None


def forbot(payload: dict):
    """
    Check if the payload is for the bot
    """
    splt = payload["comment"]["body"].split()
    if len(splt) > 0:
        return splt[0] == "@brnbot"
    else:
        return False


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
    request_url = f"{const.gh_url}/app/installations/{installation_id}/access_tokens"
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
        installation_id: get_access_token(installation_id, jwt)["token"]
        for training, installation_id in installation_ids.items()
    }

    # Save the access tokens along with the expiration time
    current_tokens = {
        "time": datetime.now(),
        "expires": datetime.now() + timedelta(hours=1),
        "tokens": token_dict,
    }

    # Save the access tokens to a file
    with open(const.token_fp, "w") as f:
        json.dump(current_tokens, f, indent=4, sort_keys=True, default=str)

    # Return the access tokens
    return current_tokens
