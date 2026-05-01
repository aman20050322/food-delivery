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
            
            # Today's Revenue
            c.execute("SELECT SUM(total_price) FROM orders WHERE DATE(timestamp) = CURRENT_DATE AND status != 'Cancelled'")
            today_res = c.fetchone()[0]
            today_revenue = today_res if today_res else 0
            
            # Daily Sales Detailed
            c.execute("SELECT DATE(timestamp), id, total_price FROM orders WHERE status != 'Cancelled' ORDER BY DATE(timestamp) DESC, id DESC")
            raw_daily = c.fetchall()
            daily_dict = {}
            for row in raw_daily:
                date_str = str(row[0])
                order_id = row[1]
                price = row[2]
                if date_str not in daily_dict:
                    daily_dict[date_str] = {"date": date_str, "revenue": 0, "order_list": []}
                daily_dict[date_str]["revenue"] += price
                daily_dict[date_str]["order_list"].append({"id": order_id, "amount": price})
            daily_sales = list(daily_dict.values())[:30]
            
            # Monthly Sales
            c.execute("SELECT TO_CHAR(timestamp, 'YYYY-MM'), SUM(total_price), COUNT(id) FROM orders WHERE status != 'Cancelled' GROUP BY TO_CHAR(timestamp, 'YYYY-MM') ORDER BY TO_CHAR(timestamp, 'YYYY-MM') DESC LIMIT 12")
            monthly_rows = c.fetchall()
            monthly_sales = [{"month": str(r[0]), "revenue": r[1], "orders": r[2]} for r in monthly_rows]
            
            conn.close()
            
            summary = {
                "today_revenue": today_revenue,
                "daily_sales": daily_sales,
                "monthly_sales": monthly_sales
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(summary).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
