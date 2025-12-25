from flask import Flask, request
import sqlite3
import subprocess
import hashlib
import os
import ast

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ✅ Requête préparée (anti SQL injection)
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return {"status": "success", "user": username}
    return {"status": "error", "message": "Invalid credentials"}, 401


@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")
    # ✅ Pas de shell=True
    cmd = ["ping", "-c", "1", host]
    output = subprocess.check_output(cmd, timeout=3)
    return {"output": output.decode()}


@app.route("/compute", methods=["POST"])
def compute():
    expression = request.json.get("expression", "")

    try:
        # ✅ Remplacement de eval par ast.literal_eval
        result = ast.literal_eval(expression)
    except Exception:
        return {"error": "Invalid expression"}, 400

    return {"result": result}


@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password", "")
    # ✅ SHA256 OK
    hashed = hashlib.sha256(pwd.encode()).hexdigest()
    return {"sha256": hashed}


@app.route("/readfile", methods=["POST"])
def readfile():
    filename = request.json.get("filename", "")

    # ✅ Protection contre path traversal
    if ".." in filename or filename.startswith("/"):
        return {"error": "Invalid filename"}, 400

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    return {"content": content}


@app.route("/hello", methods=["GET"])
def hello():
    return {"message": "Secure DevSecOps API"}


if __name__ == "__main__":
    # ❌ debug désactivé
    app.run(host="0.0.0.0", port=5000, debug=False)
