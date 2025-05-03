from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, MessageEntity
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from amazon_scraper import AmazonScraper
from database_manager import DatabaseManager
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, logger
from urllib import parse

class TelegramBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self.amazon_scraper = AmazonScraper()
        self.db_manager = DatabaseManager(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        self.logger = logger
        self.user_states = {}
        self.keyboard = [[KeyboardButton("Aggiungi URL"), KeyboardButton("Lista Prodotti")]]
        self.reply_markup_kb = ReplyKeyboardMarkup(self.keyboard, resize_keyboard=True)
        self.welcomed_users = set()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        uid_dest = update.message.chat.id

        if args:
            await self.handle_shared_product(update, context, args, uid_dest)
        else:
            await self.send_welcome_message(update, context)

    async def handle_shared_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE, args, uid_dest):
        pid, uid = args[0].split("_")
        username = self.db_manager.get_username_from_idtelegram(uid)[0][0] or "un utente"
        text_user = f"Questo articolo è stato condiviso per te da <i>{username}</i>."

        if not self.db_manager.check_productuser_from_id(pid, uid_dest):
            keyboard = [[InlineKeyboardButton("Aggiungi", callback_data=f"add_{pid}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text_start = "Premi su <b>AGGIUNGI</b> per aggiungerlo alla tua lista dei prodotti da monitorare. Ti avviserò ogni volta che il prezzo salirà o scenderà."
        else:
            reply_markup = None
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
            parse_mode='HTML',
            reply_markup=self.reply_markup_kb
        )

    async def send_welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info(f"Utente {update.message.chat.id} ha avviato il bot.")
        welcome_message = "Ciao! Il mio compito è quello di avvisarti se un prezzo di un prodotto fornito da Amazon si abbassa o si alza nei giorni a seguire."
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_message,
            reply_markup=self.reply_markup_kb
        )

    async def open_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.chat
        userid = str(user.id)
        username = self.user_identity(user)

        for entity in update.message.entities:
            if entity.type == MessageEntity.URL:
                url = update.message.text
                await self.process_url(update, context, url, userid, username)

    async def process_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url, userid, username):
        if "amazon." in url or "amzn." in url:
            params = self.amazon_scraper.fetch_amazon_data(url)
            self.logger.info(params)

            if not params:
                self.logger.info(f"Parsing fallito: {url}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Errore nell'analisi del prodotto. Riprova più tardi.",
                    reply_markup=self.reply_markup_kb
                )
                return

            price = params[0]

            if price == "Prezzo non trovato":
                self.logger.info(f"Prezzo non trovato per URL: {url}")
                keyboard = [
                    [InlineKeyboardButton("Segnala", callback_data=f"report_{userid}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="⚠️ Non sono riuscito a trovare il prezzo per questo prodotto.",
                    reply_markup=reply_markup
                )
                return

            # Prodotto valido, si prova inserimento nel DB
            message_response = self.db_manager.insert_into_db(userid, username, params)

            # Se c'è stato un errore, interrompi prima di mostrare bottoni o log di successo
            if "errore" in message_response.lower():
                self.logger.warning(f"Inserimento fallito per l'utente {userid} - {message_response}")
                keyboard = [
                    [InlineKeyboardButton("Segnala", callback_data=f"report_{userid}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message_response,
                    reply_markup=self.reply_markup
                )
                return

            # Inserimento riuscito
            keyboard = [
                [InlineKeyboardButton("Condividi", callback_data=f"share_{userid}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.logger.info(f"Associazione utente {userid} con prodotto (ASIN) {params[2]} creata")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_response,
                reply_markup=reply_markup
            )

        else:
            self.logger.info(f"URL non valido: {url}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="URL non supportato per lo scraping del prezzo.",
                reply_markup=self.reply_markup_kb
            )


    async def products_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        userid = str(user.id)
        
        try:
            results = self.db_manager.get_user_products(userid)
            if results:
                await self.display_products_list(update, context, results)
            else:
                message = "Non hai ancora inserito nessun prodotto da Amazon. Inserisci il prodotto che t'interessa con /url"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        except Exception as e:
            message_error = f"Errore durante l'accesso al database: {e}"
            self.logger.error(message_error)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)

    async def display_products_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE, results):
        for record in results:
            pid, product_name, product_price, product_url = record[0], record[1], record[2], record[3]
            discount_message = self.get_discount_message(pid)

            message = f"<a href='{product_url}'>{product_name}</a> - {product_price} € {discount_message}\n"

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

    def get_discount_message(self, pid):
        from bot_utils.message_formatter import format_discount
        
        diff_price = self.db_manager.get_diff_price_by_productid(pid)
        if diff_price and diff_price[0][0] is not None and diff_price[0][1] is not None:
            current = float(diff_price[0][0])
            previous = float(diff_price[0][1])
            return format_discount(current, previous)
        return ""

    async def button_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        action, pid = data.split("_", 1)
        
        if action == "delete":
            await self.delete_product(query, pid)
        elif action == "info":
            await self.send_product_info(update, context, pid)
        elif action == "share":
            await self.share_product(update, context, pid)
        elif action == "add":
            await self.add_product(query, pid)

    async def delete_product(self, query, pid):
        response = self.db_manager.delete_by_productid(pid, query.message.chat.id)
        await query.edit_message_text(text=response)

    async def send_product_info(self, update, context, pid):
        message = self.info_product(pid)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False,
            reply_markup=self.reply_markup_kb
        )

    async def share_product(self, update, context, pid):
        params = f"{pid}_{update.effective_chat.id}"
        encoded_params = parse.quote_plus(params)
        url = f"https://t.me/bestpriceamzbot?start={encoded_params}"
        self.logger.info(f"Generated URL for sharing: {url}")
        share_message = f"Condividi questo prodotto con gli altri! Clicca qui: {url}"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=share_message,
            parse_mode='HTML',
            reply_markup=self.reply_markup_kb
        )

    async def add_product(self, query, pid):
        uid_dest = query.message.chat.id
        username_dest = self.user_identity(query.message.chat)
        product_id = int(pid)
        params = {
            "telegram_id": uid_dest,
            "product_id": product_id,
            "username_dest": username_dest
        }
        added_message = self.db_manager.insert_new_productuser(params)
        await query.message.reply_text(text=added_message)
        self.logger.info(f"Utente con id telegram {params['telegram_id']} ha aggiunto prodotto con id {params['product_id']}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        text = update.message.text
        
        if user_id not in self.welcomed_users:
            self.welcomed_users.add(user_id)
            await self.start(update, context)
            return
        if text == 'Aggiungi URL':
            await self.request_url(update, context, user_id)
        elif self.user_states.get(user_id) == 'awaiting_url':
            await self.open_url(update, context)
            self.user_states[user_id] = None
        elif text == 'Lista Prodotti':
            await self.products_list(update, context)

    async def request_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text="Inserisci l'URL di Amazon"
        )
        self.user_states[user_id] = 'awaiting_url'

    def info_product(self, pid):
        from datetime import datetime

        result = self.db_manager.get_info_data(pid)
        diff_price = self.db_manager.get_diff_price_by_productid(pid)

        if result:
            message = f"<b>NOME</b>: <a href='{result[0][3]}'>{result[0][1]}</a> \n<b>ASIN</b>: {result[0][4]} \n<b>CATEGORIA</b>: {result[0][5]}"
            
            if diff_price and len(diff_price) > 0 and diff_price[0][0] is not None:
                updated_at_raw = diff_price[0][2]
                try:
                    updated_at_dt = datetime.strptime(str(updated_at_raw), "%Y-%m-%d %H:%M:%S")
                    updated_at_str = updated_at_dt.strftime("%d-%m-%Y")
                except Exception as e:
                    updated_at_str = str(updated_at_raw)

                prezzo_attuale = float(diff_price[0][0])
                prezzo_precedente = float(diff_price[0][1])

                message += f"\n<b>PREZZO ATTUALE</b>: {prezzo_attuale} € <i>(aggiornato il {updated_at_str})</i>\n<b>PREZZO PRECEDENTE</b>: {prezzo_precedente} €"

                discount_message = self.get_discount_message(pid)
                if discount_message:
                    message += discount_message
            else:
                message += f"\n<b>PREZZO</b>: {result[0][2]} €\n"
        else:
            message = "Prodotto non esistente"

        return message
        
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
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.button_callback_handler))
        self.application.run_polling(
            poll_interval=10,
            timeout=300
        )