# from psycopg_pool import ConnectionPool
# from config import GlobalConfig

# from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent
# from langgraph.checkpoint.postgres import PostgresSaver
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
# from psycopg_pool import ConnectionPool

# # https://github.com/langchain-ai/langgraph/discussions/894#discussioncomment-10369994
# def get_db_checkpointer():
#     connection_pool = ConnectionPool(
#         conninfo=GlobalConfig.get_db_url(),
#         max_size=20,
#         open=True,
#     )
#     checkpointer = PostgresSaver(conn=connection_pool)
#     checkpointer.setup()
#     return checkpointer


