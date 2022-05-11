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
        cmd = brnbot.process_cmd(payload)
        print("Command: " + cmd)
    elif utils.is_commit(payload=payload):
        print("is commit")
        response = brnbot.process_commit(payload)
        print("Commit: " + response.json()["commit"])

    return "ok"
