import http.server
import socketserver
import sqlite3
import json
import os
from urllib.parse import urlparse

PORT = 8000
DB_FILE = "orders.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            address TEXT,
            city TEXT,
            zip_code TEXT,
            phone TEXT,
            cart_data TEXT,
            total_price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    try:
        c.execute('ALTER TABLE orders ADD COLUMN status TEXT DEFAULT "Pending"')
    except sqlite3.OperationalError:
        pass # Column likely already exists
    conn.commit()
    conn.close()

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/orders':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT * FROM orders ORDER BY timestamp DESC')
            rows = c.fetchall()
            conn.close()
            
            orders = []
            for r in rows:
                status_val = r[9] if len(r) > 9 else "Pending"
                orders.append({
                    "id": r[0],
                    "user_name": r[1],
                    "address": r[2],
                    "city": r[3],
                    "zip_code": r[4],
                    "phone": r[5],
                    "cart_data": json.loads(r[6]),
                    "total_price": r[7],
                    "timestamp": r[8],
                    "status": status_val
                })
            
            self.wfile.write(json.dumps(orders).encode())
            
        elif parsed_path.path == '/api/sales/summary':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Today's Revenue
            c.execute("SELECT SUM(total_price) FROM orders WHERE date(timestamp) = date('now', 'localtime')")
            today_res = c.fetchone()[0]
            today_revenue = today_res if today_res else 0
            
            # Daily Sales
            c.execute("SELECT date(timestamp, 'localtime'), id, total_price FROM orders ORDER BY date(timestamp, 'localtime') DESC, id DESC")
            raw_daily = c.fetchall()
            daily_dict = {}
            for row in raw_daily:
                date_str = row[0]
                order_id = row[1]
                price = row[2]
                if date_str not in daily_dict:
                    daily_dict[date_str] = {"date": date_str, "revenue": 0, "order_list": []}
                daily_dict[date_str]["revenue"] += price
                daily_dict[date_str]["order_list"].append({"id": order_id, "amount": price})
            daily_sales = list(daily_dict.values())[:30]
            
            # Monthly Sales
            c.execute("SELECT strftime('%Y-%m', timestamp, 'localtime'), SUM(total_price), COUNT(id) FROM orders GROUP BY strftime('%Y-%m', timestamp, 'localtime') ORDER BY strftime('%Y-%m', timestamp, 'localtime') DESC LIMIT 12")
            monthly_rows = c.fetchall()
            monthly_sales = [{"month": r[0], "revenue": r[1], "orders": r[2]} for r in monthly_rows]
            
            conn.close()
            
            summary = {
                "today_revenue": today_revenue,
                "daily_sales": daily_sales,
                "monthly_sales": monthly_sales
            }
            self.wfile.write(json.dumps(summary).encode())
            
        else:
            # Serve static files as usual
            super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/order':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_name = data.get('user_name', 'Guest')
            address = data.get('address', '')
            city = data.get('city', '')
            zip_code = data.get('zip_code', '')
            phone = data.get('phone', '')
            cart_data = json.dumps(data.get('cart', []))
            
            # Calculate total
            total = sum(item['price'] * item['quantity'] for item in data.get('cart', []))
            
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('''
                INSERT INTO orders (user_name, address, city, zip_code, phone, cart_data, total_price, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')
            ''', (user_name, address, city, zip_code, phone, cart_data, total))
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "success", "message": "Order placed successfully"}
            self.wfile.write(json.dumps(response).encode())

        elif parsed_path.path == '/api/order/status':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            order_id = data.get('id')
            new_status = data.get('status')
            
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "success", "message": "Order status updated"}
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    init_db()
    Handler = MyRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
