from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from amazon_scraper import AmazonScraper
from database_manager import DatabaseManager
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, logger

class TelegramBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self.amazon_scraper = AmazonScraper()
        self.db_manager = DatabaseManager(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        self.logger = logger

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        uid_dest = update.message.chat.id
        if args:
            pid = args[0].split("_")[0]
            uid = args[0].split("_")[1]

            username = self.db_manager.get_username_from_idtelegram(uid)[0][0]
            if username:
                text_user = f"Questo articolo è stato condiviso per te da <i>{username}</i>."
            else:
                text_user = f"Un prodotto Amazon è stato condiviso per te."

            if not self.db_manager.check_productuser_from_id(pid, uid_dest):
                keyboard = [
                            [InlineKeyboardButton("Aggiungi", callback_data=f"add_{pid}")]
                        ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                text_start = f"Premi su <b>AGGIUNGI</b> per aggiungerlo alla tua lista dei prodotti da monitorare. Ti avviserò ogni volta che il prezzo salirà o scenderà."
            else:
                reply_markup = ''
                text_start = 'Articolo già presente nella tua lista.'

            product_message = self.info_product(pid)
            await update.message.reply_text(
                text=product_message,
                parse_mode='HTML',
                disable_web_page_preview=False,
                reply_markup=reply_markup
            )
            
            await update.message.reply_text(
                text=f"{text_user} {text_start}",
                parse_mode='HTML'
            )
        else:
            welcome_message = f"Ciao! Il mio compito è quello di avvisarti se un prezzo di un prodotto fornito da Amazon si abbassa o si alza nei giorni a seguire."
            await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

    async def open_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        userid = str(user.id)
        username = self.user_identity(user)
        if context.args:
            url = context.args[0]
            if "amazon." in url or "amzn." in url:
                params = self.amazon_scraper.fetch_amazon_data(url)
                if params and params[0]:
                    message_response = self.db_manager.insert_into_db(userid, username, params)
                    self.logger.info(f"Associazione utente {userid} con prodotto (ASIN) {params[2]} creata")
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_response)
                else:
                    self.logger.info(f"Informazioni prodotto non trovate: {url}")
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Non sono riuscito a trovare il prezzo.")
            else:
                self.logger.info(f"Url non valido: {url}")
                await context.bot.send_message(chat_id=update.effective_chat.id, text="URL non supportato per lo scraping del prezzo.")
        else:
            self.logger.info(f"Url non valido: {url}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Per favore, inserisci un URL dopo il comando /url")

    async def products_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        userid = str(user.id)
        
        try:
            results = self.db_manager.get_user_products(userid)
            
            if results:
                for record in results:
                    pid, product_name, product_price, product_url = record[0], record[1], record[2], record[3]
                    message = f"<a href='{product_url}'>{product_name}</a> - {product_price} €"
                    
                    keyboard = [
                        [InlineKeyboardButton("Cancella", callback_data=f"delete_{pid}"),
                         InlineKeyboardButton("Info", callback_data=f"info_{pid}"),
                         InlineKeyboardButton("Condividi", callback_data=f"share_{pid}")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message,
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup=reply_markup
                    )
            else:
                message = "Non hai ancora inserito nessun prodotto da Amazon. Inserisci il prodotto che t'interessa con /url"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        
        except Exception as e:
            message_error = f"Errore durante l'accesso al database: {e}"
            self.logger.error(message_error)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)

    async def button_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from urllib import parse
        query = update.callback_query
        await query.answer()
        
        data = query.data
        pid = data.split("_")[1]
        if data.startswith("delete_"):
            response = self.db_manager.delete_by_productid(pid, query.message.chat.id)
            await query.edit_message_text(text=response)
        elif data.startswith("info_"):
            message = self.info_product(pid)
            await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
        elif data.startswith("share_"):
            params = f"{pid}_{update.effective_chat.id}"
            encoded_params = parse.quote_plus(params)
            url = f"https://t.me/bestpriceamzbot?start={encoded_params}"
            self.logger.info(f"Generated URL for sharing: {url}")
            share_message = f"Condividi questo prodotto con gli altri! Clicca qui: {url}"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=share_message,
                parse_mode='HTML'
            )
        elif data.startswith("add_"):
            uid_dest = query.message.chat.id
            username_dest = self.user_identity(query.message.chat)
            product_id = data.split("_")[1]
            params = {
                "telegram_id": uid_dest,
                "product_id": int(product_id),
                "username_dest": username_dest
            }

            added_message = self.db_manager.insert_new_productuser(params)
            await context.bot.send_message(
                chat_id=uid_dest,
                text=added_message
            )
            self.logger.info(f"Utente con id telegram {params['telegram_id']} ha aggiunto prodotto con id {params['product_id']}")

    def info_product(self, pid):
        result = self.db_manager.get_info_data(pid)
        if result:
            return f"<b>NOME</b>: <a href='{result[0][3]}'>{result[0][1]}</a> \n<b>PREZZO</b>: {result[0][2]} €\n<b>ASIN</b>: {result[0][4]} \n<b>CATEGORIA</b>: {result[0][5]}"
        else:
            return f"Prodotto non esistente"
        
    def user_identity(self, user):
        if user.username:
            return str(user.username)
        elif user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        elif user.first_name:
            return str(user.first_name)
        elif user.last_name:
            return str(user.last_name)
        else:
            return "User senza nome"

    def run(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('url', self.open_url))
        self.application.add_handler(CommandHandler('list', self.products_list))
        self.application.add_handler(CallbackQueryHandler(self.button_callback_handler))
        self.application.run_polling(
            poll_interval=10,
            timeout=300
        )
