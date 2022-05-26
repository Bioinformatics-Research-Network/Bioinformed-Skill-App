import os
import json
import re
from time import sleep
import requests
import boto3
from datetime import datetime
from bot import utils, const, schemas
import base64


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
            print("Getting jwt")
            self.jwt = const.git_integration.create_jwt()
            print("Getting tokens")
            utils.get_all_access_tokens(self.installation_ids, jwt=self.jwt)
        with open(self.token_fp, "r") as f:
            current_tokens = json.load(f)
        exp_time = datetime.strptime(current_tokens["expires"], "%Y-%m-%d %H:%M:%S.%f")
        if exp_time < datetime.now():
            print("Getting jwt")
            self.jwt = const.git_integration.create_jwt()
            print("Getting tokens")
            utils.get_all_access_tokens(self.installation_ids, jwt=self.jwt)
        with open(self.token_fp, "r") as f:
            current_tokens = json.load(f)
            return current_tokens

    def check_tokens(self):
        """
        Check whether the tokens are up to date or not
        """
        if not os.path.exists(self.token_fp):
            print("Getting jwt")
            self.jwt = const.git_integration.create_jwt()
            print("Getting tokens")
            self.retrieve_access_tokens(self.installation_ids, jwt=self.jwt)
        with open(self.token_fp, "r") as f:
            current_tokens = json.load(f)
        exp_time = datetime.strptime(current_tokens["expires"], "%Y-%m-%d %H:%M:%S.%f")
        if exp_time < datetime.now():
            print("Getting jwt")
            self.jwt = const.git_integration.create_jwt()
            print("Getting tokens")
            self.retrieve_access_tokens()

    def parse_comment_payload(self, payload: dict):
        """
        Parse the payload for comment on PR
        """
        self.check_tokens()
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
        self.check_tokens()
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
        self.check_tokens()
        install_id = payload["installation"]["id"]
        access_token = self.current_tokens["tokens"][str(install_id)]
        return {
            "issue_number": payload["workflow_run"]["pull_requests"][0]["number"],
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
        if utils.is_for_bot(payload):
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

    def parse_new_repo_payload(self, payload: dict):
        """
        Parse the payload for new repo
        """
        self.check_tokens()
        print("Parsing new repo payload")
        install_id = payload["installation"]["id"]
        access_token = self.current_tokens["tokens"][str(install_id)]
        ghbot_message = payload["pull_request"]["body"]
        trainee = re.search(r"@(.*?)$", ghbot_message).group(1)
        return {
            "owner": payload["repository"]["owner"]["login"],
            "repo_name": payload["repository"]["name"],
            "issue_number": payload["pull_request"]["number"],
            "trainee": trainee,
            "repo_url": payload["repository"]["html_url"],
            "access_token": access_token,
        }

    def process_new_repo(self, payload):
        """
        Process a new skill assessment repo
        """
        kwarg_dict = self.parse_new_repo_payload(payload)
        print(kwarg_dict)
        text = "Initialized assessment. 🚀"

        # Initialize the skill assessment in the database using API
        request_url = f"{self.brn_url}/api/init"
        body = {
            "username": kwarg_dict["trainee"],
            "assessment_name": utils.get_assessment_name(payload),
            "latest_commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"],
                access_token=kwarg_dict["access_token"],
            )["sha"],
            "repo_owner": kwarg_dict["owner"],
            "repo_name": kwarg_dict["repo_name"],
            "pr_number": kwarg_dict["issue_number"],
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

    def process_init_payload(self, init_request: schemas.InitBotRequest):
        """
        Process the init payload
        """
        self.check_tokens()
        access_token = self.current_tokens["tokens"][str(init_request.install_id)]

        # Create a repo name
        repo_name = init_request.repo_prefix + init_request.username

        # Create the repo in the database using GitHub API
        request_url = f"{const.gh_url}/orgs/{init_request.github_org}/repos"
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
        try:
            sleep(1)
            response = requests.post(
                request_url,
                json=body,
                headers={"Authorization": f"token {access_token}"},
            )
            response.raise_for_status()
            print("Repo created")
        except requests.exceptions.HTTPError as e:
            print(e)
            raise e

        try:
            # Put an empty README in the repo
            request_url = f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}/contents/.tmp"
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
        except Exception as e:
            print(e)
            raise e

        # Download the code from aws s3 and upload to github
        try:
            # Configure s3 client
            s3 = boto3.resource(
                "s3",
                aws_access_key_id=const.settings.AWS_ACCESS_KEY,
                aws_secret_access_key=const.settings.AWS_SECRET_KEY,
                region_name=const.settings.AWS_REGION,
            )
            bucket = s3.Bucket(const.settings.AWS_BUCKET)
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
                    else os.path.join(local_dir, os.path.relpath(obj.key, object_dir))
                )
                if not os.path.exists(os.path.dirname(target)):
                    os.makedirs(os.path.dirname(target))
                if obj.key[-1] == "/":
                    continue
                bucket.download_file(obj.key, target)

                # Upload the code to github
                # Get the base64 content of the file
                with open(target, "rb") as f:
                    base64content = base64.b64encode(f.read())
                # Create the file in the repo
                request_url = f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}/contents/{os.path.relpath(target, local_dir)}"
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
        except Exception as e:
            print(e)
            raise e

        # Create a branch in the repo
        try:

            # Get the SHA of the last commit on the main branch
            request_url = f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}/git/refs/heads/main"
            response = requests.get(
                request_url,
                headers={"Authorization": f"token {access_token}"},
            )
            response.raise_for_status()
            print("Got ref")
            sha2 = response.json()["object"]["sha"]

            # Create the ref
            request_url = (
                f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}/git/refs"
            )
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
        except Exception as e:
            print(e)
            raise e

        # Delete the .tmp file from the main branch
        try:
            request_url = f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}/contents/.tmp"
            body = {
                "message": "Deleted .tmp file",
                "sha": sha,
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
        except Exception as e:
            print(e)
            raise e

        # Create the pull request from the feedback branch to the main branch
        try:
            request_url = (
                f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}/pulls"
            )
            welcome_message = (
                "Hello, @" + init_request.username + " :wave:!\n"
                + "My name is BRN Bot :robot: and I'm here to help you with your "
                + "skill assessment today!\n"
                + "Here are the commands you can use:\n\n"
                + "@brnbot help - Get a list of commands\n"
                + "@brnbot check - Check your skill assessment using automated tests\n"
                + "@brnbot review - Request a review of your skill assessment (only works if you have already passed the automated tests)\n"
                + "@brnbot view - Get our data on your skill assessment\n\n"
                + "Good luck! And have fun! :smile:"
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
        except Exception as e:
            print(e)
            raise e

        # Add the collaborator to the repo
        try:
            request_url = f"{const.gh_url}/repos/{init_request.github_org}/{repo_name}/collaborators/{init_request.username}"
            sleep(1)
            response = requests.put(
                request_url,
                json={},
                headers={"Authorization": f"token {access_token}"},
            )
            response.raise_for_status()
            print("Collaborator added")
        except Exception as e:
            print(e)
            raise e

        return True

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
        print(kwarg_dict)
        text = "Initialized assessment. 🚀"

        # Initialize the skill assessment in the database using API
        request_url = f"{self.brn_url}/api/init"
        body = {
            "username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
            "latest_commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"],
                access_token=kwarg_dict["access_token"],
            )["sha"],
            "repo_owner": kwarg_dict["owner"],
            "repo_name": kwarg_dict["repo_name"],
            "pr_number": kwarg_dict["issue_number"],
        }
        print(body)
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
                "username": kwarg_dict["sender"],
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
            err = f"**Error**: {response.json()['detail']}"
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
            "username": kwarg_dict["sender"],
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

    def check(self, payload: dict):
        """
        Check the skill assessment using automated tests via API
        """
        kwarg_dict = self.parse_comment_payload(payload)
        actions_url = (
            f"{self.gh_http}/{kwarg_dict['owner']}/{kwarg_dict['repo_name']}/actions/"
        )
        try:
            response = utils.dispatch_workflow(**kwarg_dict)
            response.raise_for_status()
            text = "Automated checks ✅ in progress ⏳. View them here: " + actions_url
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

    def process_done_check(self, payload: dict):
        kwarg_dict = self.parse_workflow_run_payload(payload)
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
                    "Checks have **failed** 💥. Please check the logs for more information: "
                    + actions_url
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
