from urllib import request
from bot import bot, utils
from fastapi import FastAPI, Body

app = FastAPI()
brnbot = bot.Bot()


@app.post("/")
def bot(payload: dict = Body(...)):

    print("Processing payload")

    if utils.forbot(payload):
        sender = payload["sender"]["login"]
        message = payload["comment"]["body"]
        print(sender)
        print(message)
        brnbot.process_cmd(payload)
    elif utils.is_commit(payload=payload):
        print("is commit")
        brnbot.process_commit(payload)
    elif utils.is_workflow_run(payload=payload):
        print("is workflow run")
        brnbot.process_done_check(payload)

    return "ok"
