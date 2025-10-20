import asyncio
import time
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
    client = AsyncOpenAI(
        base_url="http://localhost:5185/openai/v1",
        default_headers={"Accept-Encoding": "identity"} # only needed when logging response via proxy
    )

    t0 = time.time()
    sem = asyncio.Semaphore(1000)

    coros = [chat(i, client, sem) for i in range(10_000)]
    await asyncio.gather(*coros)

    t1 = time.time()
    print(t1-t0)



asyncio.run(main())



# async def test_chat(id: int, _: list[int], sem: asyncio.Semaphore):
#     print(f"wait: {id}")
#     async with sem:
#         print(f"start: {id}")
#         await asyncio.sleep(3)
#         print(f"finish: {id}")

# async def test():
#     sem = asyncio.Semaphore(2)

#     t1 = asyncio.create_task(test_chat(1, [], sem))
#     t2 = asyncio.create_task(test_chat(2, [], sem))
#     t3 = asyncio.create_task(test_chat(3, [], sem))

#     await asyncio.gather(t1, t2, t3)