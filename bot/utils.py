import requests
import json
import time
from datetime import datetime, timedelta, timezone
from bot import const


def post_comment(text: str, **kwargs) -> requests.Response:
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
    time.sleep(1)  # Sleep for 1 second to avoid rate limiting
    print(f"Posting comment: {text}")
    print(kwargs['access_token'])
    print(request_url)
    response = requests.post(
        request_url,
        headers=headers,
        json={"body": text},
    )
    response.raise_for_status()
    return response


def assign_reviewer(reviewer_username: str, **kwarg_dict) -> requests.Response:
    """
    Assign a reviewer to the assessment via API
    """
    headers = {
        "Authorization": f"Bearer {kwarg_dict['access_token']}",
        "Accept": const.accept_header,
    }
    request_url = f"{kwarg_dict['pr_url']}/requested_reviewers"
    response = requests.post(
        request_url,
        headers=headers,
        json={"reviewers": [reviewer_username]},
    )
    return response


def get_reviewer(**kwarg_dict) -> requests.Response:
    """
    Get the reviewer from github API
    """
    headers = {
        "Authorization": f"Bearer {kwarg_dict['access_token']}",
        "Accept": const.accept_header,
    }
    request_url = f"{kwarg_dict['pr_url']}/requested_reviewers"
    response = requests.get(
        request_url,
        headers=headers,
    )
    return response


def remove_reviewer(reviewer_username: str, **kwarg_dict) -> requests.Response:
    """
    Remove the reviewer from the PR
    """
    headers = {
        "Authorization": f"Bearer {kwarg_dict['access_token']}",
        "Accept": const.accept_header,
    }
    request_url = f"{kwarg_dict['pr_url']}/requested_reviewers"
    response = response = requests.delete(
        request_url,
        headers=headers,
        json={"reviewers": [reviewer_username]},
    )
    return response


def get_comment_by_id(comment_id, **kwargs) -> requests.Response:
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


def get_recent_comments(
    delt: timedelta = timedelta(minutes=1), **kwargs
) -> requests.Response:
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
        request_url, headers=headers, params={"since": one_minute_ago.isoformat()}
    )
    return response


def get_last_comment(**kwargs) -> requests.Response:
    """
    Get the last comment
    """
    headers = {
        "Authorization": f"Bearer {kwargs['access_token']}",
        "Accept": const.accept_header,
    }
    request_url = f"{const.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments"
    response = requests.get(request_url, headers=headers)
    return response


def delete_comment(comment_id, **kwargs) -> requests.Response:
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


def get_assessment_name(payload: dict) -> str:
    """
    Get the assessment name based on installation ID
    """
    install_id = payload["installation"]["id"]
    assessment = [
        key for key, value in const.installation_ids.items() if value == install_id
    ][0]
    if assessment is None:
        return "Unknown"
    return assessment


def get_last_commit(owner, repo_name, access_token) -> dict:
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
        return commit
    else:
        return None


def is_for_bot(payload: dict) -> bool:
    """
    Check if the payload is for the bot
    """
    try:
        splt = payload["comment"]["body"].split()
        if len(splt) > 0:
            return splt[0] == "@brnbot"
        else:
            return False
    except KeyError:
        return False


def is_pr_commit(payload: dict, event: str) -> bool:
    """
    Check if the payload is a user commit on the PR
    """
    # TODO: What else could cause this to trigger?
    # TODO: What about a non-user committing something?
    if event == "pull_request" and payload["action"] == "synchronize":
        try:
            payload["pull_request"]["head"]["sha"]
            valid_ids = const.installation_ids.values()
            return (
                payload["sender"]["login"] != "github-classroom[bot]"
                and payload["installation"]["id"] in valid_ids
            )
        except KeyError:
            return False
    else:
        return False


def is_delete_repo(payload: dict, event: str) -> bool:
    """
    Check if the payload is a delete repo event
    """
    if event == "repository" and payload["action"] == "deleted":
        try:
            valid_ids = const.installation_ids.values()
            return payload["installation"]["id"] in valid_ids
        except KeyError:
            return False
    else:
        return False


def is_assessment_init(payload: dict, event: str) -> bool:
    """
    Check if the payload is a new repo event
    """
    if event == "pull_request" and payload["action"] == "edited":
        try:
            payload["pull_request"]["head"]["sha"]
            valid_ids = const.installation_ids.values()
            return (
                payload["sender"]["login"] == "github-classroom[bot]"
                and payload["installation"]["id"] in valid_ids
            )
        except KeyError:
            return False
    else:
        return False


def is_workflow_run(payload: dict) -> bool:
    """
    Check if the payload is a workflow run
    """
    try:
        payload["workflow_run"]["head_sha"]
        return payload["action"] == "completed"
    except KeyError:
        return False


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
    request_url = f"{const.gh_url}/app/installations/{installation_id}/access_tokens"
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
    with open(const.token_fp, "w") as f:
        json.dump(current_tokens, f, indent=4, sort_keys=True, default=str)

    # Return the access tokens
    return current_tokens


def dispatch_workflow(**kwarg_dict) -> requests.Response:
    # Dispatch workflow file
    request_url = (
        f"{const.gh_url}/repos/{kwarg_dict['owner']}/"
        + f"{kwarg_dict['repo_name']}/actions/workflows/{const.workflow_filename}/dispatches"
    )
    headers = {
        "Authorization": f"Bearer {kwarg_dict['access_token']}",
        "Accept": const.accept_header,
    }
    response = requests.post(
        request_url,
        headers=headers,
        json={
            "ref": const.git_ref,
        },
    )
    return response
