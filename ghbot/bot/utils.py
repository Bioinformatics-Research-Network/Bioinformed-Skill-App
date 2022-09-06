from pydoc import resolve
import requests
import time
import os
from datetime import datetime, timedelta, timezone
from bot import dependencies, schemas
from bot.models import AssessmentTracker
import boto3
from time import sleep
import base64
from sqlalchemy.orm import Session
from bot.dependencies import Settings


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
        "Accept": dependencies.accept_header,
    }

    request_url = f"{dependencies.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments"
    print("Post comment")
    print(request_url)
    print(headers)
    time.sleep(1)  # Sleep for 1 second to avoid rate limiting
    print(f"Posting comment: {text}")
    print(kwargs["access_token"])
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
        "Accept": dependencies.accept_header,
    }

    # Add reviewer to the PR
    request_url = f"{kwarg_dict['pr_url']}/requested_reviewers"
    sleep(1)
    response = requests.post(
        request_url,
        headers=headers,
        json={"reviewers": [reviewer_username]},
    )
    response.raise_for_status()
    print("Reviewer added")
    return response


def get_reviewer(**kwarg_dict) -> requests.Response:
    """
    Get the reviewer from github API
    """
    headers = {
        "Authorization": f"Bearer {kwarg_dict['access_token']}",
        "Accept": dependencies.accept_header,
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
        "Accept": dependencies.accept_header,
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
        "Accept": dependencies.accept_header,
    }
    request_url = f"{dependencies.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments/{comment_id}"
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
        "Accept": dependencies.accept_header,
    }
    request_url = f"{dependencies.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments"
    one_minute_ago = datetime.now(tz=timezone.utc) - delt
    response = requests.get(
        request_url,
        headers=headers,
        params={"since": one_minute_ago.isoformat()},
    )
    return response


def get_last_comment(**kwargs) -> requests.Response:
    """
    Get the last comment
    """
    headers = {
        "Authorization": f"Bearer {kwargs['access_token']}",
        "Accept": dependencies.accept_header,
    }
    request_url = f"{dependencies.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments"
    response = requests.get(request_url, headers=headers)
    return response


def delete_comment(comment_id, **kwargs) -> requests.Response:
    """
    Delete a comment
    """
    headers = {
        "Authorization": f"Bearer {kwargs['access_token']}",
        "Accept": dependencies.accept_header,
    }
    request_url = f"{dependencies.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/comments/{comment_id}"
    response = requests.delete(request_url, headers=headers)
    return response


