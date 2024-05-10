from config import TELEGRAM_BOT_TOKEN
from telegram_bot import TelegramBot

if __name__ == '__main__':
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()