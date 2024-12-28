from datetime import datetime
import json
import logging
from typing import AsyncGenerator
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import StreamingResponse
from psycopg_pool import AsyncConnectionPool
from langchain_core.messages import AIMessageChunk
from agents.lucy.graph import Lucy
from config import GlobalConfig

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from agents import Agents
from agents.services.google_calendar_manager import GoogleCalendarManager
from agents.services.google_drive_manager import GoogleDriveManager

# loaded = load_dotenv('/Users/kuba.szwajka/DEV/priv/lucy-all/lucy-python/.env')
loaded = load_dotenv()

logger = logging.getLogger()
logger.handlers.clear()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


USER_ID = "kuba"

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }
    async with AsyncConnectionPool(
        GlobalConfig.get_db_url(), kwargs=connection_kwargs
    ) as pool:
        await pool.wait()  # optional
        yield {"pool": pool}


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/calendar-login")
async def calendar_login(request: Request):
    manager = GoogleCalendarManager()
    return {"url": "check logs"}


@app.get("/drive-login")
async def drive_login(request: Request):
    manager = GoogleDriveManager()
    return {"url": "check logs"}

@app.post("/ai")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")
    conversation_id = data.get("conversation_id")
    user_id = data.get("user_id", USER_ID)

    config = RunnableConfig(
                {"configurable": {"thread_id": conversation_id, "user_id": user_id}}
            )

    if not message or not conversation_id:
        return {"error": "No message or conversation_id provided"}

    async with request.state.pool.connection() as conn:
        checkpointer = AsyncPostgresSaver(conn=conn)
        await checkpointer.setup()

        lucy_agent = Lucy(checkpointer)
        response = await lucy_agent.agent.ainvoke({"messages": [("user", message)]}, config=config)

    response_message = response.get("messages", [])[-1]
    return {"message": response_message.content}


@app.post("/ai/stream")
async def chat_stream(request: Request):
    """
    An endpoint that demonstrates e2e async streaming from Lucy using a Postgres checkpointer.
    """
    data = await request.json()
    conversation_id = data.get("conversation_id")
    user_id = data.get("user_id", USER_ID)
    messages = data.get("messages", [])
    if not messages:
        return {"error": "No messages provided"}

    # Grab the latest message from the conversation
    message_payload = messages[-1]
    # print('Message payload: ', message_payload)
    messages = []
    if type(message_payload) != list:
        messages.append(("user", message_payload.get("content", "")))
    elif type(message_payload) == list:
        raise Exception("Message is a list. Probably a file upload. Not supported yet.")

    async with request.state.pool.connection() as conn:
        checkpointer = AsyncPostgresSaver(conn=conn)
        await checkpointer.setup()

        lucy_agent = Lucy(checkpointer)

        async def stream_chat() -> AsyncGenerator[str, None]:
            config = RunnableConfig(
                {"configurable": {"thread_id": conversation_id, "user_id": user_id}}
            )

            # Example: hypothetical streaming method
            # lucy_agent.agent.get_graph().print_ascii()
            async for token_type, token in lucy_agent.agent.astream(
                input={"messages": messages},
                config=config,
                stream_mode=["messages"],
            ):
                # https://langchain-ai.github.io/langgraph/how-tos/streaming-from-final-node/#filter-on-event-metadata
                if token_type == "messages":
                    message_chunk, config = token
                    node = config.get("langgraph_node")  # type: ignore
                    if (
                        isinstance(message_chunk, AIMessageChunk)
                        and node == Agents.LUCY
                    ):
                        data = {
                            "id": message_chunk.id,
                            "object": "chat.completion.chunk",
                            "created": datetime.now().timestamp(),
                            "model": message_chunk.response_metadata.get("model_name"),
                            "system_fingerprint": message_chunk.response_metadata.get(
                                "system_fingerprint"
                            ),
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {
                                        "role": "assistant",
                                        "content": message_chunk.content,
                                    },
                                    "logprobs": None,
                                    "finish_reason": None,
                                },
                            ],
                        }
                        yield f"event: chat.completion.chunk\ndata: {json.dumps(data)}\n\n"

        return StreamingResponse(stream_chat(), media_type="text/event-stream")


if __name__ == "__main__":
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
