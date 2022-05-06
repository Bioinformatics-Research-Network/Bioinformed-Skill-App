from bot.utils import *
from bot.const import *
from bot.bot import *
from fastapi import FastAPI, Body

app = FastAPI()

brnbot = Bot()

@app.post("/")
def bot(payload: dict = Body(...)):

    print("Processing payload")
    sender = payload["sender"]["login"]
    print(sender)

    if brnbot.forbot(payload):
        cmd = brnbot.process_cmd(payload)
        print(cmd)

    return "ok"
