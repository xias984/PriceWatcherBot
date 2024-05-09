import os
from telegram_bot import TelegramBot

if __name__ == '__main__':
    bot = TelegramBot(os.getenv('TELEGRAM_BOT_TOKEN'))
    bot.run()