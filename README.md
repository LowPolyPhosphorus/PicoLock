# PicoLock

PicoLock is a WiFi-enabled smart lock system built on the Raspberry Pi Pico WH. It uses a 12V electromagnetic solenoid controlled through a password-protected web interface hosted directly on the Pico. No apps, no cloud, no subscription.

## Features

- PIN, pattern, or password unlock
- Full onboarding flow with master password
- Settings protected by master password
- Lockout after configurable failed attempts, cleared by master password
- Unlock history log
- Configurable unlock duration
- Accent color, font, and background customization
- Animated unlock feedback
- Session timeout on settings
- PWA home screen shortcut support
- Serves directly from the Pico over local WiFi, no internet required
<img width="1904" height="870" alt="image" src="https://github.com/user-attachments/assets/19061722-4bb6-42cf-8be7-0e2dce00cb65" />

## Hardware

| Part | |
|------|-|
| [Raspberry Pi Pico WH](https://www.amazon.com/Raspberry-Pi-RP-PICO-WH-Pico-WH/dp/B0C58X9Q77) | Microcontroller with WiFi and pre-soldered headers |
| [5V relay module](https://www.amazon.com/HiLetgo-Channel-optocoupler-Support-Trigger/dp/B00LW15A4W) | Switches the 12V lock circuit |
| [12V solenoid lock](https://www.amazon.com/uxcell-Electromagnetic-Solenoid-Assembly-Electirc/dp/B07TMWY94C) (decapitated) | The lock itself |
| [12V DC power supply](https://www.amazon.com/GuanTing-Universal-adapters-Converter-Transformer/dp/B086T1N5R4) | Powers the lock |
| Jumper wires | |
| USB cable | Powers the Pico |

## Docs

- [Setup](docs/setup.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Wiring diagram](docs/PicoLock.drawio.svg)

# Gallery
<img width="459" height="818" alt="image" src="https://github.com/user-attachments/assets/7321a687-3d76-41c0-9b28-5d3c3431bd73" />
<img width="413" height="652" alt="image" src="https://github.com/user-attachments/assets/e998d406-7969-4f66-adac-11d9215fe274" />
<img width="407" height="848" alt="image" src="https://github.com/user-attachments/assets/47d56bd5-46bb-4c5d-897e-0da3105440e0" />
<img width="425" height="614" alt="image" src="https://github.com/user-attachments/assets/4dae65c9-587b-4b0d-a0c6-c58071cc1fbf" />
<img width="425" height="439" alt="image" src="https://github.com/user-attachments/assets/08fa2c4d-a396-4807-ab24-489c7b2dea51" />


> License: MPL-2.0
