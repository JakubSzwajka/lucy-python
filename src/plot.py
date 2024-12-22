from dotenv import load_dotenv

load_dotenv()

from agents.teams.supervisor.graph import get_agent

agent = get_agent()


print("```mermaid")
print(agent.get_graph().draw_mermaid())
print("```")
