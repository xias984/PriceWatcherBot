import mysql.connector
from mysql.connector import Error
from datetime import datetime
from amazonify import amazonify
import os

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.c = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.c = self.conn.cursor(buffered=True)
        except Error as e:
            print(f"Errore durante la connessione a MySQL: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def insert_into_db(self, userid, username, amz_data):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_response = ""

        try:
            # Cerca il prodotto per ASIN o nome prodotto
            self.c.execute("SELECT id FROM products WHERE asin = %s OR product_name = %s", (amz_data[3], amz_data[1]))
            result_product = self.c.fetchone()

            if result_product:
                product_id = result_product[0]
            else:
                self.c.execute(
                    "INSERT INTO products (product_name, created_at, price, url, asin, category) VALUES (%s, %s, %s, %s, %s, %s)",
                    (amz_data[1], now, amz_data[0], amazonify(amz_data[4], os.getenv('AMAZON_AFFILIATE_TAG')), amz_data[2], amz_data[3])
                )
                product_id = self.c.lastrowid

            self.conn.commit()

            # Cerca l'utente per idtelegram
            self.c.execute("SELECT id FROM users WHERE idtelegram = %s", (userid,))
            result_user = self.c.fetchone()

            if result_user:
                user_id = result_user[0]
            else:
                self.c.execute(
                    "INSERT INTO users (nome, idtelegram, created_at) VALUES (%s, %s, %s)",
                    (username, userid, now)
                )
                user_id = self.c.lastrowid

            self.conn.commit()

            # Verifica se l'associazione utente-prodotto esiste già
            self.c.execute(
                "SELECT product_id FROM product_user WHERE product_id = %s AND user_id = %s",
                (product_id, user_id)
            )
            n_prod = self.c.fetchall()

            if len(n_prod) == 0:
                try:
                    self.c.execute(
                        "INSERT INTO product_user (user_id, product_id, created_at) VALUES (%s, %s, %s)",
                        (user_id, product_id, now)
                    )
                    self.conn.commit()
                    message_response = "Prodotto aggiunto correttamente, ora ti terremo aggiornato qualora il prezzo variasse."
                except Error as e:
                    message_response = f"Errore: {e}"
            else:
                message_response = 'Prodotto già presente nella tua lista dei prodotti che stai monitorando.'

        except Error as e:
            message_response = f"Errore durante l'accesso al database: {e}"

        return message_response

    def get_user_products(self, userid):
        try:
            self.c.execute("""
                SELECT P.* FROM products AS P 
                LEFT JOIN product_user AS PU ON P.id = PU.product_id 
                LEFT JOIN users AS U ON PU.user_id = U.id 
                WHERE U.idtelegram = %s
            """, (userid,))
            return self.c.fetchall()
        except Error as e:
            print(f"Errore durante l'accesso al database: {e}")
            return []

    def delete_by_asin(self, asin, user):
        try:
            self.c.execute("""
                SELECT PU.id FROM products AS P
                LEFT JOIN product_user AS PU ON P.id = PU.product_id
                LEFT JOIN users AS U ON PU.user_id = U.id
                WHERE P.asin = %s AND U.idtelegram = %s
            """, (asin, user))
            result_id = self.c.fetchone()

            if result_id and result_id[0]:
                self.c.execute("DELETE FROM product_user WHERE id = %s", (result_id[0],))
                self.conn.commit()

                return "Prodotto eliminato correttamente, continua ad aggiungere prodotti da monitorare con /url. Digita /help per maggiori informazioni."
            else:
                return "Non è stato trovato un ASIN corrispondente"
        except Error as e:
            print(f"Errore durante l'accesso al database: {e}")
            return []

    def get_price_for_scraping(self):
        try:
            self.c.execute("SELECT id, price, url FROM products")
            return self.c.fetchall()
        except Error as e:
            print(f"Errore durante l'accesso al database: {e}")
            return []

    def get_recent_price_changes(self):
        now = datetime.now().strftime('%Y-%m-%d')
        try:
            self.c.execute("""
                SELECT P.product_name, P.url, U.idtelegram, VP.newprice, VP.oldprice 
                FROM variation_price AS VP 
                LEFT JOIN products AS P ON VP.idprodotto = P.id 
                LEFT JOIN product_user AS PU ON P.id = PU.product_id 
                LEFT JOIN users AS U ON PU.user_id = U.id
                WHERE VP.updated_at = %s
            """, (now,))
            return self.c.fetchall()
        except Error as e:
            print(f"Errore durante l'accesso al database: {e}")
            return []

    def update_variation_price(self, idprod, oldprice, newprice):
        now = datetime.now().strftime('%Y-%m-%d')
        try:
            self.c.execute("""
                INSERT INTO variation_price (idprodotto, oldprice, newprice, updated_at) 
                VALUES (%s, %s, %s, %s)
            """, (idprod, oldprice, newprice, now))
            self.c.execute("""
                UPDATE products SET price = %s WHERE id = %s
            """, (newprice, idprod))
            self.conn.commit()
        except Error as e:
            print(f"Errore durante l'accesso al database: {e}")
