from .const import *
from .utils import *


class Bot:
    """
    Bot class
    """

    def __init__(self):
        self.base_url = base_url
        self.accept_header = accept_header
        self.installation_ids = installation_ids
        self.cmds = cmds
        self.token_fp = token_fp
        self.jwt = git_integration.create_jwt()
        self.current_tokens = self.retrieve_access_tokens()

    def retrieve_access_tokens(self):
        """
        Load the access tokens from the file and regenerate if expired
        """
        # Create tokens if file doesn't exist
        print("Loading access tokens")
        if not os.path.exists(self.token_fp):
            get_all_access_tokens(self.installation_ids, jwt=self.jwt)
        with open(self.token_fp, "r") as f:
            current_tokens = json.load(f)
        exp_time = datetime.strptime(current_tokens["expires"], "%Y-%m-%d %H:%M:%S.%f")
        if exp_time < datetime.now():
            get_all_access_tokens(self.installation_ids, jwt=self.jwt)
        with open(self.token_fp, "r") as f:
            current_tokens = json.load(f)
            return current_tokens

    def post_comment(self, text: str, **kwargs):
        """
        Post a comment to the issue
        """
        headers = {
            "Authorization": f"Bearer {kwargs['access_token']}",
            "Accept": self.accept_header,
        }

        request_url = f"{self.base_url}/repos/{kwargs['owner']}/{kwargs['repo_name']}/issues/{kwargs['issue_number']}/comments"
        response = requests.post(
            request_url,
            headers=headers,
            json={"body": text},
        )
        return response.json()

    # def retrieve_last_comment(self, payload: dict):
    #     """
    #     Retrieve the last comment
    #     """

    #     print("Getting last comment")

    #     kwarg_dict = self.parse_payload(payload)
    #     headers = {
    #         "Authorization": f"Bearer {kwarg_dict['access_token']}",
    #         "Accept": self.accept_header,
    #     }
    #     request_url = f"{self.base_url}/repos/{kwarg_dict['owner']}/{kwarg_dict['repo_name']}/issues/{kwarg_dict['issue_number']}/comments"
    #     response = requests.get(request_url, headers=headers)
    #     comments = response.json()
    #     if len(comments) > 0:
    #         return comments[-1]["body"]
    #     else:
    #         return None

    def process_cmd(self, payload):
        """
        Process the command and run the appropriate bot function

        Returns:
            str: The comment text
        """
        if self.forbot(payload):
            cmd = payload["comment"]["body"].split(" ")[1]
            return getattr(self, str(cmd), self.invalid)(payload)

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

    def forbot(self, payload: dict):
        """
        Check if the payload is for the bot
        """
        return payload["comment"]["body"].startswith("@brnbot")

    ## Bot commands ##

    def invalid(self, payload):
        """
        Return an error message
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Invalid command. Try @brnbot help"
        self.post_comment(text, **kwarg_dict)
        return text

    def hello(self, payload: dict):
        """
        Say hello to the user
        """
        kwarg_dict = self.parse_payload(payload)
        text = f"Hello, @{kwarg_dict['sender']}! 😊"
        self.post_comment(text, **kwarg_dict)
        return text

    def help(self, payload: dict):
        """
        Return a list of commands
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Available commands: \n" + "\n".join(cmds)
        self.post_comment(text, **kwarg_dict)
        return text

    ## Additional commands go here ##
