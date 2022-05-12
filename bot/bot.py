import os
import json
import requests
from datetime import datetime
from bot import utils, const


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
        self.token_fp = const.token_fp
        self.jwt = const.git_integration.create_jwt()
        self.current_tokens = self.retrieve_access_tokens()

    def retrieve_access_tokens(self):
        """
        Load the access tokens from the file and regenerate if expired
        """
        # Create tokens if file doesn't exist
        if not os.path.exists(self.token_fp):
            utils.get_all_access_tokens(self.installation_ids, jwt=self.jwt)
        with open(self.token_fp, "r") as f:
            current_tokens = json.load(f)
        exp_time = datetime.strptime(current_tokens["expires"], "%Y-%m-%d %H:%M:%S.%f")
        if exp_time < datetime.now():
            utils.get_all_access_tokens(self.installation_ids, jwt=self.jwt)
        with open(self.token_fp, "r") as f:
            current_tokens = json.load(f)
            return current_tokens

    def parse_comment_payload(self, payload: dict):
        """
        Parse the payload for comment on PR
        """
        install_id = payload["installation"]["id"]
        access_token = self.current_tokens["tokens"][str(install_id)]
        return {
            "sender": payload["sender"]["login"],
            "issue_number": payload["issue"]["number"],
            "owner": payload["repository"]["owner"]["login"],
            "repo_name": payload["repository"]["name"],
            "access_token": access_token,
            "pr_url": payload["issue"]["pull_request"]["url"],
        }

    def parse_commit_payload(self, payload: dict):
        """
        Parse the payload for commit on PR
        """
        install_id = payload["installation"]["id"]
        access_token = self.current_tokens["tokens"][str(install_id)]
        return {
            "sender": payload["sender"]["login"],
            "issue_number": payload["number"],
            "owner": payload["repository"]["owner"]["login"],
            "repo_name": payload["repository"]["name"],
            "access_token": access_token,
            "pr_url": payload["pull_request"]["url"],
            "last_commit": payload["pull_request"]["head"]["sha"],
        }

    
    def parse_workflow_run_payload(self, payload: dict):
        """
        Parse the payload for workflow run
        """
        install_id = payload["installation"]["id"]
        access_token = self.current_tokens["tokens"][str(install_id)]
        return {
            "issue_number": payload["workflow_run"]['pull_requests'][0]['number'],
            "owner": payload["repository"]["owner"]["login"],
            "repo_name": payload["repository"]["name"],
            "access_token": access_token,
            "last_commit": payload["workflow_run"]["head_sha"],
            "conclusion": payload["workflow_run"]["conclusion"],
        }


    def process_cmd(self, payload):
        """
        Process the command and run the appropriate bot function

        Returns:
            str: The comment text
        """
        if utils.forbot(payload):
            cmd = payload["comment"]["body"].split(" ")[1]
            return getattr(self, str(cmd), self.invalid)(payload)
        else:
            return None

    def process_commit(self, payload: dict):
        """
        Process the commit and run the update function
        """
        # TODO: This will only capture the HEAD on pushes, not all commits
        kwarg_dict = self.parse_commit_payload(payload)
        log = {"type": "commit"}
        # Update the assessment in the database using API
        request_url = f"{self.brn_url}/api/update"
        body = {
            "github_username": kwarg_dict["sender"],
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
            err = (
                f"**Error**: {response.json()['detail']}"
                + "\n\n"
                + "Re-initialize this assessment with `@brnbot init`."
            )
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

    ## Bot commands ##

    def invalid(self, payload):
        """
        Return an error message
        """
        kwarg_dict = self.parse_comment_payload(payload)
        text = "Invalid command. Try @brnbot help"
        utils.post_comment(text, **kwarg_dict)
        return True

    def hello(self, payload: dict):
        """
        Say hello to the user
        """
        kwarg_dict = self.parse_comment_payload(payload)
        text = f"Hello, @{kwarg_dict['sender']}! 😊"
        print("Hello")
        utils.post_comment(text, **kwarg_dict)
        return True

    def help(self, payload: dict):
        """
        Return a list of commands
        """
        kwarg_dict = self.parse_comment_payload(payload)
        text = "Available commands: \n" + "\n".join(self.cmds)
        utils.post_comment(text, **kwarg_dict)
        return True

    def init(self, payload: dict):
        """
        Initialize the skill assessment
        """
        kwarg_dict = self.parse_comment_payload(payload)
        text = "Initialized assessment. 🚀"

        # Initialize the skill assessment in the database using API
        request_url = f"{self.brn_url}/api/init"
        body = {
            "github_username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
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
            utils.post_comment(text, **kwarg_dict)
            return True
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

    def view(self, payload: dict):
        """
        View the data for this assessment
        """
        kwarg_dict = self.parse_comment_payload(payload)
        # Get the assessment data from the database using API
        request_url = f"{self.brn_url}/api/view"
        body = {
            "github_username": kwarg_dict["sender"],
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
            err = (
                f"**Error**: {response.json()['detail']}"
                + "\n\n"
                + "Re-initialize this assessment with `@brnbot init`."
            )
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

    def delete(self, payload: dict):
        """
        Delete the assessment
        """
        kwarg_dict = self.parse_comment_payload(payload)
        try:
            # Remove the reviewer if there is one
            reviewer_response = utils.get_reviewer(**kwarg_dict)
            reviewer_response.raise_for_status()
            if reviewer_response.json()["users"] != []:
                reviewer = reviewer_response.json()["users"][0]["login"]
                remove_response = utils.remove_reviewer(reviewer, **kwarg_dict)
                remove_response.raise_for_status()
            # Delete the assessment from the database using API
            request_url = f"{self.brn_url}/api/delete"
            body = {
                "github_username": kwarg_dict["sender"],
                "assessment_name": utils.get_assessment_name(payload),
            }
            response = requests.post(
                request_url,
                json=body,
            )
            response.raise_for_status()
            # Notify on successful deletion
            text = "Assessment entry deleted 🗑."
            utils.post_comment(text, **kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            err = (
                f"**Error**: {response.json()['detail']}"
                + "\n\n"
                + "Re-initialize this assessment with `@brnbot init`."
            )
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e:  # pragma: no cover
            err = (
                f"**Error**: {str(e)}"
                + "\n\n"
                + "**Please contact the maintainer for this bot.**"
            )
            utils.post_comment(err, **kwarg_dict)
            raise e

    # TODO: Remove public access to this function
    def update(self, payload: dict):
        """
        Update the skill assessment using automated tests via API

        Internal use only
        """
        log = " ".join(payload["comment"]["body"].split(" ")[2:])
        kwarg_dict = self.parse_comment_payload(payload)
        request_url = f"{self.brn_url}/api/update"
        body = {
            "github_username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
            "latest_commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"],
                access_token=kwarg_dict["access_token"],
            )["sha"],
            "log": {"message": log},
        }
        response = requests.patch(
            request_url,
            json=body,
        )
        try:
            response.raise_for_status()
            text = "Assessment entry updated with message: \n" + log
            utils.post_comment(text, **kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            err = (
                f"**Error**: {response.json()['detail']}"
                + "\n\n"
                + "Re-initialize this assessment with `@brnbot init`."
            )
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

    def check(self, payload: dict):
        """
        Check the skill assessment using automated tests via API
        """
        kwarg_dict = self.parse_comment_payload(payload)      
        actions_url = f"{self.gh_http}/{kwarg_dict['owner']}/{kwarg_dict['repo_name']}/actions/"    
        try:
            response = utils.dispatch_workflow(**kwarg_dict)
            response.raise_for_status()
            text = "Automated checks ✅ in progress ⏳. View them here: " + actions_url
            utils.post_comment(text, **kwarg_dict)
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


    def process_done_check(self, payload: dict):
        kwarg_dict = self.parse_workflow_run_payload(payload)
        actions_url = f"{self.gh_http}/{kwarg_dict['owner']}/{kwarg_dict['repo_name']}/actions/" 
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
        body = {
            "latest_commit": latest_commit,
            "passed": passed
        }
        response = requests.post(
            request_url,
            json=body,
        )
        try:
            response.raise_for_status()
            if passed:
                text = "Checks have **passed** 💯. You can now request manual review with `@brnbot review`."
            else:
                text = "Checks have **failed** 💥. Please check the logs for more information: " + actions_url
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


    def review(self, payload: dict):
        """
        Find a reviewer for the assessment via API
        """
        kwarg_dict = self.parse_comment_payload(payload)
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

    def unreview(self, payload: dict):
        """
        Remove a reviewer for the assessment via API
        """
        kwarg_dict = self.parse_comment_payload(payload)
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

    def approve(self, payload: dict):
        """
        Approve the assessment via API
        """
        kwarg_dict = self.parse_comment_payload(payload)
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

    ## Additional commands go here ##
    # Unapprove