def get_assessment_name(payload: dict) -> str:
    """
    Get the assessment name based on installation ID
    """
    install_id = payload["installation"]["id"]
    assessment = [
        key
        for key, value in dependencies.installation_ids.items()
        if value == install_id
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
    url = f"{dependencies.gh_url}/repos/{owner}/{repo_name}/commits"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": dependencies.accept_header,
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


def is_valid_repo(payload: dict, db: Session) -> bool:
    """
    Check if the payload is for the bot
    """
    repo_name = payload["repository"]["name"]

    # Query the assessment tracker table for this repo name
    assessment_tracker = (
        db.query(AssessmentTracker)
        .filter(AssessmentTracker.repo_name == repo_name)
        .first()
    )

    print("AT")

    if assessment_tracker is None:
        print("Entry unavailable in the assessment tracker table")
    else:
        print(assessment_tracker.id)

    return assessment_tracker is not None


def is_pr_commit(payload: dict, event: str) -> bool:
    """
    Check if the payload is a user commit on the PR
    """
    # TODO: What else could cause this to trigger?
    # TODO: What about a non-user committing something?
    if event == "pull_request" and payload["action"] == "synchronize":
        try:
            payload["pull_request"]["head"]["sha"]
            valid_ids = dependencies.installation_ids.values()
            return (
                payload["sender"]["login"] != "github-classroom[bot]"
                and payload["installation"]["id"] in valid_ids
            )
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
            valid_ids = dependencies.installation_ids.values()
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


def dispatch_workflow(**kwarg_dict) -> requests.Response:
    # Dispatch workflow file
    request_url = (
        f"{dependencies.gh_url}/repos/{kwarg_dict['owner']}/"
        + f"{kwarg_dict['repo_name']}/actions/workflows/{dependencies.workflow_filename}/dispatches"
    )
    headers = {
        "Authorization": f"Bearer {kwarg_dict['access_token']}",
        "Accept": dependencies.accept_header,
    }
    print("Dispatching workflow")
    print(request_url)
    print(headers)
    response = requests.post(
        request_url,
        headers=headers,
        json={
            "ref": dependencies.git_ref,
        },
    )
    return response


def delete_repo(
    delete_request: schemas.DeleteBotRequest, access_token: str
):
    """
    Process a delete repo request
    """
    request_url = (
        f"{dependencies.gh_url}/repos/{delete_request.github_org}/{delete_request.repo_name}"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": dependencies.accept_header,
    }
    print("delete repo")
    print(request_url)
    print(headers)
    try:
        response = requests.delete(request_url, headers=headers)
        response.raise_for_status()
        print("Deleted repo")
    except requests.exceptions.HTTPError:  # pragma: no cover
        print("Repo doesn't exist")
        pass


def archive_repo(**kwargs: dict):
    """
    Process an archive repo request
    """
    request_url = (
        f"{dependencies.gh_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}"
    )
    body = {
        "archived": True,
    }
    try:
        sleep(1)
        response = requests.patch(
            request_url,
            json=body,
            headers={
                "Authorization": f"token {kwargs['access_token']}",
                "Accept": dependencies.accept_header,
            },
        )
        response.raise_for_status()
        print("Repo archived")
    except requests.exceptions.HTTPError as e:  # pragma: no cover
        print(e)
        raise e


def init_create_repo(
    init_request: schemas.InitBotRequest, repo_name: str, access_token: str
):
    # Delete the repo if it already exists
    request_url = f"{dependencies.gh_url}/repos/{init_request.github_org}/{repo_name}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": dependencies.accept_header,
    }
    print("delete repo")
    print(request_url)
    print(headers)
    try:
        response = requests.delete(request_url, headers=headers)
        response.raise_for_status()
        print("Deleted repo")
    except requests.exceptions.HTTPError:  # pragma: no cover
        print("Repo didn't exist yet")
        pass

    # Create the repo in the database using GitHub API
    request_url = f"{dependencies.gh_url}/orgs/{init_request.github_org}/repos"
    body = {
        "name": repo_name,
        "description": init_request.name
        + " Skill Assessment. Trainee: "
        + init_request.username,
        "private": True,
        "visibility": "private",
        "has_issues": False,
        "has_projects": False,
        "has_wiki": False,
        "is_template": False,
    }
    print("Create repo")
    print(request_url)
    print(headers)
    try:
        sleep(1)
        response = requests.post(
            request_url,
            json=body,
            headers={"Authorization": f"token {access_token}"},
        )
        response.raise_for_status()
        print("Repo created")
    except requests.exceptions.HTTPError as e:  # pragma: no cover
        print(e)
        raise e

    try:
        # Put an empty README in the repo
        request_url = f"{dependencies.gh_url}/repos/{init_request.github_org}/{repo_name}/contents/.tmp"
        base64content = base64.b64encode(b".")
        body = {
            "message": "Initial commit",
            "content": base64content.decode("utf-8"),
            "branch": "main",
        }
        sleep(1)
        response = requests.put(
            request_url,
            json=body,
            headers={"Authorization": f"token {access_token}"},
        )
        sha = response.json()["content"]["sha"]
        response.raise_for_status()
        print(".tmp created")
        return sha
    except Exception as e:  # pragma: no cover
        print(e)
        raise e


def init_fill_repo(
    init_request: schemas.InitBotRequest, 
    repo_name: str, 
    access_token: str,
    settings: Settings,
):
    # Download the code from aws s3 and upload to github
    try:
        # Configure s3 client
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION,
        )
        bucket = s3.Bucket(settings.AWS_BUCKET)
        # Object directory on s3
        object_dir = (
            "templates/"
            + init_request.template_repo
            + "/"
            + init_request.latest_release
        )
        local_dir = (
            "botdata/"
            + init_request.template_repo
            + "/"
            + init_request.latest_release
        )
        for obj in bucket.objects.filter(Prefix=object_dir):
            target = (
                obj.key
                if local_dir is None
                else os.path.join(
                    local_dir, os.path.relpath(obj.key, object_dir)
                )
            )
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
                os.chmod(os.path.dirname(target), 0o777)
            if obj.key[-1] == "/":
                continue
            bucket.download_file(obj.key, target)
            os.chmod(target, 0o777)

            # Upload the code to github
            # Get the base64 content of the file
            with open(target, "rb") as f:
                base64content = base64.b64encode(f.read())
            # Create the file in the repo
            request_url = (
                f"{dependencies.gh_url}/repos/{init_request.github_org}/{repo_name}/contents/{os.path.relpath(target, local_dir)}"
            )
            body = {
                "message": "Adding assessment files...",
                "content": base64content.decode("utf-8"),
                "branch": "main",
            }
            sleep(1)
            response_files = requests.put(
                request_url,
                json=body,
                headers={"Authorization": f"token {access_token}"},
            )
            response_files.raise_for_status()
            print(f"{target} uploaded")
        print("Code downloaded and uploaded to github")
    except Exception as e:  # pragma: no cover
        print(e)
        raise e


