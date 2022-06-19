from bot import utils, schemas, auth
from bot.dependencies import get_settings, get_db, Settings
from bot.bot import Bot
from sqlalchemy.orm import Session
from fastapi import FastAPI, Body, Header, Depends, HTTPException

app = FastAPI()

@app.post("/")
def bot(
    payload: dict = Body(...),
    x_github_event: str = Header(...),
    access_tokens: dict = Depends(auth.retrieve_access_tokens),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> str:

    # Init the bot
    brnbot = Bot(settings=settings)

    try:
        action = payload["action"]
    except KeyError:
        # Raise HTTP 422 if the payload is missing the action
        raise HTTPException(
            status_code=422,
            detail="The payload is missing the action",
        )

    event = x_github_event
    print(event + ": " + action)

    if event == "issue_comment" and action == "created":
        # Check if comment is for the bot and the repo is valid
        if utils.is_for_bot(payload) and utils.is_valid_repo(payload, db=db):
            sender = payload["sender"]["login"]
            message = payload["comment"]["body"]
            print(sender + ": " + message)
            brnbot.process_cmd(payload, access_tokens=access_tokens)
    elif utils.is_pr_commit(payload=payload, event=event):
        print("is PR commit")
        brnbot.process_commit(payload, access_tokens=access_tokens)
    elif utils.is_workflow_run(payload=payload):
        print("is workflow run")
        brnbot.process_done_check(payload, access_tokens=access_tokens)
    return "ok"


@app.post("/init")
def init(
    init_request: schemas.InitBotRequest,
    access_tokens: dict = Depends(auth.retrieve_access_tokens),
    settings: Settings = Depends(get_settings),
) -> dict:

    # Init the bot
    brnbot = Bot(settings=settings)

    print("init")
    gh_url, latest_commit = brnbot.process_init_payload(
        init_request, access_tokens=access_tokens
    )
    return {
        "github_url": gh_url,
        "latest_commit": latest_commit,
    }


@app.post("/delete")
def delete(
    delete_request: schemas.DeleteBotRequest,
    access_tokens: dict = Depends(auth.retrieve_access_tokens),
    settings: Settings = Depends(get_settings),
) -> str:

    # Init the bot
    brnbot = Bot(settings=settings)

    print("delete")
    brnbot.process_delete_repo(delete_request, access_tokens=access_tokens)
    return "ok"


@app.get("/")
def root() -> dict:
    return {"message": "Hello World"}
