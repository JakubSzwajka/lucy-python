import time
import logging
from fastapi import FastAPI, Request
from dotenv import load_dotenv

from agent import Agent

loaded = load_dotenv()

app = FastAPI()


logger = logging.getLogger()
logger.handlers.clear()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Starting agent")


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Right now only Alice App is supported
@app.post("/")
async def chat(request: Request):
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

    start_time = time.time()
    response = await agent.talk(message, user_id, conversation_id)
    end_time = time.time()

    response_time = end_time - start_time
    logger.info(f"Response time: {response_time} seconds")

    return response.to_open_ai_dict()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level="info",
        workers=1,
    )
