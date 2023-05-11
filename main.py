import loader
import asyncio
import threading
import parser
import src.handlers.forward_handler
import src.handlers.start_handler
import src.handlers.add_community
import src.handlers.my_communities
import src.handlers.information
import src.handlers.bundle_handler

from telethon.sync import TelegramClient


async def main():
    await loader.client.start()
    threading.Thread(target=parser.parse).start()
    await loader.dp.start_polling()

if __name__ == '__main__':
    # me = loader.client.get_me()
    # print(me)
    asyncio.run(main())
