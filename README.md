# Network Automation & Monitoring Tool

A simple Flask-based web tool to automate and monitor routers (tested on GNS3 routers with SSH access).

## Features
- SSH into routers using IP, username, and password
- Run commands via web interface
- Stores router details in SQLite database

## Technologies
- Flask (Python)
- Netmiko (for SSH)
- SQLite
- HTML (basic frontend)

## Usage

1. Start Flask app:
```bash
python app.py
