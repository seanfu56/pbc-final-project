from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import base64
import db_api
from utils.spam import spam_detection
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
            content_type = self.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                data = json.loads(body.decode())
            else:
                data = urllib.parse.parse_qs(body.decode())

            username = data.get("username") if isinstance(data.get("username"), str) else data.get("username", [""])[0]
            password = data.get("password") if isinstance(data.get("password"), str) else data.get("password", [""])[0]
            print(f'Login. Username: {username}, Password: {password}')
            login_success, categories = db_api.login(
                username=username,
                input_password=password
            )
            categories = categories[0]
            print("categories: ", categories, json.loads(categories))
            if login_success:
                self._send_response(
                    {
                        "status": "ok",
                        "msg": "login successfully",
                        "categories": categories
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
                    "timestamp": row[5],
                    "system_type": row[6],
                    "user_type": row[7],
                    "read_status": row[8],
                    "image_uids": row[9],
                    "category": row[10],
                    'recall': row[11],
                    "image_list": []
                }
                for row in email_list if row[11] != 1
            ]



            for email in email_list:
                print('USER TYPE', email['user_type'])

            for email in email_list:
                if email['image_uids'] is not None:
                    print("EMAIL UUID", email['image_uids'], type(email["image_uids"]))
                    email_image_uid_list = json.loads(email['image_uids'])
                    for email_image_uid in email_image_uid_list:
                        image_data = db_api.get_image(email_image_uid)
                        image_str = image_data[2]
                        email["image_list"].append(image_str)
                    #     email_image_str_list.append(image_str)
                    # email['image_list'] = email_image_str_list

            self._send_response({
                "status": "ok",
                "emails": email_list
            })

        elif self.path == '/fetch_draft':
            username = data.get('username', [""])[0]
            email_list = db_api.fetch_all_draft(username)

            email_list = [
                {
                    "uid": row[0],
                    "sender": row[1],
                    "receiver": row[2],
                    "title": row[3],
                    "content": row[4],
                    "timestamp": row[5],
                    "image_uids": row[6],
                }
                for row in email_list
            ]

            print(email_list)
            self._send_response({
                "status": "ok",
                "emails": email_list
            })

        elif self.path == '/trash':
            content_type = self.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = json.loads(body.decode('utf-8'))  # ✅ 正確解析 JSON
            else:
                data = urllib.parse.parse_qs(body.decode())  # fallback for form data

            email_id = data.get("email_id", "")[0]
            print("TRASH", email_id)
            db_api.change_email_user_type(
                mode='trash',
                id=email_id
            )

            self._send_response({
                'status': 'ok',
            })

        elif self.path == '/send':
            content_type = self.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = json.loads(body.decode('utf-8'))  # ✅ 正確解析 JSON
                print("parse with json")
                sender = data.get("sender", "")
                receiver = data.get("receiver", "")
                title = data.get("title", "")
                content = data.get("content", "")
                image_list = data.get("image_list", [])

            else:
                data = urllib.parse.parse_qs(body.decode())  # fallback for form data
                print("parse with urllib")
                sender = data.get("sender", "")[0]
                receiver = data.get("receiver", "")[0]
                title = data.get("title", "")[0]
                content = data.get("content", "")[0]
                if data.get('image_list'):
                    image_list = data.get("image_list", [])[0]
                else:
                    image_list = None


            print(f"SEND email from {sender} to {receiver}")
            # print(f"image_list length: {len(image_list)}")

            spam = spam_detection(content)

            db_api.send_email(
                sender=sender,
                receiver=receiver,
                title=title,
                content=content,
                system_type=spam,
                image=image_list
            )

            if spam == 'spam':

                self._send_response({'status': 'ok', 'msg': 'spam'})

            else:

                self._send_response({"status": "ok", "msg": "received"})

        elif self.path == "/message":
            msg = data.get("message", [""])[0]
            print(f"[MESSAGE] 收到訊息：{msg}")
            self._send_response({"status": "ok", "msg": "訊息收到"})

        elif self.path == '/draft':
            sender = data.get("sender", [""])[0]
            receiver = data.get("receiver", [""])[0]
            title = data.get("title", [""])[0]
            content = data.get("content", [""])[0]

            db_api.send_draft(
                sender=sender,
                receiver=receiver,
                title=title,
                content=content
            )

            self._send_response({'status': 'ok', 'msg': '草稿儲存成功'})

        elif self.path == '/mark_read':
            email_id = data.get("email_id", [""])[0]
            read_status = data.get("read_status", [""])[0]
            print("標記為已讀", read_status)

            if read_status:
                read_status_int = 1
            else:
                read_status_int = 0

            db_api.mark_read(email_id, read_status_int)

            self._send_response({'status': 'ok', 'msg': '已讀狀態更新'})

        elif self.path == '/new_cat':
            username = data.get("username", [""])[0]
            category = data.get("category", [""])[0]
            color = data.get("color", [""])[0]

            db_api.create_category(username, category, color)

            self._send_response({'status': 'ok', 'msg': '新增類別成功'})

        # elif self.path == '/del_cat':
        elif self.path == '/set_cat':
            username = data.get("username", [""])[0]
            email_id = data.get("email_id", [""])[0]
            category = data.get("category", [""])[0]
            print("set_cat:", username, email_id, category)
            db_api.set_category(
                username, email_id, category
            )

            self._send_response({'status': 'ok', 'msg': '成功修改類別'})

        elif self.path == '/recall':
            email_id = data.get("email_id", [""])[0]
            print("RECALL EMAIL")
            db_api.recall(
                email_id
            )
            self._send_response({'status': 'ok', 'msg': '成功收回信件'})

        else:
            self._send_response({"status": "error", "msg": "未知路由"}, code=404)

    def _send_response(self, json_data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(json_data).encode("utf-8"))

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    print("伺服器啟動：http://localhost:8080")
    server.serve_forever()