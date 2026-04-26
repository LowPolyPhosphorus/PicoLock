# Troubleshooting

## The page won't load

**Check the IP is correct.** Open Thonny, run main.py and look at the shell output for `Serving on http://...`. Use that exact IP in your browser.

**Make sure you're using http not https.** Browsers sometimes auto-upgrade to HTTPS which will fail on the Pico. Type `http://` explicitly.

**Make sure your device is on the same WiFi network as the Pico.** Mobile data will not work. Turn off mobile data and connect to WiFi first.

**The IP may have changed.** If you haven't reserved a static IP on your router, the Pico may have been assigned a new address after a reboot. Check the Thonny shell for the current IP and reserve it in your router settings to prevent this.

---

## The relay fires but the lock doesn't move

**Check all screw terminal connections.** Unscrew each terminal on the relay output side, push the wire all the way in, and retighten firmly. Loose strands not fully inserted are the most common cause.

**Verify the wiring order.** COM goes to 12V PSU positive. NO goes to the lock red wire. Lock black wire goes directly to PSU negative. Nothing connects to NC.

**Test the lock directly.** Disconnect the relay and touch the lock wires directly to the PSU to confirm the lock itself works.

**Check your PSU is actually outputting 12V.** Measure across the PSU terminals with a multimeter.

---

## The relay doesn't fire at all

**Test GP15 manually in Thonny shell:**

```python
from machine import Pin
r = Pin(15, Pin.OUT)
r.high()
```

If the relay LED lights up but contacts don't close, the relay module is faulty. Try another one from the pack.

If the LED doesn't light up at all, check the dupont wire from GP15 to the relay IN pin is fully seated on both ends.

---

## The lock screen keeps showing onboarding after a reload

The config was not saved to the Pico properly. Go through onboarding, complete all steps, and wait for the lock screen to appear before reloading. If it still happens, check the Thonny shell for any `Error:` lines printed during the POST /save request.

---

## Settings changes don't save

Make sure you tap **Save and close** and wait for the screen to return to the lock screen before reloading. The save is confirmed when the lock screen appears. If unlock duration changes aren't taking effect, make sure main.py on the Pico is the latest version which reads duration from config on each unlock rather than at boot.

---

## Wrong password lockout

Enter your master password on the lockout screen to restore access. If you have forgotten your master password, use the **Wipe and reset** button in settings while you still have access, or manually delete `config.json` from the Pico using Thonny's file browser (View → Files).

---

## The Pico won't connect to WiFi

**Double check credentials in secrets.py.** SSID and password are case sensitive.

**Make sure the Pico is in range.** The Pico WH has a small antenna and range can be limited.

**The Pico only supports 2.4GHz WiFi.** If your router uses the same SSID for both bands, the Pico should connect automatically on 2.4GHz, but if it fails try connecting your phone to the 2.4GHz band to confirm it is available.

---

## The page loads but unlocking does nothing

The fetch to `/unlock` may be failing silently. Open your browser dev tools (F12) → Console and look for any errors when you tap unlock. Also check the Thonny shell for any `Error:` output at the time you tap unlock.
