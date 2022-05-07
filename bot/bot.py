from .const import *
from .utils import *


class Bot:
    """
    Bot class
    """

    def __init__(self):
        self.gh_url = gh_url
        self.brn_url = brn_url
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
        if self.forbot(payload):
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
        post_comment(text, **kwarg_dict)
        return text

    def hello(self, payload: dict):
        """
        Say hello to the user
        """
        kwarg_dict = self.parse_payload(payload)
        text = f"Hello, @{kwarg_dict['sender']}! 😊"
        post_comment(text, **kwarg_dict)
        return text

    def help(self, payload: dict):
        """
        Return a list of commands
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Available commands: \n" + "\n".join(cmds)
        post_comment(text, **kwarg_dict)
        return text


    def init(self, payload: dict):
        """
        Initialize the skill assessment
        """
        kwarg_dict = self.parse_payload(payload)
        text = "Initialized assessment. 🚀"
        print("Initializing assessment")
        
        # Initialize the skill assessment in the database using API
        request_url = f"{self.brn_url}/api/init_assessment"
        body = {
            "user": {
                "github_username": kwarg_dict["sender"],
            },
            "assessment_tracker": {
                "assessment_name": get_assessment_name(payload),
                "latest_commit": get_last_commit(**kwarg_dict),
            }
        }
        print(body)
        response = requests.post(
            request_url,
            json=body,
        )
        print(response.json())
        post_comment(text, **kwarg_dict)
        return text

    ## Additional commands go here ##
