# Setup

## What you need

- [Raspberry Pi Pico WH](https://www.amazon.com/Raspberry-Pi-RP-PICO-WH-Pico-WH/dp/B0C58X9Q77)
- [5V single channel relay module](https://www.amazon.com/HiLetgo-Channel-optocoupler-Support-Trigger/dp/B00LW15A4W)
- [12V electromagnetic solenoid lock](https://www.amazon.com/uxcell-Electromagnetic-Solenoid-Assembly-Electirc/dp/B07TMWY94C)
- [12V DC power supply](https://www.amazon.com/GuanTing-Universal-adapters-Converter-Transformer/dp/B086T1N5R4)
- Jumper wires
- USB cable
- A computer with [Thonny](https://thonny.org) installed

---

## 1. Flash MicroPython onto the Pico

1. Hold the **BOOTSEL** button on the Pico and plug it into your computer over USB
2. It mounts as a drive called `RPI-RP2`
3. Open Thonny and go to **Tools → Options → Interpreter**
4. Select **MicroPython (Raspberry Pi Pico)** and click **Install or update MicroPython**
5. Wait for it to finish, then unplug and replug the Pico without holding BOOTSEL

---

## 2. Set up your secrets file

Copy `secrets.example.py` to a new file called `secrets.py` and fill in your details:

```python
WIFI_SSID = "your_wifi_name"
WIFI_PASSWORD = "your_wifi_password"
UNLOCK_DURATION = 2  # seconds the relay stays open
```

`secrets.py` is gitignored and never gets pushed to GitHub. It only lives on the Pico.

---

## 3. Flash the firmware files

Open each of these files in Thonny and save them to the Pico via **File → Save as → Raspberry Pi Pico**:

- `firmware/main.py`
- `firmware/picolock.html`
- `firmware/manifest.json`
- `secrets.py`

All four files go flat on the Pico root, not inside any folder.

> In Thonny's file open dialog, change the filter from "Python files" to "All files" to see the .html and .json files.

---

## 4. Wire everything up

See the [wiring diagram](https://github.com/LowPolyPhosphorus/PicoLock/blob/main/docs/PicoLock.drawio.svg) for the full reference.

| Pico WH | Relay module |
|---------|-------------|
| VBUS (pin 40) | VCC |
| GND (pin 38) | GND |
| GP15 (pin 20) | IN |

| Relay module | Lock + PSU |
|-------------|-----------|
| COM | 12V PSU + |
| NO | Lock red wire |
| — | Lock black wire → 12V PSU − |

The 12V circuit is fully isolated from the Pico. The relay is the only bridge between the two sides.

---

## 5. Boot and connect

Plug the Pico in over USB. In Thonny's shell you should see:

```
Connecting to WiFi...
Connected: 192.168.x.x
Serving on http://192.168.x.x
```

Open that IP in a browser on the same WiFi network. You will be taken through a short onboarding flow to set your master password and unlock method. After that the lock screen loads on every visit.

---

## 6. Reserve a static IP (recommended)

Your router may assign the Pico a different IP after a reboot. Log into your router and reserve the Pico's IP address so it never changes. Bookmark the IP on your phone once reserved.

---

## 7. Add to home screen (optional)

On iPhone open the IP in Safari → Share → **Add to Home Screen**.
On Android open the IP in Chrome → menu → **Add to Home Screen**.

This gives you a one tap shortcut on your home screen that opens the lock interface directly.
