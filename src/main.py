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
from agents.services.qdrant_manager import MemoryManager
from agents.lucy.graph import Lucy
from config import GlobalConfig

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

loaded = load_dotenv()

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


@app.post("/")
async def langchain(request: Request):
    """
    An endpoint that demonstrates e2e async streaming from Lucy using a Postgres checkpointer.
    """
    data = await request.json()
    conversation_id = data.get("conversation_id")
    user_id = data.get("user_id", "kuba-123")
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
        raise Exception('Message is a list. Probably a file upload. Not supported yet.')
        # print('Message is a list')
        # print('First message: ', message_payload[0])
        # for m in message_payload:
        #     if m.get("type") == "text":
        #         messages.append(("User", m.get("content", "")))
        #     else:
        #         messages.append(("User", m))

    # Simple check for special 'mem' command
    # if message.lower().strip() == "mem":
    #     MemoryManager().plot_memories()
    #     return {
    #         "object": "chat.completion",
    #         "choices": [
    #             {
    #                 "index": 0,
    #                 "message": {"role": "assistant", "content": "Graph generated!"},
    #                 "finish_reason": "stop",
    #             }
    #         ],
    #     }

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
                stream_mode=["messages", "values"],
            ):
                if token_type == "messages":
                    message_chunk, config = token
                    if isinstance(message_chunk, AIMessageChunk):
                        # print('Message chunk: ', message_chunk)
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
                # elif token_type == "values":
                #     print('token', token)
                #     print('========================')

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
