import json
from bot import bot, utils, schemas
from fastapi import FastAPI, Body, Header

app = FastAPI()
brnbot = bot.Bot()


@app.post("/")
def bot(
    payload: dict = Body(...),
    x_github_event: str = Header(...),
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
            brnbot.process_cmd(payload)
    elif utils.is_pr_commit(payload=payload, event=event):
        print("is PR commit")
        brnbot.process_commit(payload)
    elif utils.is_workflow_run(payload=payload):
        print("is workflow run")
        brnbot.process_done_check(payload)
    elif utils.is_assessment_init(payload=payload, event=event):
        print("is new repo")
        brnbot.process_new_repo(payload)
    elif utils.is_delete_repo(payload=payload, event=event):
        print("is delete repo")
        # brnbot.process_delete_repo(payload)

    return "ok"




@app.post("/init")
def init(
    init_request: schemas.InitBotRequest,
):
    print("init")
    brnbot.process_init(init_request)
    return "ok"



