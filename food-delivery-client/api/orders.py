from http.server import BaseHTTPRequestHandler
import json
import psycopg2
import os

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        try:
            conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
            c = conn.cursor()
            
            c.execute('SELECT * FROM orders ORDER BY timestamp DESC')
            rows = c.fetchall()
            
            conn.close()
            
            orders = []
            for r in rows:
                orders.append({
                    "id": r[0],
                    "user_name": r[1],
                    "address": r[2],
                    "city": r[3],
                    "zip_code": r[4],
                    "phone": r[5],
                    "cart_data": json.loads(r[6]) if isinstance(r[6], str) else r[6],
                    "total_price": r[7],
                    "timestamp": str(r[8]),
                    "status": r[9]
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(orders).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
