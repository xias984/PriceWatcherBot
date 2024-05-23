import mysql.connector
from mysql.connector import Error
from datetime import datetime
from amazonify import amazonify
from config import AMAZON_AFFILIATE_TAG, logger

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connect()
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.today = datetime.now().strftime('%Y-%m-%d')

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
            logger.error(f"Errore durante la connessione a MySQL: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.commit()
            self.c.close()
            self.conn.close()

    def insert_into_db(self, userid, username, amz_data):
        message_response = ""

        try:
            product_id = self.get_or_insert_product(amz_data)
            user_id = self.get_or_insert_user(userid, username)
            message_response = self.add_product_to_user(user_id, product_id)
            self.conn.commit()
        except Error as e:
            self.conn.rollback()
            message_response = f"Errore durante l'accesso al database: {e}"
            logger.error(message_response)

        return message_response

    def get_or_insert_product(self, amz_data):
        self.c.execute("SELECT id FROM products WHERE asin = %s OR product_name = %s", (amz_data[3], amz_data[1]))
        result_product = self.c.fetchone()

        if result_product:
            return result_product[0]
        else:
            self.c.execute(
                "INSERT INTO products (product_name, created_at, price, url, asin, category) VALUES (%s, %s, %s, %s, %s, %s)",
                (amz_data[1], self.now, amz_data[0], amazonify(amz_data[4], AMAZON_AFFILIATE_TAG), amz_data[2], amz_data[3])
            )
            return self.c.lastrowid

    def get_or_insert_user(self, userid, username):
        self.c.execute("SELECT id FROM users WHERE idtelegram = %s", (userid,))
        result_user = self.c.fetchone()

        if result_user:
            return result_user[0]
        else:
            self.c.execute(
                "INSERT INTO users (nome, idtelegram, created_at) VALUES (%s, %s, %s)",
                (username, userid, self.now)
            )
            return self.c.lastrowid

    def add_product_to_user(self, user_id, product_id):
        self.c.execute(
            "SELECT product_id FROM product_user WHERE product_id = %s AND user_id = %s",
            (product_id, user_id)
        )
        n_prod = self.c.fetchall()

        if not n_prod:
            self.c.execute(
                "INSERT INTO product_user (user_id, product_id, created_at) VALUES (%s, %s, %s)",
                (user_id, product_id, self.now)
            )
            return "Prodotto aggiunto correttamente, ora ti terremo aggiornato qualora il prezzo variasse."
        else:
            return 'Prodotto già presente nella tua lista dei prodotti che stai monitorando.'

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
            logger.error(f"Errore durante l'accesso al database: {e}")
            return []

    def get_username_from_idtelegram(self, uid):
        try:
            self.c.execute("SELECT nome FROM users WHERE idtelegram = %s", (uid,))
            return self.c.fetchall()
        except Error as e:
            logger.error(f"Errore durante l'accesso al database: {e}")
            return []

    def delete_by_productid(self, pid, user):
        try:
            result_id = self.check_productuser_from_id(pid, user)
            if result_id:
                self.c.execute("DELETE FROM product_user WHERE id = %s", (result_id[0],))
                self.conn.commit()
                return "Prodotto eliminato correttamente."
            else:
                return "Il prodotto non esiste più."
        except Error as e:
            self.conn.rollback()
            logger.error(f"Errore durante l'accesso al database: {e}")
            return []

    def get_info_data(self, pid):
        try:
            self.c.execute("SELECT * FROM products WHERE id = %s", (pid,))
            return self.c.fetchall()
        except Error as e:
            logger.error(f"Errore durante l'accesso al database: {e}")
            return []

    def check_productuser_from_id(self, pid, uid):
        try:
            self.c.execute("""
                SELECT PU.id FROM products AS P
                LEFT JOIN product_user AS PU ON P.id = PU.product_id
                LEFT JOIN users AS U ON PU.user_id = U.id
                WHERE P.id = %s AND U.idtelegram = %s
            """, (pid, uid))
            return self.c.fetchone()
        except Error as e:
            logger.error(f"Errore durante l'accesso al database: {e}")
            return []

    def get_price_for_scraping(self):
        try:
            self.c.execute("SELECT id, price, url FROM products")
            return self.c.fetchall()
        except Error as e:
            logger.error(f"Errore durante l'accesso al database: {e}")
            return []

    def get_recent_price_changes(self):
        try:
            self.c.execute("""
                SELECT P.product_name, P.url, U.idtelegram, VP.newprice, VP.oldprice, P.id
                FROM variation_price AS VP 
                LEFT JOIN products AS P ON VP.idprodotto = P.id 
                LEFT JOIN product_user AS PU ON P.id = PU.product_id 
                LEFT JOIN users AS U ON PU.user_id = U.id
                WHERE VP.updated_at LIKE %s
            """, (self.today + "%",))
            return self.c.fetchall()
        except Error as e:
            logger.error(f"Errore durante l'accesso al database: {e}")
            return []

    def update_variation_price(self, idprod, oldprice, newprice):
        try:
            self.c.execute("""
                INSERT INTO variation_price (idprodotto, oldprice, newprice, updated_at) 
                VALUES (%s, %s, %s, %s)
            """, (idprod, oldprice, newprice, self.now))
            self.c.execute("""
                UPDATE products SET price = %s WHERE id = %s
            """, (newprice, idprod))
            self.conn.commit()
        except Error as e:
            self.conn.rollback()
            logger.error(f"Errore durante l'accesso al database: {e}")

    def insert_new_productuser(self, params):
        try:
            user_id = self.get_or_insert_user(params['telegram_id'], params['username_dest'], self.now)
            message_response = self.add_product_to_user(user_id, params['product_id'], self.now)
            self.conn.commit()
        except Error as e:
            self.conn.rollback()
            message_response = f"Errore durante l'accesso al database: {e}"
            logger.error(message_response)

        return message_response
