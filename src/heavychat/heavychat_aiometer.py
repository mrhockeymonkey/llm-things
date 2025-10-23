import aiometer
import asyncio
import time
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


async def chat(id: int, client: AsyncOpenAI):
    print(f"start chat {id}")
    completion = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": "Talk like a pirate."},
            {
                "role": "user",
                "content": "How do I check if a Python object is an instance of a class?",
            },
        ],
    )
    print(completion.choices[0].message.content)


async def main():
    limits = httpx.Limits(max_connections=5000, max_keepalive_connections=5000)
    http_client = httpx.AsyncClient(limits=limits)
    client = AsyncOpenAI(
        base_url="http://localhost:5185/openai/v1",
        default_headers={"Accept-Encoding": "identity"},
        http_client=http_client
    )

    t0 = time.time()

    async def chat_wrapper(i: int):
        return await chat(i, client)

    # Runs max 5000 at a time, feeds continuously
    await aiometer.run_on_each(
        chat_wrapper,
        [i for i in range(5000)],
        max_at_once=5000
    )

    t1 = time.time()
    print(f"Total time: {t1-t0:.2f}s")


asyncio.run(main())