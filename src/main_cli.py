from dotenv import load_dotenv
loaded = load_dotenv()
from langchain_agent import get_agent, show_memory


def pretty_print_stream_chunk(chunk):
    for node, updates in chunk.items():
        print(f"Update from node: {node}")
        if "messages" in updates:
            updates["messages"][-1].pretty_print()
        else:
            print(updates)

        print("\n")

def main():

    config = {"configurable": {"thread_id": "abc123"}}
    agent = get_agent()


    while True:
        user_input = input("You: ")

        if user_input == "mem":
            show_memory()
            continue

        output = agent.invoke({"messages": [("user", user_input)]}, config=config)
        message = output['messages'][-1]
        print(f'Lucy: {message.content}')


if __name__ == "__main__":
    main()