from dotenv import load_dotenv
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import StreamingResponse
from psycopg_pool import AsyncConnectionPool

from agents.modules.memory_manager import MemoryManager
from agents.lucy.graph import Lucy
from config import GlobalConfig

loaded = load_dotenv()

import logging
from fastapi import FastAPI, Request
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.postgres import PostgresSaver

logger = logging.getLogger()
logger.handlers.clear()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)



@asynccontextmanager
async def lifespan(app: FastAPI):
    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
        # "row_factory": dict_row,
    }
    async with AsyncConnectionPool(GlobalConfig.get_db_url(), kwargs=connection_kwargs) as pool:
        await pool.wait()  # optional
        yield {"pool": pool}


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/")
async def langchain(request: Request):
    data = await request.json()
    conversation_id = data.get("conversation_id")
    user_id = data.get("user_id", 'kuba-123')
    messages = data.get("messages")
    message = messages[
        -1
    ].get(
        "content"
    )  # taking the last message since the conversation history should be stored on server side

    if message == "mem":
        MemoryManager().plot_memories()
        return {
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Graph generated!"},
                    "finish_reason": "stop",
                }
            ],
        }


    async with request.state.pool.connection() as conn:
        checkpointer = AsyncPostgresSaver(conn=conn)
        await checkpointer.setup()
        app = Lucy(checkpointer)

        response = app.talk(message, RunnableConfig({
            "configurable": {
                "thread_id": conversation_id,
                "user_id": user_id,
            }
        }))
        # return StreamingResponse(response, media_type="text/event-stream")

    return {
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "xyz"},
                "finish_reason": "stop",
            }
        ],
    }


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
