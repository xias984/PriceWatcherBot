import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def insert_into_db(self, userid, username, amz_data):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_response = ""

        try:
            self.c.execute("SELECT id FROM products WHERE asin = ? OR product_name = ?", (amz_data[3],amz_data[1]))
            result_product = self.c.fetchone()

            if result_product:
                product_id = result_product[0]
            else:
                self.c.execute(
                    "INSERT INTO products (product_name, created_at, price, url, asin, category) VALUES (?, ?, ?, ?, ?, ?)",
                    (amz_data[1], now, amz_data[0], amz_data[4], amz_data[2], amz_data[3])
                )
                product_id = self.c.lastrowid

            self.conn.commit()

            self.c.execute("SELECT id FROM users WHERE idtelegram = ?", (userid,))
            result_user = self.c.fetchone()

            if result_user:
                user_id = result_user[0]
            else:
                self.c.execute(
                    "INSERT INTO users (nome, idtelegram, created_at) VALUES (?, ?, ?)",
                    (username, userid, now)
                )
                user_id = self.c.lastrowid

            self.conn.commit()

            self.c.execute(
                    "SELECT product_id FROM product_user WHERE product_id = ? AND user_id = ?",
                    (product_id, user_id)
                )
            n_prod = self.c.fetchall()
            
            if len(n_prod) == 0:
                try:
                    self.c.execute(
                        "INSERT INTO product_user (user_id, product_id, created_at) VALUES (?, ?, ?)",
                        (user_id, product_id, now)
                    )
                    self.conn.commit()
                    message_response = "Prodotto aggiunto correttamente, ora ti terremo aggiornato qualora il prezzo variasse."
                except sqlite3.IntegrityError:
                    message_response = "Errore: questa associazione prodotto-utente esiste già. Digita /list per visualizzare tutti i prodotti che hai inserito nel nostro sistema."
            else:
                message_response = 'Prodotto già presente nella tua lista dei prodotti che stai monitorando.'

        except sqlite3.Error as e:
            message_response = f"Errore durante l'accesso al database: {e}"

        return message_response
    
    def get_user_products(self, userid):
        try:
            self.c.execute("""
                SELECT P.* FROM products AS P 
                LEFT JOIN product_user AS PU ON P.id = PU.product_id 
                LEFT JOIN users AS U ON PU.user_id = U.id 
                WHERE U.idtelegram = ?
            """, (userid,))
            return self.c.fetchall()
        except sqlite3.Error as e:
            print(f"Errore durante l'accesso al database: {e}")
            return []
        
    def delete_by_asin(self, asin, user):
        try:
            self.c.execute("""
                SELECT PU.id FROM products AS P
                LEFT JOIN product_user AS PU ON P.id = PU.product_id
                LEFT JOIN users AS U ON PU.user_id = U.id
                WHERE P.asin = ? AND U.idtelegram = ? 
            """, (asin, user))
            result_id = self.c.fetchone()

            if result_id[0]:
                self.c.execute("DELETE FROM product_user WHERE id = ?", (result_id[0],))
                self.conn.commit()

                return "Prodotto eliminato correttamente, continua ad aggiungere prodotti da monitorare con /url. Digita /help per maggiori informazioni."
            else:
                return "Non è stato un ASIN corrispondente"
        except sqlite3.Error as e:
            print(f"Errore durante l'accesso al database: {e}")
            return []

    def get_price_for_scraping(self):
        try:
            self.c.execute("""SELECT id, price, url FROM products""")
            return self.c.fetchall()
        except sqlite3.Error as e:
            print(f"Errore durante l'accesso al database: {e}")
            return []
        
    def get_recent_price_changes(self):
        now = datetime.now().strftime('%Y-%m-%d')
        try:
            self.c.execute("""SELECT P.product_name, P.url, U.idtelegram, VP.newprice, VP.oldprice 
                FROM variation_price AS VP 
                LEFT JOIN products AS P ON VP.idprodotto = P.id 
                LEFT JOIN product_user AS PU ON P.id = PU.product_id 
                LEFT JOIN users AS U ON PU.user_id = U.id
                WHERE VP.updated_at = ?
            """, (now,))
            return self.c.fetchall()
        except sqlite3.Error as e:
            print(f"Errore durante l'accesso al database: {e}")
            return []
        
    def update_variation_price(self, idprod, oldprice, newprice):
        now = datetime.now().strftime('%Y-%m-%d')
        try:
            self.c.execute("""
                INSERT INTO variation_price (idprodotto, oldprice, newprice, updated_at) 
                VALUES (?, ?, ?, ?)    
            """, (idprod, oldprice, newprice, now))
            return self.conn.commit()
        except sqlite3.IntegrityError:
            return "Errore: questa associazione prodotto-utente esiste già. Digita /list per visualizzare tutti i prodotti che hai inserito nel nostro sistema."
