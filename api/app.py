from flask import Flask, request
import sqlite3
import subprocess
import hashlib
import os

app = Flask(__name__)
SECRET_KEY = "dev-secret-key-12345"

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ⚠️ Vulnérable (SQL injection) mais Bandit ne le détecte pas
    # À corriger si besoin : use prepared statements
    query = "SELECT * FROM users WHERE username=? AND password=?"
    cursor.execute(query, (username, password))

    result = cursor.fetchone()
    if result:
        return {"status": "success", "user": username}
    return {"status": "error", "message": "Invalid credentials"}


@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")
    # ✅ FIX: pas de shell=True
    cmd = ["ping", "-c", "1", host]
    output = subprocess.check_output(cmd)
    return {"output": output.decode()}


@app.route("/compute", methods=["POST"])
def compute():
    expression = request.json.get("expression", "1+1")
    # ⚠️ eval est dangereux → Bandit peut aussi détecter
    # Exemple simple sécurisé :
    try:
        safe = eval(expression, {"__builtins__": {}}, {})
    except Exception:
        return {"error": "Invalid expression"}
    return {"result": safe}


@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password", "admin")
    # ✅ FIX : MD5 → SHA256
    hashed = hashlib.sha256(pwd.encode()).hexdigest()
    return {"sha256": hashed}


@app.route("/readfile", methods=["POST"])
def readfile():
    filename = request.json.get("filename", "test.txt")
    with open(filename, "r") as f:
        content = f.read()
    return {"content": content}


@app.route("/debug", methods=["GET"])
def debug():
    return {
        "debug": True,
        "secret_key": SECRET_KEY,
        "environment": dict(os.environ)
    }


@app.route("/hello", methods=["GET"])
def hello():
    return {"message": "Welcome to the DevSecOps vulnerable API"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
