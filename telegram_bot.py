from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from amazon_scraper import AmazonScraper
from database_manager import DatabaseManager
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME

class TelegramBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self.amazon_scraper = AmazonScraper()
        self.db_manager = DatabaseManager(DB_HOST, DB_USER, DB_PASS, DB_NAME)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = """
            Ciao! Il mio compito è quello di avvisarti se un prezzo di un prodotto fornito da Amazon si abbassa o si alza nei giorni a seguire. Ecco cosa puoi fare:
            - Inserisci il link del tuo prodotto preferito subito dopo aver digitato /url. Ad esempio: /url <link>
            - Digita /list per visualizzare i prodotti che stiamo monitorando per te.
            Ti manderò sicuramente una notifica qui per qualsiasi aggiornamento. Cominciamo!
            """
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

    async def open_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        userid = str(user.id)
        username = str(user.username) if user.username else "User senza username"

        if context.args:
            url = context.args[0]
            if "amazon." in url or "amzn." in url:
                params = self.amazon_scraper.fetch_amazon_data(url)
                if params and params[0]:
                    message_response = self.db_manager.insert_into_db(userid, username, params)
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_response)
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Non sono riuscito a trovare il prezzo.")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="URL non supportato per lo scraping del prezzo.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Per favore, inserisci un URL dopo il comando /url")

    async def products_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        userid = str(user.id)
        
        try:
            results = self.db_manager.get_user_products(userid)
            
            if results:
                for record in results:
                    product_asin, product_name, product_price, product_url = record[4], record[1], record[2], record[3]
                    message = f"<b>ASIN</b>: {product_asin} \n<b>NOME</b>: <a href='{product_url}'>{product_name}</a> \n<b>PREZZO</b>: {product_price} €"
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message,
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='Se necessiti che un prodotto non venga più monitorato, eliminalo con /delete ASIN (es. /delete B0BX3GGV1T)'
                )
            else:
                message = "Non hai ancora inserito nessun prodotto da Amazon. Inserisci il prodotto che t'interessa con /url"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        
        except Exception as e:
            message_error = f"Errore durante l'accesso al database: {e}"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)

    async def remove_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        userid = str(user.id)
        asin = context.args[0]

        if asin:
            message_response = self.db_manager.delete_by_asin(context.args[0], userid)
        else:
            message_response = 'L\'ASIN fornito non è valida o mancante'
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_response)

    def run(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('url', self.open_url))
        self.application.add_handler(CommandHandler('list', self.products_list))
        self.application.add_handler(CommandHandler('delete', self.remove_product))
        self.application.run_polling()