def init_create_feedback_branch(
    init_request: schemas.InitBotRequest, repo_name: str, access_token: str
):
    # Create a branch in the repo
    try:

        # Get the SHA of the last commit on the main branch
        request_url = f"{dependencies.gh_url}/repos/{init_request.github_org}/{repo_name}/git/refs/heads/main"
        response = requests.get(
            request_url,
            headers={"Authorization": f"token {access_token}"},
        )
        response.raise_for_status()
        print("Got ref")
        sha2 = response.json()["object"]["sha"]

        # Create the ref
        request_url = f"{dependencies.gh_url}/repos/{init_request.github_org}/{repo_name}/git/refs"
        body = {
            "ref": "refs/heads/feedback",
            "sha": sha2,
        }
        sleep(1)
        response = requests.post(
            request_url,
            json=body,
            headers={"Authorization": f"token {access_token}"},
        )
        response.raise_for_status()
        print("Branch created")
    except Exception as e:  # pragma: no cover
        print(e)
        raise e


def init_delete_tmp(
    init_request: schemas.InitBotRequest,
    repo_name: str,
    access_token: str,
    tmp_sha: str,
):
    # Delete the .tmp file from the main branch
    try:
        request_url = f"{dependencies.gh_url}/repos/{init_request.github_org}/{repo_name}/contents/.tmp"
        body = {
            "message": "Deleted .tmp file",
            "sha": tmp_sha,
            "branch": "main",
        }
        sleep(1)
        response = requests.delete(
            request_url,
            json=body,
            headers={"Authorization": f"token {access_token}"},
        )
        response.raise_for_status()
        print(".tmp deleted")
        # Get the SHA of the last commit on the main branch from the response
        sha = response.json()["commit"]["sha"]
        return sha
    except Exception as e:  # pragma: no cover
        print(e)
        raise e


