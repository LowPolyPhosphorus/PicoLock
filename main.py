import network
import socket
import time
from machine import Pin
import secrets

# relay on GP15, active high
RELAY_PIN = 15
UNLOCK_DURATION = 2  # seconds

relay = Pin(RELAY_PIN, Pin.OUT)
relay.low()

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    print("Connecting to WiFi...")
    for _ in range(20):
        if wlan.isconnected():
            print("Connected:", wlan.ifconfig()[0])
            return wlan.ifconfig()[0]
        time.sleep(1)
    raise RuntimeError("WiFi connection failed")

def unlock():
    relay.high()
    time.sleep(UNLOCK_DURATION)
    relay.low()

def page(message=""):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>PicoLock</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #111; color: #fff; }}
        h1 {{ margin-bottom: 24px; }}
        input {{ padding: 10px; font-size: 16px; border-radius: 6px; border: none; margin-bottom: 12px; width: 220px; }}
        button {{ padding: 10px 24px; font-size: 16px; border-radius: 6px; border: none; background: #4CAF50; color: white; cursor: pointer; width: 220px; }}
        button:active {{ background: #388E3C; }}
        .msg {{ margin-top: 16px; font-size: 14px; color: {'#4CAF50' if message == 'Unlocked' else '#f44336'}; }}
    </style>
</head>
<body>
    <h1>PicoLock</h1>
    <form method="POST" action="/unlock">
        <input type="password" name="password" placeholder="Password" autofocus><br>
        <button type="submit">Unlock</button>
    </form>
    {'<p class="msg">' + message + '</p>' if message else ''}
</body>
</html>"""

def parse_body(body):
    for part in body.split("&"):
        if part.startswith("password="):
            return part[len("password="):]
    return ""

def serve(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print(f"Serving on http://{ip}")

    while True:
        conn, _ = s.accept()
        try:
            request = conn.recv(1024).decode()
            if not request:
                conn.close()
                continue

            if "POST /unlock" in request:
                body = request.split("\r\n\r\n", 1)[-1]
                password = parse_body(body)
                if password == secrets.UNLOCK_PASSWORD:
                    unlock()
                    message = "Unlocked"
                else:
                    message = "Wrong password"
            else:
                message = ""

            response = page(message)
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.send(response)
        except Exception as e:
            print("Error:", e)
        finally:
            conn.close()

ip = connect_wifi()
serve(ip)
