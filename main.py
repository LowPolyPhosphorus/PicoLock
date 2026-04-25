import network
import socket
import time
from machine import Pin
import secrets

RELAY_PIN = 15
UNLOCK_DURATION = secrets.UNLOCK_DURATION if hasattr(secrets, 'UNLOCK_DURATION') else 2

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

def send_response(conn, status, content_type, body):
    body_bytes = body if isinstance(body, bytes) else body.encode()
    header = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n\r\n"
    )
    conn.send(header.encode())
    # send in chunks in case file is large
    chunk = 512
    for i in range(0, len(body_bytes), chunk):
        conn.send(body_bytes[i:i+chunk])

def serve(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(3)
    print(f"Serving on http://{ip}")

    with open("picolock.html", "r") as f:
        html = f.read()

    while True:
        conn, addr = s.accept()
        try:
            request = conn.recv(2048).decode("utf-8", "ignore")
            if not request:
                continue

            if "POST /unlock" in request:
                unlock()
                send_response(conn, "200 OK", "text/plain", "ok")
            else:
                send_response(conn, "200 OK", "text/html", html)

        except Exception as e:
            print("Error:", e)
        finally:
            conn.close()

ip = connect_wifi()
serve(ip)
