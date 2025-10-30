from typing import Optional

from dev.langgraph_tutorial.agents import research_agent, math_agent, web_search

from langchain_core.messages import convert_to_messages

def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")


def get_invoke_by_agent_type(
        agent_type: str,
        content: str,
        max_results: Optional[int] = 3,
        role: Optional[str] = None
):
    if agent_type == "web_search":
        web_search_results = web_search.invoke(content)
        print(web_search_results["results"][0]["content"])
    elif agent_type == "research":
        research = research_agent.invoke({
                "messages": [{"role": role, "content": content}]
        })
        print(research)
    elif agent_type == "math":
        math_result = math_agent.invoke(
                {"messages": [{"role": role, "content": content}]}
        )
        print(math_result)

def get_streaming_by_agent_type(agent_type: str, role: str, content: str):
    if agent_type == "research":
        for chunk in research_agent.stream({
                "messages": [{"role": role, "content": content}]
        }):
            pretty_print_messages(chunk)

    elif agent_type == "math":
        for chunk in math_agent.stream(
                {"messages": [{"role": role, "content": content}]}
        ):
            pretty_print_messages(chunk)


get_streaming_by_agent_type(
    agent_type="research", role="user", content="who is the mayor of NYC?"
)
get_streaming_by_agent_type(
    agent_type="math", role="user", content="what's (3 + 5) x 7"
)
