import network
import socket
import time
import os
import json
from machine import Pin
import secrets

RELAY_PIN = 15
CONFIG_FILE = "config.json"

relay = Pin(RELAY_PIN, Pin.OUT, value=0)

# Rate limiting: track unlock attempts by IP
rate_limit = {}
RATE_WINDOW = 60
RATE_MAX = 10

def get_unlock_duration():
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        return cfg.get("unlockDuration", 2)
    except:
        return getattr(secrets, "UNLOCK_DURATION", 2)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    print("Connecting to WiFi...")
    for _ in range(20):
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print("Connected:", ip)
            print("Serving on http://" + ip)
            return ip, wlan
        time.sleep(1)
    raise RuntimeError("WiFi connection failed")

def ensure_wifi(wlan):
    if not wlan.isconnected():
        print("WiFi lost, reconnecting...")
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        for _ in range(20):
            if wlan.isconnected():
                print("Reconnected:", wlan.ifconfig()[0])
                return True
            time.sleep(1)
        print("Reconnect failed")
        return False
    return True

def is_rate_limited(client_ip):
    now = time.time()
    if client_ip not in rate_limit:
        rate_limit[client_ip] = []
    rate_limit[client_ip] = [t for t in rate_limit[client_ip] if now - t < RATE_WINDOW]
    if len(rate_limit[client_ip]) >= RATE_MAX:
        return True
    rate_limit[client_ip].append(now)
    return False

def unlock():
    dur = get_unlock_duration()
    relay.high()
    time.sleep(dur)
    relay.low()

def config_exists():
    try:
        os.stat(CONFIG_FILE)
        return True
    except:
        return False

def send_html(conn):
    size = os.stat("picolock.html")[6]
    header = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        "Content-Length: " + str(size) + "\r\n"
        "Connection: close\r\n\r\n"
    )
    conn.send(header.encode())
    with open("picolock.html", "rb") as f:
        while True:
            chunk = f.read(256)
            if not chunk:
                break
            conn.send(chunk)
            time.sleep(0.01)

def send_json(conn, body):
    conn.send(("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body)) + "\r\nConnection: close\r\n\r\n").encode())
    conn.send(body.encode())

def send_ok(conn):
    conn.send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok")

def send_404(conn):
    conn.send(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")

def send_429(conn):
    conn.send(b"HTTP/1.1 429 Too Many Requests\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")

def get_body(conn, request):
    parts = request.split("\r\n\r\n", 1)
    body = parts[1] if len(parts) > 1 else ""
    for line in request.split("\r\n"):
        if line.lower().startswith("content-length:"):
            total = int(line.split(":")[1].strip())
            while len(body) < total:
                more = conn.recv(512)
                if not more:
                    break
                body += more.decode("utf-8", "ignore")
            break
    return body

def serve(ip, wlan):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(3)
    while True:
        ensure_wifi(wlan)
        conn, client_addr = s.accept()
        client_ip = client_addr[0]
        try:
            request = conn.recv(2048).decode("utf-8", "ignore")
            if not request:
                continue
            if "POST /unlock" in request:
                if is_rate_limited(client_ip):
                    print("Rate limited:", client_ip)
                    send_429(conn)
                else:
                    unlock()
                    send_ok(conn)
            elif "GET /config" in request:
                if config_exists():
                    with open(CONFIG_FILE, "r") as f:
                        data = f.read()
                    send_json(conn, data)
                else:
                    send_404(conn)
            elif "GET /manifest.json" in request:
                try:
                    with open("manifest.json", "r") as f:
                        data = f.read()
                    conn.send(("HTTP/1.1 200 OK\r\nContent-Type: application/manifest+json\r\nContent-Length: " + str(len(data)) + "\r\nConnection: close\r\n\r\n").encode())
                    conn.send(data.encode())
                except:
                    send_404(conn)
            elif "GET /info" in request:
                info = json.dumps({"ip": ip})
                send_json(conn, info)
            elif "POST /save" in request:
                body = get_body(conn, request)
                if body:
                    with open(CONFIG_FILE, "w") as f:
                        f.write(body)
                send_ok(conn)
            elif "POST /wipe" in request:
                try:
                    os.remove(CONFIG_FILE)
                except:
                    pass
                send_ok(conn)
            else:
                send_html(conn)
        except Exception as e:
            print("Error:", e)
        finally:
            conn.close()

ip, wlan = connect_wifi()
serve(ip, wlan)
