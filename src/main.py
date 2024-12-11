from fastapi import FastAPI, Request
from dotenv import load_dotenv

from agent import Agent

loaded = load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Right now only Alice App is supported
@app.post("/")
async def create_task(request: Request):
    agent = Agent()
    data = await request.json()
    conversation_id = data.get("conversation_id")
    user_id = data.get("user_id")
    messages = data.get("messages")
    message = messages[
        -1
    ].get(
        "content"
    )  # taking the last message since the conversation history should be stored on server side
    return agent.talk(message, user_id, conversation_id).to_open_ai_dict()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
