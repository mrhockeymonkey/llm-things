import asyncio
import time
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


async def chat(id: int, client: AsyncOpenAI, sem: asyncio.Semaphore):
    async with sem:
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
        default_headers={"Accept-Encoding": "identity"}, # only needed when logging response via proxy
        http_client=http_client
    )

    t0 = time.time()
    
    # TODO it seems like asuncio event loop can only handle 1000???
    sem = asyncio.Semaphore(5000) 

    coros = [chat(i, client, sem) for i in range(5000)]
    await asyncio.gather(*coros)

    t1 = time.time()
    print(t1-t0)



asyncio.run(main())
