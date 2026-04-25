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
            return ip, wlan
        time.sleep(1)
    raise RuntimeError("WiFi connection failed")

def setup_mdns(hostname):
    try:
        import network
        sta = network.WLAN(network.STA_IF)
        sta.config(dhcp_hostname=hostname)
        print("mDNS hostname:", hostname + ".local")
    except Exception as e:
        print("mDNS setup failed:", e)

def get_mdns_hostname():
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        return cfg.get("mdnsHostname", "picolock")
    except:
        return "picolock"

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

def serve(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(3)
    print("Serving on http://" + ip)
    hostname = get_mdns_hostname()
    print("Also try: http://" + hostname + ".local")
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
            elif "GET /manifest.json" in request:
                with open("manifest.json", "r") as f:
                    data = f.read()
                conn.send(("HTTP/1.1 200 OK\r\nContent-Type: application/manifest+json\r\nContent-Length: "+str(len(data))+"\r\nConnection: close\r\n\r\n").encode())
                conn.send(data.encode())
            elif "GET /info" in request:
                hostname = get_mdns_hostname()
                info = json.dumps({"ip": ip, "hostname": hostname + ".local"})
                send_json(conn, info)
            elif "POST /save" in request:
                body = get_body(conn, request)
                if body:
                    with open(CONFIG_FILE, "w") as f:
                        f.write(body)
                    setup_mdns(get_mdns_hostname())
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
setup_mdns(get_mdns_hostname())
serve(ip)
