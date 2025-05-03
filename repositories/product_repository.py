class ProductRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def list_user_tracked_products(self, user_id):
        return self.db.get_user_products(user_id)

    def get_price_change(self, product_id):
        return self.db.get_diff_price_by_productid(product_id)

    def get_product_details(self, product_id):
        return self.db.get_info_data(product_id)

    def track_product_for_user(self, user_id, username, product_data):
        return self.db.insert_into_db(user_id, username, product_data)

    def delete_user_product(self, product_id, user_id):
        return self.db.delete_by_productid(product_id, user_id)

    def share_url_for_product(self, product_id, user_id):
        from urllib import parse
        params = f"{product_id}_{user_id}"
        encoded = parse.quote_plus(params)
        return f"https://t.me/bestpriceamzbot?start={encoded}"

    def associate_existing_product_to_user(self, product_id, user_id, username):
        params = {
            "telegram_id": user_id,
            "product_id": int(product_id),
            "username_dest": username
        }
        return self.db.insert_new_productuser(params)

    def get_username_by_telegram_id(self, telegram_id):
        result = self.db.get_username_from_idtelegram(telegram_id)
        return result[0][0] if result and result[0] else None
