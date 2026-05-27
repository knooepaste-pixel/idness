#!/usr/bin/env python3
"""KIDNESS API + cloud-to-local task queue"""
import json, os, hashlib, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE = "/var/www/kidness"
FILES = {"users": f"{BASE}/users.json", "comments": f"{BASE}/comments.json", "reservations": f"{BASE}/reservations.json", "tasks": f"{BASE}/tasks.json"}

def load(name):
    path = FILES[name]
    if not os.path.exists(path): return []
    with open(path) as f: return json.load(f)
def save(name, data):
    with open(FILES[name], "w") as f: json.dump(data, f, ensure_ascii=False)
def hash_pw(s): return hashlib.sha256(s.encode()).hexdigest()

class Handler(BaseHTTPRequestHandler):
    def _ok(self, data):
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    def _err(self, msg, code=400):
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers()
        self.wfile.write(json.dumps({"error": msg}, ensure_ascii=False).encode())
    def do_OPTIONS(self):
        self.send_response(200); self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type"); self.end_headers()

    def do_GET(self):
        q = urlparse(self.path)
        p = q.path
        if p == "/comments":
            product = parse_qs(q.query).get("product", [None])[0]
            items = load("comments")
            if product: items = [c for c in items if c.get("product") == product]
            return self._ok({"items": items})
        if p == "/tasks/pending":
            tasks = load("tasks")
            pending = [t for t in tasks if t.get("status") == "pending"]
            return self._ok({"items": pending})
        return self._err("Not found", 404)

    def do_POST(self):
        p = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        b = json.loads(self.rfile.read(length)) if length > 0 else {}

        if p == "/register":
            u = (b.get("username") or "").strip()
            pw = (b.get("password") or "").strip()
            n = (b.get("nickname") or u).strip()
            if len(u) < 3: return self._err("用户名至少3位")
            if len(pw) < 6: return self._err("密码至少6位")
            users = load("users")
            if any(x["username"] == u for x in users): return self._err("该用户名已被注册")
            users.append({"username": u, "password": hash_pw(pw), "nickname": n, "createdAt": time.time()})
            save("users", users)
            return self._ok({"ok": True, "name": n})
        if p == "/login":
            u = (b.get("username") or "").strip()
            pw = (b.get("password") or "").strip()
            user = next((x for x in load("users") if x["username"] == u), None)
            if not user or user["password"] != hash_pw(pw): return self._err("用户名或密码错误", 401)
            return self._ok({"ok": True, "name": user["nickname"]})
        if p == "/comments/add":
            txt = (b.get("text") or "").strip()
            if not txt: return self._err("写点什么吧")
            cmts = load("comments")
            cmts.insert(0, {"product": (b.get("product") or "").strip(), "name": (b.get("name") or "匿名").strip(), "text": txt, "createdAt": time.time()})
            if len(cmts) > 500: cmts = cmts[:500]
            save("comments", cmts)
            return self._ok({"ok": True})
        if p == "/reservations":
            if not (b.get("name") or "").strip(): return self._err("请填写称呼")
            if not (b.get("contact") or "").strip(): return self._err("请填写联系方式")
            rsv = load("reservations")
            rsv.append({"name": b.get("name","").strip(), "contact": b.get("contact","").strip(), "piece": b.get("piece","").strip(), "note": b.get("note","").strip(), "createdAt": time.time()})
            save("reservations", rsv)
            return self._ok({"ok": True})
        if p == "/tasks/add":
            task = (b.get("task") or "").strip()
            if not task: return self._err("task required")
            tasks = load("tasks")
            tasks.append({"id": str(time.time()).replace(".",""), "task": task, "context": b.get("context",""), "status": "pending", "createdAt": time.time()})
            if len(tasks) > 100: tasks = tasks[-100:]
            save("tasks", tasks)
            return self._ok({"ok": True})
        if p == "/tasks/done":
            tid = b.get("id", "")
            result = b.get("result", "")
            tasks = load("tasks")
            for t in tasks:
                if t["id"] == tid:
                    t["status"] = "done"
                    t["result"] = result
                    t["doneAt"] = time.time()
                    break
            save("tasks", tasks)
            return self._ok({"ok": True})
        return self._err("Not found", 404)
    def log_message(self, *a): pass

HTTPServer(("127.0.0.1", 3001), Handler).serve_forever()
