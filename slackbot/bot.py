# Currently following: https://slack.dev/bolt-python/tutorial/getting-started-http
import os
from dotenv import load_dotenv
from slack_bolt import App

# Load variables from .env file
load_dotenv()

# Initializes your app with your bot token and signing secret
app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
)


# Start your app
if __name__ == "__main__":
    # app.start(port=int(os.environ.get("PORT", 3000)))

    # One off message
    app.client.chat_postMessage(
        channel=os.getenv('SLACK_CHANNEL_ID'),
        text="Hello World!"
    )
