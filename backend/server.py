from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json

import db_api

class SimpleHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(body.decode())
        
        # 路由分支處理
        if self.path == "/create":
            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]
            print(f"[CREATE] 建立帳號：{username}，密碼：{password}")
            self._send_response({"status": "ok", "msg": "帳號已建立"})
        
        elif self.path == '/login':
            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]
            print(f'Login. Username: {username}, Password: {password}')
            login_success = db_api.login(
                username=username,
                input_password=password
            )
            if login_success:
                self._send_response(
                    {
                        "status": "ok",
                        "msg": "login successfully"
                    }
                )
            else:
                self._send_response(
                    {
                        "status": "fail",
                        "msg": "login unsuccessfully"
                    }
                )

        elif self.path == "/message":
            msg = data.get("message", [""])[0]
            print(f"[MESSAGE] 收到訊息：{msg}")
            self._send_response({"status": "ok", "msg": "訊息收到"})

        else:
            self._send_response({"status": "error", "msg": "未知路由"}, code=404)

    def _send_response(self, json_data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(json_data).encode("utf-8"))

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8080), SimpleHandler)
    print("伺服器啟動：http://localhost:8080")
    server.serve_forever()