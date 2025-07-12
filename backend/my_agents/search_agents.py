from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model="gpt-4o-mini-search-preview"  # specify your desired model here
)

result = Runner.run_sync(agent, "Search for the latest news about AI.")
print(result.final_output)
