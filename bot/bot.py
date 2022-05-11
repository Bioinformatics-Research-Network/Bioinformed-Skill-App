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
        self.brn_url = const.brn_url
        self.accept_header = const.accept_header
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


    def parse_payload(self, payload: dict):
        """
        Parse the payload
        """
        install_id = payload["installation"]["id"]
        access_token = self.current_tokens["tokens"][str(install_id)]
        return {
            "sender": payload["sender"]["login"],
            "issue_number": payload["issue"]["number"],
            "owner": payload["repository"]["owner"]["login"],
            "repo_name": payload["repository"]["name"],
            "access_token": access_token,
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


    ## Bot commands ##

    def invalid(self, payload):
        """
        Return an error message
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Invalid command. Try @brnbot help"
        utils.post_comment(text, **kwarg_dict)
        return True


    def hello(self, payload: dict):
        """
        Say hello to the user
        """
        kwarg_dict = self.parse_payload(payload)
        text = f"Hello, @{kwarg_dict['sender']}! 😊"
        utils.post_comment(text, **kwarg_dict)
        return True


    def help(self, payload: dict):
        """
        Return a list of commands
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Available commands: \n" + "\n".join(self.cmds)
        utils.post_comment(text, **kwarg_dict)
        return True


    def init(self, payload: dict):
        """
        Initialize the skill assessment
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Initialized assessment. 🚀"
        
        # Initialize the skill assessment in the database using API
        request_url = f"{self.brn_url}/api/init"
        body = {
            "github_username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
            "latest_commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"], 
                access_token=kwarg_dict["access_token"]
            ),
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
        except Exception as e: # pragma: no cover
            err = f"**Error**: {e}" + "\n\n" + "**Please contact the maintainer for this bot.**"
            utils.post_comment(err, **kwarg_dict)
            raise e

    
    def view(self, payload: dict):
        """
        View the data for this assessment
        """
        kwarg_dict = self.parse_payload(payload)
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
            text = "Hi @" + kwarg_dict["sender"] + ", here is the data you requested 🔥:\n<details>\n\n```JSON\n\n" + json.dumps(response.json(), indent=4) + "\n\n```\n</details>"
            utils.post_comment(text, **kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            err = f"**Error**: {response.json()['detail']}" + "\n\n" + "Re-initialize this assessment with `@brnbot init`."
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e: # pragma: no cover
            err = f"**Error**: {e}" + "\n\n" + "**Please contact the maintainer for this bot.**"
            utils.post_comment(err, **kwarg_dict)
            raise e

    
    def delete(self, payload: dict):
        """
        Delete the assessment
        """
        kwarg_dict = self.parse_payload(payload)
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
        try:
            response.raise_for_status()
            text = "Assessment entry deleted 🗑."
            utils.post_comment(text, **kwarg_dict)
            return response
        except requests.exceptions.HTTPError as e:
            err = f"**Error**: {response.json()['detail']}" + "\n\n" + "Re-initialize this assessment with `@brnbot init`."
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e: # pragma: no cover
            err = f"**Error**: {e}" + "\n\n" + "**Please contact the maintainer for this bot.**"
            utils.post_comment(err, **kwarg_dict)
            raise e
        

    def update(self, payload: dict):
        """
        Update the skill assessment using automated tests via API
        """
        log = " ".join(payload["comment"]["body"].split(" ")[2:])
        print(log)
        kwarg_dict = self.parse_payload(payload)
        request_url = f"{self.brn_url}/api/update"
        body = {
            "github_username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
            "commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"],
                access_token=kwarg_dict["access_token"]
            ),
            "log": {"message": log}
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
            err = f"**Error**: {response.json()['detail']}" + "\n\n" + "Re-initialize this assessment with `@brnbot init`."
            utils.post_comment(err, **kwarg_dict)
            raise e
        except Exception as e: # pragma: no cover
            err = f"**Error**: {e}" + "\n\n" + "**Please contact the maintainer for this bot.**"
            utils.post_comment(err, **kwarg_dict)
            raise e
        
    
    def check(self, payload: dict):
        """
        Check the skill assessment using automated tests via API
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Checking assessment. 🤔"
        # Check the skill assessment in the database using API
        request_url = f"{self.brn_url}/api/check"
        body = {
            "github_username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
            "commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"],
                access_token=kwarg_dict["access_token"]
            ),
        }
        response = requests.post(
            request_url,
            json=body,
        )
        response.raise_for_status()
        utils.post_comment(text, **kwarg_dict)
        return text
        
    
    def review(self, payload: dict):
        """
        Find a reviewer for the assessment via API
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Finding a reviewer. 🔍 This may take up to 48 hours. If you do not receive a reviewer by then, please contact the BRN reviewer team on Slack."
        # Find a reviewer for the assessment in the database using API
        request_url = f"{self.brn_url}/api/review"
        body = {
            "github_username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
            "commit": utils.get_last_commit(
                owner=kwarg_dict["owner"],
                repo_name=kwarg_dict["repo_name"],
                access_token=kwarg_dict["access_token"]
            ),
        }
        response = requests.post(
            request_url,
            json=body,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 422:
                text = response.json()["detail"]
        utils.post_comment(text, **kwarg_dict)
        return text
    

    def approve(self, payload: dict):
        """
        Approve the assessment via API
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Assessment approved. 🤘"
        # Approve the assessment in the database using API
        request_url = f"{self.brn_url}/api/approve"
        body = {
            "reviewer_username": kwarg_dict["sender"],
            "member_username": kwarg_dict["sender"],
            "assessment_name": utils.get_assessment_name(payload),
        }
        response = requests.patch(
            request_url,
            json=body,
        )
        
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 422:
                text = response.json()["detail"]

        utils.post_comment(text, **kwarg_dict)
        return text


    ## Additional commands go here ##
