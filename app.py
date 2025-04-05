from flask import Flask, request, jsonify, render_template
from netmiko import ConnectHandler
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["GET", "POST"])
def run_command():
    ip = None
    command = None

    if request.method == "POST":
        # Check if it's a JSON request
        if request.content_type == "application/json":
            data = request.get_json()
            ip = data.get("ip")
            command = data.get("command")
        else:
            # Assume it's a form submission from the web UI
            ip = request.form.get("ip")
            command = request.form.get("command")

    if not ip or not command:
        return render_template("index.html", output="IP or command missing")

    # Fetch credentials from DB
    conn = sqlite3.connect("routers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM routers WHERE ip = ?", (ip,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return render_template("index.html", output="Router not found in database.")

    username, password = row
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": username,
        "password": password,
    }

    try:
        net_connect = ConnectHandler(**device)
        output = net_connect.send_command(command)
        net_connect.disconnect()
    except Exception as e:
        output = f"Error connecting to router: {str(e)}"

    return render_template("index.html", output=output)

