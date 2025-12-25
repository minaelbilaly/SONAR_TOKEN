from flask import Flask, request, jsonify
import sqlite3
import subprocess
import hashlib
import os
import ast

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify(status="success", user=username)

    return jsonify(status="error", message="Invalid credentials"), 401


@app.route("/ping", methods=["POST"])
def ping():
    data = request.get_json(force=True)
    host = data.get("host", "")
    cmd = ["ping", "-c", "1", host]
    output = subprocess.check_output(cmd, timeout=5)
    return jsonify(output=output.decode())


@app.route("/compute", methods=["POST"])
def compute():
    data = request.get_json(force=True)
    expression = data.get("expression", "")

    # ✅ Sécurisé : pas de eval
    try:
        result = ast.literal_eval(expression)
    except Exception:
        return jsonify(error="Invalid expression"), 400

    return jsonify(result=result)


@app.route("/hash", methods=["POST"])
def hash_password():
    data = request.get_json(force=True)
    pwd = data.get("password", "")
    hashed = hashlib.sha256(pwd.encode()).hexdigest()
    return jsonify(sha256=hashed)


@app.route("/hello", methods=["GET"])
def hello():
    return jsonify(message="Welcome to the DevSecOps secure API")


if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    app.run(host=host, port=5000, debug=False)
