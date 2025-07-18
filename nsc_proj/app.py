from flask import Flask, render_template, request, jsonify, redirect
from database import init_db, get_all_products
from robot_controller import send_robot_command

import sqlite3
app = Flask(__name__)
init_db()

@app.route('/')
def index():
    products = get_all_products()
    # products = [('A1','Product A1',10), ('A2','Product A2',8), ...]
    return render_template('index.html', products=products)

@app.route('/order', methods=['POST'])
def order_product():
    data = request.get_json()
    product_code = data.get('product')

    if not product_code:
        return jsonify({"error": "Missing product code"}), 400


    result = send_robot_command(product_code)


    update_stock(product_code)

    return jsonify({"message": "Order sent", "result": result})

def update_stock(product_code):
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()


    c.execute('SELECT stock FROM products WHERE code = ?', (product_code,))
    row = c.fetchone()
    if row and row[0] > 0:
        new_stock = row[0] - 1
        c.execute('UPDATE products SET stock = ? WHERE code = ?', (new_stock, product_code))
        conn.commit()

    conn.close()


if __name__ == '__main__':
    app.run(debug=True)

# โค้ดเดิมก่อนหน้านี้
# import sqlite3
# from flask import Flask, request, jsonify, render_template
# from robot_controller import send_robot_command

# from database import init_db
# init_db()

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/order', methods=['POST'])
# def order_product():
#     data = request.get_json()
#     product_code = data.get('product')

#     if not product_code:
#         return jsonify({"error": "Missing product code"}), 400

#     result = send_robot_command(product_code)
#     return jsonify({"message": "Order sent", "result": result})


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
