from flask import Flask, jsonify
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')