import os
import json
import requests
from datetime import datetime
from bot import utils, const, schemas


class Bot:
    """
    Bot class
    """

    def __init__(self):
        self.gh_url = const.gh_url
        self.gh_http = const.gh_http
        self.brn_url = const.brn_url
        self.accept_header = const.accept_header
        self.worlflow_filename = const.workflow_filename
        self.installation_ids = const.installation_ids
        self.cmds = const.cmds

    def parse_comment_payload(self, payload: dict, access_tokens: dict):
        """
        Parse the payload for comment on PR
        """
        install_id = payload["installation"]["id"]
        access_token = access_tokens["tokens"][str(install_id)]
        return {
            "sender": payload["sender"]["login"],
            "issue_number": payload["issue"]["number"],
            "owner": payload["repository"]["owner"]["login"],
            "repo_name": payload["repository"]["name"],
            "access_token": access_token,
            "pr_url": payload["issue"]["pull_request"]["url"],
        }

    def parse_commit_payload(self, payload: dict, access_tokens: dict):
        """
        Parse the payload for commit on PR
        """
        install_id = payload["installation"]["id"]
        access_token = access_tokens["tokens"][str(install_id)]
        return {
            "sender": payload["sender"]["login"],
            "issue_number": payload["number"],
            "owner": payload["repository"]["owner"]["login"],
            "repo_name": payload["repository"]["name"],
            "access_token": access_token,
            "pr_url": payload["pull_request"]["url"],
            "last_commit": payload["pull_request"]["head"]["sha"],
        }

    def parse_workflow_run_payload(self, payload: dict, access_tokens: dict):
        """
        Parse the payload for workflow run
        """
        install_id = payload["installation"]["id"]
        access_token = access_tokens["tokens"][str(install_id)]
        return {
            "issue_number": payload["workflow_run"]["pull_requests"][0]["number"],
            "owner": payload["repository"]["owner"]["login"],
            "repo_name": payload["repository"]["name"],
            "access_token": access_token,
            "last_commit": payload["workflow_run"]["head_sha"],
            "conclusion": payload["workflow_run"]["conclusion"],
        }

    def process_cmd(self, payload: dict, access_tokens: dict):
        """
        Process the command and run the appropriate bot function

        Returns:
            str: The comment text
        """
        if utils.is_for_bot(payload):
            cmd = payload["comment"]["body"].split(" ")[1]
            return getattr(self, str(cmd), self.invalid)(payload, access_tokens=access_tokens)
        else:
            return None

    def process_commit(self, payload: dict, access_tokens: dict):
        """
        Process the commit and run the update function
        """
        # TODO: This will only capture the HEAD on pushes, not all commits
        kwarg_dict = self.parse_commit_payload(payload, access_tokens=access_tokens)
        log = {"type": "commit"}
        print(kwarg_dict["sender"])
        # Update the assessment in the database using API
        request_url = f"{self.brn_url}/api/update"
        body = {
            "username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
            "latest_commit": kwarg_dict["last_commit"],
            "log": {"message": log},
        }
        response = requests.patch(
            request_url,
            json=body,
        )
        try:
            response.raise_for_status()
            text = (
                "Commit detected: "
                + kwarg_dict["last_commit"]
                + "\n\nRun `@brnbot check` to test your code."
            )
            utils.post_comment(text, **kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            err = f"**Error**: {response.json()['detail']}"
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e:  # pragma: no cover
            err = (
                f"**Error**: {e}"
                + "\n\n"
                + "**Please contact the maintainer for this bot.**"
            )
            utils.post_comment(err, **kwarg_dict)
            raise e


    def process_init_payload(self, init_request: schemas.InitBotRequest, access_tokens: dict):
        """
        Process the init payload
        """
        access_token = access_tokens["tokens"][str(init_request.install_id)]

        # Create a repo name
        repo_name = init_request.repo_prefix + init_request.username

        # Create a repo, and upload the code, and create a branch
        print(f"Creating repo: {repo_name}")
        tmp_sha = utils.init_create_repo(init_request=init_request, repo_name=repo_name, access_token=access_token)
        print(f"Filling repo: {repo_name}")
        utils.init_fill_repo(init_request, repo_name=repo_name, access_token=access_token)
        print(f"Creating feedback branch: {repo_name}")
        utils.init_create_feedback_branch(init_request, repo_name=repo_name, access_token=access_token)
        print(f"Deleting .tmp file: {repo_name}")
        latest_commit=utils.init_delete_tmp(init_request, repo_name=repo_name, access_token=access_token, tmp_sha=tmp_sha)
        print(f"Creating PR: {repo_name}")
        http_repo=utils.init_create_pr(init_request, repo_name=repo_name, access_token=access_token)
        print(f"Adding collaborator: {repo_name}")
        utils.init_add_collaborator(init_request, repo_name=repo_name, access_token=access_token)

        return http_repo, latest_commit

    
    def process_delete_repo(self, delete_request: schemas.DeleteBotRequest, access_tokens: dict):
        """
        Process the delete repo payload
        """
        access_token = access_tokens["tokens"][str(delete_request.install_id)]
        repo_name = delete_request.repo_prefix + delete_request.username
        utils.delete_repo(delete_request=delete_request, repo_name=repo_name, access_token=access_token)
        return True

    ## Bot commands ##

    def invalid(self, payload: dict, access_tokens: dict):
        """
        Return an error message
        """
        kwarg_dict = self.parse_comment_payload(payload, access_tokens=access_tokens)
        text = "Invalid command. Try @brnbot help"
        utils.post_comment(text, **kwarg_dict)
        return True

    def hello(self, payload: dict, access_tokens: dict):
        """
        Say hello to the user
        """
        kwarg_dict = self.parse_comment_payload(payload, access_tokens=access_tokens)
        text = f"Hello, @{kwarg_dict['sender']}! 😊"
        print("Hello")
        utils.post_comment(text, **kwarg_dict)
        return True

    def help(self, payload: dict, access_tokens: dict):
        """
        Return a list of commands
        """
        kwarg_dict = self.parse_comment_payload(payload, access_tokens=access_tokens)
        text = "Available commands: \n" + "\n".join(self.cmds)
        utils.post_comment(text, **kwarg_dict)
        return True


    def view(self, payload: dict, access_tokens: dict):
        """
        View the data for this assessment
        """
        kwarg_dict = self.parse_comment_payload(payload, access_tokens=access_tokens)
        # Get the assessment data from the database using API
        request_url = f"{self.brn_url}/api/view"
        body = {
            "username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
        }
        response = requests.get(
            request_url,
            json=body,
        )
        try:
            response.raise_for_status()
            text = (
                "Hi @"
                + kwarg_dict["sender"]
                + ", here is the data you requested 🔥:\n<details>\n\n```JSON\n\n"
                + json.dumps(response.json(), indent=4)
                + "\n\n```\n</details>"
            )
            utils.post_comment(text, **kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            err = f"**Error**: {response.json()['detail']}"
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e:  # pragma: no cover
            err = (
                f"**Error**: {e}"
                + "\n\n"
                + "**Please contact the maintainer for this bot.**"
            )
            utils.post_comment(err, **kwarg_dict)
            raise e


    def check(self, payload: dict, access_tokens: dict):
        """
        Check the skill assessment using automated tests via API
        """
        kwarg_dict = self.parse_comment_payload(payload, access_tokens=access_tokens)
        actions_url = (
            f"{self.gh_http}/{kwarg_dict['owner']}/{kwarg_dict['repo_name']}/actions/"
        )
        try:
            response = utils.dispatch_workflow(**kwarg_dict)
            response.raise_for_status()
            text = "Automated checks ✅ in progress ⏳. View them here: [`link`](" + actions_url + ")"
            utils.post_comment(text, **kwarg_dict)
            return True
        except requests.exceptions.HTTPError as e:
            err = f"**Error**: {str(e)}" + "\n"
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e:  # pragma: no cover
            err = (
                f"**Error**: {e}"
                + "\n\n"
                + "**Please contact the maintainer for this bot.**"
            )
            utils.post_comment(err, **kwarg_dict)
            raise e

    def process_done_check(self, payload: dict, access_tokens: dict):
        kwarg_dict = self.parse_workflow_run_payload(payload, access_tokens=access_tokens)
        actions_url = (
            f"{self.gh_http}/{kwarg_dict['owner']}/{kwarg_dict['repo_name']}/actions/"
        )
        print(kwarg_dict)

        # Confirm that latest commit is the same as the one in the database
        latest_commit = utils.get_last_commit(
            owner=kwarg_dict["owner"],
            repo_name=kwarg_dict["repo_name"],
            access_token=kwarg_dict["access_token"],
        )["sha"]
        if latest_commit != kwarg_dict["last_commit"]:
            msg = (
                "Checks are complete 🔥! However, the current commit has changed since the "
                + "checks were initiated. Re-run the checks with `@brnbot check`."
            )
            utils.post_comment(msg, **kwarg_dict)
            return None

        # Check the skill assessment in the database using API
        passed = kwarg_dict["conclusion"] != "failure"
        request_url = f"{self.brn_url}/api/check"
        body = {"latest_commit": latest_commit, "passed": passed}
        response = requests.post(
            request_url,
            json=body,
        )
        try:
            response.raise_for_status()
            if passed:
                text = "Checks have **passed** 😎. You can now request manual review with `@brnbot review`."
            else:
                text = (
                    "Checks have **failed** 💥. Please check the logs for more information: [`link`]("
                    + actions_url + ")"
                )
            utils.post_comment(text, **kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            err = f"**Error**: {response.json()['detail']}" + "\n"
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e:  # pragma: no cover
            err = (
                f"**Error**: {e}"
                + "\n\n"
                + "**Please contact the maintainer for this bot.**"
            )
            utils.post_comment(err, **kwarg_dict)
            raise e

    def review(self, payload: dict, access_tokens: dict):
        """
        Find a reviewer for the assessment via API
        """
        kwarg_dict = self.parse_comment_payload(payload, access_tokens=access_tokens)
        # Find a reviewer for the assessment in the database using API
        request_url = f"{self.brn_url}/api/review"
        body = {
            "latest_commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"],
                access_token=kwarg_dict["access_token"],
            )["sha"],
        }
        response = requests.post(
            request_url,
            json=body,
        )
        try:
            response.raise_for_status()
            reviewer = response.json()["reviewer_username"]
            utils.assign_reviewer(reviewer, **kwarg_dict)
            text = (
                "Reviewer assigned 🔥. Welcome @"
                + response.json()["reviewer_username"]
                + "!"
            )
            utils.post_comment(text, **kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            err = f"**Error**: {response.json()['detail']}" + "\n"
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e:  # pragma: no cover
            err = (
                f"**Error**: {e}"
                + "\n\n"
                + "**Please contact the maintainer for this bot.**"
            )
            utils.post_comment(err, **kwarg_dict)
            raise e

    def unreview(self, payload: dict, access_tokens: dict):
        """
        Remove a reviewer for the assessment via API
        """
        kwarg_dict = self.parse_comment_payload(payload, access_tokens=access_tokens)
        # Remove a reviewer from the github api
        response = utils.get_reviewer(**kwarg_dict)
        try:
            response.raise_for_status()
            reviewer_username = response.json()["users"][0]["login"]
            response_remove = utils.remove_reviewer(reviewer_username, **kwarg_dict)
            response_remove.raise_for_status()
            return response_remove
        except requests.exceptions.HTTPError as e:
            err = f"**Error**: {response.json()['detail']}" + "\n"
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e:
            err = (
                f"**Error**: {e}"
                + "\n\n"
                + "**Please contact the maintainer for this bot.**"
            )
            utils.post_comment(err, **kwarg_dict)
            raise e

    def approve(self, payload: dict, access_tokens: dict):
        """
        Approve the assessment via API
        """
        kwarg_dict = self.parse_comment_payload(payload, access_tokens=access_tokens)
        # Approve the assessment in the database using API
        request_url = f"{self.brn_url}/api/approve"
        body = {
            "reviewer_username": kwarg_dict["sender"],
            "latest_commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"],
                access_token=kwarg_dict["access_token"],
            )["sha"],
        }
        response = requests.patch(
            request_url,
            json=body,
        )
        try:
            response.raise_for_status()
            text = (
                "Skill assessment approved 🎉. Please check your email for your badge 😎."
            )
            utils.post_comment(text, **kwarg_dict)
            utils.archive_repo(**kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            msg = response.json()["detail"]
            if msg == "Reviewer cannot be the same as the trainee.":
                msg = "Trainee cannot approve their own skill assessment."
            err = f"**Error**: {msg}" + "\n"
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e:  # pragma: no cover
            err = (
                f"**Error**: {e}"
                + "\n\n"
                + "**Please contact the maintainer for this bot.**"
            )
            utils.post_comment(err, **kwarg_dict)
            raise e
