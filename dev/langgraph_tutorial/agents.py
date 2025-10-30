from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from dev.langgraph_tutorial import add, multiply, divide

load_dotenv()

web_search = TavilySearch(max_results=max_results)

research_agent = create_react_agent(
    model="openai:gpt-4o-mini",
    tools=[get_invoke_by_agent_type],
    prompt=(
        "You are a research agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="research_agent",
)

math_agent = create_react_agent(
    model="openai:gpt-4.1",
    tools=[add, multiply, divide],
    prompt=(
        "You are a math agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with math-related tasks\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="math_agent",
)
