import asyncio
from claude_agent_sdk import query, ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ResultMessage, AgentDefinition
from pathlib import Path

lead_agent = Path('poem-director.txt').read_text()
creative_agent = Path('creative-agent.txt').read_text()


async def main():

    # Define specialized subagents
    agents = {
        "creative-agent": AgentDefinition(
            description=(
                "Use this agent when you need to create a single verse of a poem "
                "The creative agent will create four lines of beautiful prose in french "
            ),
            tools=["WebSearch", "Write"],
            prompt=creative_agent,
            model="haiku"
        ),
    }

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        setting_sources=["project"],  # Load skills from project .claude directory
        system_prompt=lead_agent,
        allowed_tools=["Task"],
        agents=agents,
        #hooks=hooks,
        model="haiku"
    )

    async for message in query(
        prompt="write me a poem about the moon",
        options=options
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)              # Claude's reasoning
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name} block type {type(block).__name__}")
                    print(f"{block.input.get('subagent_type', 'unknown')}")   # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")     

    # try:
    #     async with ClaudeSDKClient(options=options) as client:
    #         while True:
    #             # Get input
    #             try:
    #                 user_input = input("\nYou: ").strip()
    #             except (EOFError, KeyboardInterrupt):
    #                 break

    #             if not user_input or user_input.lower() in ["exit", "quit", "q"]:
    #                 break

    #             # Write user input to transcript (file only, not console)
    #             # transcript.write_to_file(f"\nYou: {user_input}\n")

    #             # Send to agent
    #             await client.query(prompt=user_input)

    #             # transcript.write("\nAgent: ", end="")

    #             # Stream and process response
    #             async for msg in client.receive_response():
    #                 if type(msg).__name__ == 'AssistantMessage':
    #                     process_assistant_message(msg, tracker, transcript)

    #             # transcript.write("\n")
    # finally:
    #     # transcript.write("\n\nGoodbye!\n")
    #     # transcript.close()
    #     # tracker.close()
    #     # print(f"\nSession logs saved to: {session_dir}")
    #     # print(f"  - Transcript: {transcript_file}")
    #     # print(f"  - Tool calls: {session_dir / 'tool_calls.jsonl'}")
    #     print("fin")


if __name__ == "__main__":
    asyncio.run(main())
