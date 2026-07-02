import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()
client = TelegramClient(os.getenv('SESSION_NAME'), int(os.getenv('API_ID')), os.getenv('API_HASH'))

async def main():
    async for d in client.iter_dialogs():
        print(f'{d.id:>15} | {d.name}')

with client:
    client.loop.run_until_complete(main())
