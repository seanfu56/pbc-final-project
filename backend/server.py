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
            create = db_api.create_user(username, password)
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

        elif self.path == '/fetch':
            username = data.get('username', [""])[0]
            mode = data.get('mode', [""])[0]
            email_list = db_api.fetch_all_email(mode, username)

            email_list = [
                {
                    "uid": row[0],
                    "sender": row[1],
                    "receiver": row[2],
                    "title": row[3],
                    "content": row[4],
                    "timestamp": row[5]
                }
                for row in email_list
            ]

            print(email_list)
            self._send_response({
                "status": "ok",
                "emails": email_list
            })

        elif self.path == '/send':
            sender = data.get("sender", [""])[0]
            receiver = data.get("receiver", [""])[0]
            title = data.get("title", [""])[0]
            content = data.get("content", [""])[0]

            db_api.send_email(
                sender=sender,
                receiver=receiver,
                title=title,
                content=content
            )

            self._send_response({"status": "ok", "msg": "received"})

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