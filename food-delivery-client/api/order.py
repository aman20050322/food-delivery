from http.server import BaseHTTPRequestHandler
import json
import psycopg2
import os

def get_db_connection():
    # Attempt to connect to the Postgres URL provided by Vercel
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    
    # Create the table if it doesn't exist (good practice for init)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_name TEXT,
            address TEXT,
            city TEXT,
            zip_code TEXT,
            phone TEXT,
            cart_data TEXT,
            total_price REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    c.close()
    return conn

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_name = data.get('user_name', 'Guest')
            address = data.get('address', '')
            city = data.get('city', '')
            zip_code = data.get('zip_code', '')
            phone = data.get('phone', '')
            cart_data = json.dumps(data.get('cart', []))
            total = sum(item['price'] * item['quantity'] for item in data.get('cart', []))
            
            conn = get_db_connection()
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO orders (user_name, address, city, zip_code, phone, cart_data, total_price, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
            ''', (user_name, address, city, zip_code, phone, cart_data, total))
            
            conn.commit()
            c.close()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Order placed successfully"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
