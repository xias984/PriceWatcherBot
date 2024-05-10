import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/supervisor/bot.log'),
        logging.FileHandler('/var/log/supervisor/bot_err.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('PWB')

TELEGRAM_BOT_TOKEN=os.getenv('TELEGRAM_BOT_TOKEN')
AMAZON_AFFILIATE_TAG=os.getenv('AMAZON_AFFILIATE_TAG')
DB_HOST=os.getenv('DB_HOST')
DB_USER=os.getenv('DB_USER')
DB_PASS=os.getenv('DB_PASS')
DB_NAME=os.getenv('DB_NAME')