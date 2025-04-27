
from app.langgraph.tools import tools
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model

prompt = """
You are a helpful bot. 

Currently you have some tools and will be added more regarding AWS services and Supabase.

Instructions and Guidence:
1. When user wants to write a code, always use the tool, generate_code and then QA it before returning it to the user.
2. When user wants to deploy an AWS Lambda function, you can do it in an order of:
    - Gather all information, what the code does and specification of the function, name, cron if needed, region.
    - Get the codes using generate_code and qa it by using tools like lint_and_test
    - You have the ability to save the code in your own file system and you also have the function to deploy it. 
    - If something goes wrong, just return a message with what went wrong or the error message.

"""

# llm = init_chat_model("gpt-4o-mini", model_provider="openai")
agent_node = create_react_agent(
    model=init_chat_model("gpt-4o-mini", model_provider="openai"),
    prompt=prompt,
    tools=tools
)


