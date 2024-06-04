from flask import Flask, jsonify, render_template
from database_manager import DatabaseManager
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, logger
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DM = DatabaseManager(DB_HOST, DB_USER, DB_PASS, DB_NAME)

@app.route('/api/users', methods=['GET'])
def get_users():
    users_with_products = DM.get_all_users_with_products()
    return jsonify(users_with_products)

@app.route('/api/products', methods=['GET'])
def get_products():
    all_products = DM.get_all_products()
    return jsonify(all_products)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = DM.get_info_data(product_id)
    return jsonify(product)

@app.route('/')
def index():
    return render_template('analisi-bot.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')