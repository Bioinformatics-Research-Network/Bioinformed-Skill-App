import json
from bot import bot, utils, schemas, auth, const
from fastapi import FastAPI, Body, Header, Depends

app = FastAPI()
brnbot = bot.Bot()


@app.post("/")
def bot(
    payload: dict = Body(...),
    x_github_event: str = Header(...),
    access_tokens: dict=Depends(auth.retrieve_access_tokens),
):

    action = payload["action"]
    event = x_github_event
    print(event + ": " + action)

    if event == "issue_comment" and action == "created":
        # Check if comment is for the bot
        if utils.is_for_bot(payload):
            sender = payload["sender"]["login"]
            message = payload["comment"]["body"]
            print(sender + ": " + message)
            brnbot.process_cmd(
                payload,
                access_tokens=access_tokens
            )
    elif utils.is_pr_commit(payload=payload, event=event):
        print("is PR commit")
        brnbot.process_commit(
            payload,
            access_tokens=access_tokens
        )
    elif utils.is_workflow_run(payload=payload):
        print("is workflow run")
        brnbot.process_done_check(
            payload,
            access_tokens=access_tokens
        )
    return "ok"




@app.post("/init")
def init(
    init_request: schemas.InitBotRequest,
    access_tokens: dict=Depends(auth.retrieve_access_tokens),
):
    print("init")
    gh_url, latest_commit=brnbot.process_init_payload(
        init_request,
        access_tokens=access_tokens
    )
    return {
        "github_url": gh_url,
        "latest_commit": latest_commit,
    }


@app.post("/delete")
def delete(
    delete_request: schemas.DeleteBotRequest,
    access_tokens: dict=Depends(auth.retrieve_access_tokens),
):
    print("delete")
    brnbot.process_delete_repo(
        delete_request,
        access_tokens=access_tokens
    )
    return "ok"
