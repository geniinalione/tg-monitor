import os
import json
from datetime import timezone, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION = os.getenv('SESSION_NAME')

with open('config.json', encoding='utf-8') as f:
    cfg = json.load(f)

CHATS = cfg['chats']
KEYWORDS = [k.lower() for k in cfg['keywords']]
NOTIFY_TO = cfg['notify_to']

MSK = timezone(timedelta(hours=3))  # Москва

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
    if not find_keyword(text):
        return

    sender = await event.get_sender()
    chat = await event.get_chat()

    # автор: сначала @тег, если нет — имя, если и его нет — id
    if sender is None:
        author = 'неизвестно'
    else:
        uname = getattr(sender, 'username', None)
        if uname:
            author = f'@{uname}'
        else:
            name = ' '.join(filter(None, [getattr(sender, 'first_name', None),
                                           getattr(sender, 'last_name', None)]))
            author = name or str(sender.id)

    group = getattr(chat, 'title', None) or 'личка'

    # время и дата по Москве
    dt = event.message.date.astimezone(MSK).strftime('%d.%m.%Y %H:%M')

    notice = (
        f'{text}\n\n'
        f'Автор: {author}\n'
        f'Группа: {group}\n'
        f'Время: {dt}'
    )

    for user in NOTIFY_TO:
        try:
            await client.send_message(user, notice)
        except Exception as e:
            print(f'Не смог отправить {user}: {e}')


async def main():
    await client.start()
    me = await client.get_me()
    print(f'Запущен под: {me.first_name}')
    print(f'Мониторю {len(CHATS)} чат(ов), {len(KEYWORDS)} ключей, шлю {len(NOTIFY_TO)} получателям. Жду...')
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
