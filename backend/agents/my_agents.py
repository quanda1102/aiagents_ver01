from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from dotenv import load_dotenv
load_dotenv(override=True)

router_instruction = """
You are a router agent that can route the user's request to the appropriate agent.
"""

router_agent = Agent(
    name="Router",
    instructions=router_instruction,
    model="gpt-4o-mini",
    handoffs=[]
)


google_drive_agent = Agent(
    name="Google Drive",
    instructions="You are a Google Drive agent that can help with Google Drive tasks.",
    model="gpt-4o-mini",
    handoffs=[router_agent]
)


chatting_agent = Agent(
    name="Chatting",
    instructions="You are a chatting agent that can chat with the user.",
    model="gpt-4o-mini",
    handoffs=[router_agent]
)
router_agent.handoffs.append(google_drive_agent)
async def run_agents(input = "I want to create a new document in Google Drive"):
    runner = Runner.run_streamed(
        starting_agent=router_agent,
        input=input
    )
    async for event in runner.stream_events():
        if event.type == "raw_response_event":
            data = event.data
            if hasattr(data, "delta"):
                print(data.delta, end="", flush=True)




if __name__ == "__main__":
    asyncio.run(run_agents("I want to create a new document in Google Drive"))
