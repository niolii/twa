import os.path
import uuid

import loader
import time
import asyncio
import requests
import logging

from playwright.async_api import async_playwright
from telethon import TelegramClient


def send_msg(txt, chat_id, file=None):
    img = True
    if file:
        txt = f'<a href="{file}">&#8205;</a>' + txt
        img = False
    response = requests.post(
        url=f'https://api.telegram.org/bot{loader.token}/sendMessage',
        data={'chat_id': chat_id, 'text': txt, 'parse_mode': 'HTML', 'disable_web_page_preview': img}
    ).json()


async def parse_tg(client):
    channels = loader.db.get_groups('tg')
    print(channels)
    for channel in channels:
        if len(channel[2]) == 0:
            continue

        chnl = await client.get_entity(channel[0])
        time.sleep(0.2)
        msgs = []
        if int(channel[1]) == -1:
            async for msg in client.iter_messages(channel[0], limit=1):
                msgs.append(msg)
        else:
            async for msg in client.iter_messages(channel[0], min_id=int(channel[1]), reverse=True, limit=10):
                msgs.append(msg)
        if len(msgs) == 0:
            continue

        loader.db.update_group_last_post(channel[3], msgs[-1].id)
        for msg in msgs:
            await msg.forward_to(loader.bot_link)


async def parse_tw():
    accs = loader.db.get_groups('tw')
    print(accs)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for acc in accs:
            if len(acc[2]) == 0:
                continue

            await page.goto(acc[0])
            await page.wait_for_selector('article[aria-labelledby]')
            await page.keyboard.press('PageDown')
            await page.keyboard.press('PageDown')
            parsed_articles = await page.query_selector_all('article[aria-labelledby]')
            articles = []
            for article in parsed_articles:
                article_code = await article.inner_html()
                href = await article.query_selector('a[href*=status]')
                href = await href.get_attribute('href')
                link = 'https://twitter.com' + href
                if 'Закрепленный твит' in article_code or 'Pinned Tweet' in article_code or \
                        page.url.replace('https://twitter.com/', '') not in link:
                    continue

                if link.replace(f'{acc[0]}/status/', '') == str(acc[1]):
                    break

                art_div = await article.query_selector('div[dir="auto"]')
                art_span = await art_div.query_selector('span')
                text = await art_span.inner_html()
                img = None
                file = None
                if f'{href}/photo' in article_code:
                    img = await article.query_selector(f'a[href^="{href}/photo"]')
                    img = await img.query_selector('img[alt="Image"][src]')
                    file = await img.get_attribute('src')
                articles.append((text, link, file))
                if str(acc[1]) == "-1":
                    break
            if len(articles) == 0:
                continue

            articles.reverse()
            loader.db.update_group_last_post(acc[3], int(articles[-1][1].replace(f'{acc[0]}/status/', '')))
            for article in articles:
                txt = f'<b>Новая публикация от {page.url.replace("https://twitter.com/", "")}</b>\n' \
                    f'<b>_________________________</b>\n\n' \
                    f'<i>{article[0][0:200]}...</i>\n\n' \
                    f'<b>_________________________</b>\n' \
                    f'<a href="{article[1]}">🔗 Читать полностью</a> ' \
                    f'<b>(Twitter)</b>'
                for user in acc[2]:
                    send_msg(txt, user, article[2])
        await browser.close()


async def parsee(client):
    logging.basicConfig(level=logging.INFO)
    await client.start()
    while True:
        print('parsing tg...')
        try:
            await parse_tg(client)
        except Exception as e:
            print('exception while parsing:', e)
        print('parsed tg.')
        print('parsing tw...')
        try:
            await parse_tw()
        except Exception as e:
            print('exception while parsing:', e)
        print('parsed tw. waiting for 10 min')
        time.sleep(600)


def parse():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient('session1', loader.api_id, loader.api_hash, loop=loop)
    asyncio.run(parsee(client))


if __name__ == '__main__':
    asyncio.run(parse_tw())