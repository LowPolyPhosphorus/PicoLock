import network
import socket
import time
import os
import json
from machine import Pin
import secrets

RELAY_PIN = 15
UNLOCK_DURATION = secrets.UNLOCK_DURATION if hasattr(secrets, 'UNLOCK_DURATION') else 2
CONFIG_FILE = "config.json"

relay = Pin(RELAY_PIN, Pin.OUT)
relay.low()

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    print("Connecting to WiFi...")
    for _ in range(20):
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print("Connected:", ip)
            return ip
        time.sleep(1)
    raise RuntimeError("WiFi connection failed")

def unlock():
    relay.high()
    time.sleep(UNLOCK_DURATION)
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

def get_body(request):
    parts = request.split("\r\n\r\n", 1)
    return parts[1] if len(parts) > 1 else ""

def serve(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(3)
    print("Serving on http://" + ip)

    while True:
        conn, addr = s.accept()
        try:
            request = conn.recv(2048).decode("utf-8", "ignore")
            if not request:
                continue

            if "POST /unlock" in request:
                unlock()
                send_ok(conn)

            elif "GET /config" in request:
                if config_exists():
                    with open(CONFIG_FILE, "r") as f:
                        data = f.read()
                    send_json(conn, data)
                else:
                    send_404(conn)

            elif "POST /save" in request:
                body = get_body(request)
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

ip = connect_wifi()
serve(ip)
