import sys
import os
import re
import asyncio
import logging
import aiohttp
from telethon import TelegramClient, events

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Config
from config import TELEGRAM_BOT_TOKEN, logger_session, API_ID, API_HASH, SESSION_NAME, TARGET_CHANNEL, PWB_ID

# Regex per Amazon
amazon_link_regex = re.compile(r'https?://(?:www\.)?(?:amazon\.[a-z]{2,3}|amzn\.to)/[^\s]+')

# Telethon Client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={'chat_id': PWB_ID, 'text': text}) as resp:
            if resp.status != 200:
                logger_session.warning(f'Telegram API response {resp.status}: {await resp.text()}')


@client.on(events.NewMessage)
async def handler(event):
    if event.chat_id == TARGET_CHANNEL:
        msg = event.message.message
        match = amazon_link_regex.search(msg)
        if match:
            url = match.group()
            logger_session.info(f'Amazon link found: {url}')
            await send_telegram_message('Lista Prodotti')
            logger_session.info("Inviato messaggio: 'Lista Prodotti'")
            await asyncio.sleep(10)
            await send_telegram_message(url)
            logger_session.info(f"Inviato messaggio con URL: {url}")

async def simulate_message():
    # Crea un oggetto "message" simulato
    class MockEvent:
        def __init__(self, message):
            self.message = message
            self.chat_id = TARGET_CHANNEL  # Imposta l'ID del canale di destinazione

    # Simula il messaggio
    test_message = "Check this link: https://www.amazon.com/dp/B08N5M7S6K"
    event = MockEvent(test_message)

    # Richiama il handler manualmente
    await handler(event)


async def main():
    await client.start()
    logger_session.info('Session bot started')
    simulate_message()
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
