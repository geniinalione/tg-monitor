import os
import json
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION = os.getenv('SESSION_NAME')
NOTIFY_TO = os.getenv('NOTIFY_TO')

with open('config.json', encoding='utf-8') as f:
    cfg = json.load(f)

CHATS = cfg['chats']
KEYWORDS = [k.lower() for k in cfg['keywords']]

client = TelegramClient(SESSION, API_ID, API_HASH)


def find_keyword(text):
    low = text.lower()
    for kw in KEYWORDS:
        if kw in low:
            return kw
    return None


@client.on(events.NewMessage(chats=CHATS))
async def handler(event):
    text = event.raw_text or ''
    kw = find_keyword(text)
    if not kw:
        return

    sender = await event.get_sender()
    chat = await event.get_chat()

    if sender is None:
        author = 'неизвестно'
    else:
        name = ' '.join(filter(None, [getattr(sender, 'first_name', None),
                                       getattr(sender, 'last_name', None)]))
        uname = getattr(sender, 'username', None)
        author = name or (f'@{uname}' if uname else str(sender.id))

    chat_title = getattr(chat, 'title', None) or 'личка'

    notice = (
        f'🔔 Ключ: «{kw}»\n'
        f'💬 Чат: {chat_title}\n'
        f'👤 Автор: {author}\n'
        f'📝 Текст: {text}'
    )

    await client.send_message(NOTIFY_TO, notice)


async def main():
    await client.start()
    me = await client.get_me()
    print(f'Запущен под: {me.first_name}')
    print(f'Мониторю {len(CHATS)} чат(ов), {len(KEYWORDS)} ключей. Жду...')
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
