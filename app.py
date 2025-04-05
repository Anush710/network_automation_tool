from flask import Flask, request, jsonify, render_template
from netmiko import ConnectHandler
import sqlite3
import subprocess
import platform

app = Flask(__name__)

# Initialize database if it doesn't exist
def init_db():
    conn = sqlite3.connect('routers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS routers (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 ip TEXT,
                 username TEXT,
                 password TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Get router details by IP
def get_router(ip):
    conn = sqlite3.connect('routers.db')
    c = conn.cursor()
    c.execute("SELECT ip, username, password, name FROM routers WHERE ip=?", (ip,))
    router = c.fetchone()
    conn.close()
    return router

# Execute SSH command on router
def run_command(ip, command):
    router = get_router(ip)
    if not router:
        return "Router not found in database."
    
    device = {
        'device_type': 'cisco_ios',
        'host': router[0],
        'username': router[1],
        'password': router[2],
    }
    try:
        connection = ConnectHandler(**device)
        output = connection.send_command(command)
        connection.disconnect()
        return output
    except Exception as e:
        return str(e)

# Check router status using ping
def check_router_status(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    try:
        result = subprocess.run(['ping', param, '1', ip], capture_output=True, text=True, timeout=5)
        if "TTL=" in result.stdout or "ttl=" in result.stdout:
            return "Online"
        else:
            return "Offline"
    except Exception:
        return "Error"

# Route for command page (default homepage)
@app.route("/")
def index():
    return render_template("index.html")

# Route to handle sending commands (handles both form and JSON)
@app.route("/run", methods=["GET", "POST"])
def run_command_route():
    ip = None
    command = None

    if request.method == "POST":
        if request.content_type == "application/json":
            data = request.get_json()
            ip = data.get("ip")
            command = data.get("command")
        else:
            ip = request.form.get("ip")
            command = request.form.get("command")
    
    if not ip or not command:
        return render_template("index.html", output="IP or command missing")

    output = run_command(ip, command)
    return render_template("index.html", output=output)

# Route for dashboard page
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("routers.db")
    c = conn.cursor()
    c.execute("SELECT id, name, ip FROM routers")
    routers = c.fetchall()
    conn.close()

    router_statuses = []
    for router in routers:
        router_id, name, ip = router
        status = check_router_status(ip)
        router_statuses.append({
            "id": router_id,
            "name": name,
            "ip": ip,
            "status": status
        })
    
    return render_template("dashboard.html", routers=router_statuses)

# Route for monitoring settings page (stub for now)
@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")

# API endpoint to add a router to the database
@app.route("/add_router", methods=["POST"])
def add_router():
    data = request.json
    name, ip, username, password = data['name'], data['ip'], data['username'], data['password']
    conn = sqlite3.connect('routers.db')
    c = conn.cursor()
    c.execute("INSERT INTO routers (name, ip, username, password) VALUES (?, ?, ?, ?)",
              (name, ip, username, password))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Router added successfully'})

if __name__ == '__main__':
    app.run(debug=True)
