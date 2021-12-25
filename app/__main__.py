import os
import aiohttp

from aiohttp import web

from slack import WebClient
from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp
import requests
import json

routes = web.RouteTableDef()

router = routing.Router()
## test

def post_message_to_slack(text, blocks = None):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': os.environ['SLACK_KEY'],
        'channel': '#project-review',
        'text': text,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):

    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]
    author_url = event.data["issue"]["user"]["html_url"]
    submitted_url = event.data["issue"]["body"]
    post_message_to_slack(f"New <{submitted_url}|project> needs review. Author:<{author_url}|{author}>. "
                          f"Please react to this message to be assigned as author")
    message = f"Thank you for submitting your code for review @{author}. A reviewer will be assigned shortly."
    await gh.post(url, data={"body": message})

@routes.post("/")
async def main(request):
    body = await request.read()

    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    event = sansio.Event.from_http(request.headers, body, secret=secret)
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "TestbotBRN",
                                  oauth_token=oauth_token)
        await router.dispatch(event, gh)
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)