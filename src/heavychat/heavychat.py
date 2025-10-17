import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


async def chat(id: int, client: AsyncOpenAI, sem: asyncio.Semaphore):
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
    client = AsyncOpenAI()
    sem = asyncio.Semaphore(2)
    t1 = asyncio.create_task(chat(1, client, sem))
    t2 = asyncio.create_task(chat(2, client, sem))
    t3 = asyncio.create_task(chat(3, client, sem))

    await asyncio.gather(t1, t2, t3)

async def test_chat(id: int, _: list[int], sem: asyncio.Semaphore):
    print(f"wait: {id}")
    async with sem:
        print(f"start: {id}")
        await asyncio.sleep(3)
        print(f"finish: {id}")

async def test():
    sem = asyncio.Semaphore(2)

    t1 = asyncio.create_task(test_chat(1, [], sem))
    t2 = asyncio.create_task(test_chat(2, [], sem))
    t3 = asyncio.create_task(test_chat(3, [], sem))

    await asyncio.gather(t1, t2, t3)

asyncio.run(main())