def init_create_pr(
    init_request: schemas.InitBotRequest, repo_name: str, access_token: str
):
    # Create the pull request from the feedback branch to the main branch
    try:
        request_url = (
            f"{dependencies.gh_url}/repos/{init_request.github_org}/{repo_name}/pulls"
        )
        if init_request.review_required:
            opt_statement = (
                "then you can trigger manual review using the '@brnbot review'"
                " command. The reviewer will be notified and"
                + " will be added to this pull request. They will review your"
                " code :memo: and (probably) will request changes.\n"
                + "7. Once you successfully respond to each reviewer critique"
                " :dart:, they will approve your code and "
            )
            opt_statement2 = (
                "**@brnbot review** - Request a review of your skill assessment"
                + " (only works if you have already passed the automated"
                " tests)\n"
            )
        else:
            opt_statement = ""
            opt_statement2 = ""

        http_repo = (
            dependencies.gh_http + "/" + init_request.github_org + "/" + repo_name
        )
        welcome_message = (
            "Hello, @"
            + init_request.username
            + " :wave:!\n\n"
            + "My name is BRN Bot :robot: and I'm here to help you complete"
            " this "
            + "skill assessment!\n\nWe will use this Pull Request (PR) as a"
            " place to talk :speech_balloon:"
            + "(so please **do not** close or merge the"
            " PR).\n\n<details>\n\n<summary>Instructions</summary>\n\n\n"
            + "<hr>\n\nTo complete the assessment, do the following:\n\n1."
            " Clone the repository"
            + " and open the code in your favorite editor (or open it in the"
            " GitHub editor by navigating"
            + f" to the [repo code]({http_repo}) and pressing the '.' key).\n"
            + "2. Modify the repo code to meet the requirements described in "
            + f" [README.md]({http_repo}/blob/main/README.md).\n3. "
            + "When you are ready, push your changes to the `main` branch and"
            " trigger "
            + "automated tests :white_check_mark: by writing '@brnbot check' in"
            " the comments below. "
            + "I will see your message and run the tests for you :gear: and"
            " will let you know the outcome."
            + "\n5. If the tests fail, examine the "
            + f"output in the [Actions]({http_repo}/actions) tab to see what"
            " went wrong :mag:. Then, update your code "
            + "to fix the problem, push your changes to the `main` branch, and"
            " run '@brnbot check' again.\n"
            + "6. Once your code passess the tests, "
            + opt_statement
            + "then the badge for this assessment will be awarded to you"
            " :trophy:. \n\n"
            + "Once completed, the assessment repo will be archived to prevent"
            " changes :lock:.\n\n<hr>\n\n</details>\n\n"
            + "Here are the **bot commands** you can issue as part of this"
            " assessment:\n\n"
            + "**@brnbot hello** - Say hello to brnbot :wave:.\n"
            + "**@brnbot check** - Check your code using automated tests\n"
            + opt_statement2
            + "**@brnbot help** - Get a list of commands and information about"
            " them\n\n"
            + "Good luck! And have fun! :smile:\n\n<hr>\n\n"
            + "**Note**: If you have any questions or if something isn't"
            " working right,"
            + " please send a message to the '#skill-assessment-wg channel' in"
            " the BRN Slack (however,"
            + " don't share any repo code or answers there).\n\n"
            + "Finally, if you observe any violations of our "
            + "[code of"
            " conduct](https://docs.google.com/document/d/1q06RJbIsyIzLC828A7rBEhtfkujkj9kx7Y118AaWASA/edit?usp=sharing) "
            + "or [academic honesty"
            " policy](https://docs.google.com/document/d/1-Xoko7VDr0lK7olboGQ2CPmEnUTV3WmiDxwQQuGBgiQ/edit),"
            + " please report them to"
            + " codeofconduct@bioresnet.org and someone will respond shortly.\n"
        )
        body = {
            "title": "Feedback",
            "base": "feedback",
            "head": "main",
            "body": welcome_message,
        }
        sleep(1)
        response_pr = requests.post(
            request_url,
            json=body,
            headers={"Authorization": f"token {access_token}"},
        )
        response_pr.raise_for_status()
        print("PR created")
        return http_repo
    except Exception as e:  # pragma: no cover
        print(e)
        raise e


def init_add_collaborator(
    init_request: schemas.InitBotRequest, repo_name: str, access_token: str
):
    # Add the collaborator to the repo
    try:
        request_url = f"{dependencies.gh_url}/repos/{init_request.github_org}/{repo_name}/collaborators/{init_request.username}"
        sleep(1)
        response = requests.put(
            request_url,
            json={},
            headers={"Authorization": f"token {access_token}"},
        )
        response.raise_for_status()
        print("Collaborator added")
    except Exception as e:  # pragma: no cover
        print(e)
        raise e


def approve_assessment(**kwarg_dict):
    # Approve the assessment in the database using API
    request_url = f"{kwarg_dict['CRUD_APP_URL']}/api/approve"
    body = {
        "reviewer_username": kwarg_dict["sender"],
        "latest_commit": get_last_commit(
            owner=kwarg_dict["owner"],
            repo_name=kwarg_dict["repo_name"],
            access_token=kwarg_dict["access_token"],
        )["sha"],
    }
    print(body)
    response = requests.patch(
        request_url,
        json=body,
    )
    try:
        response.raise_for_status()
        text = (
            "Skill assessment approved 🎉. Please check your email for your"
            " badge 😎."
        )
        post_comment(text, **kwarg_dict)
        archive_repo(**kwarg_dict)
        return response
    except requests.exceptions.HTTPError as e:  # pragma: no cover
        msg = response.json()["detail"]
        if msg == "Reviewer cannot be the same as the trainee.":
            msg = "Trainee cannot approve their own skill assessment."
        err = f"**Error**: {msg}" + "\n"
        post_comment(err, **kwarg_dict)
        raise e
    except Exception as e:  # pragma: no cover
        err = (
            f"**Error**: {e}"
            + "\n\n"
            + "**Please contact the maintainer for this bot.**"
        )
        post_comment(err, **kwarg_dict)
        raise e
