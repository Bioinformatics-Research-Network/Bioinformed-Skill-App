from fastapi import FastAPI
from app.api import api_endpoints

app = FastAPI(
    title="BRN API",
    description="BRN API",
    version="0.1.0",
    docs_url="/api/docs",
)


@app.get("/")
def root():
    """
    Root api endpoint, has no specific function. Was created to test API.

    :param db: Generator for Session of database

    :returns: json with "Hello World!"
    """
    return {"Hello World!"}


# Router links all the api endpoints to main.py
app.include_router(api_endpoints.router)
