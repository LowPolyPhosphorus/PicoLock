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

## Hardware

| Part | |
|------|-|
| [Raspberry Pi Pico WH](https://www.amazon.com/Raspberry-Pi-RP-PICO-WH-Pico-WH/dp/B0C58X9Q77) | Microcontroller with WiFi and pre-soldered headers |
| [5V relay module](https://www.amazon.com/HiLetgo-Channel-optocoupler-Support-Trigger/dp/B00LW15A4W) | Switches the 12V lock circuit |
| [12V solenoid lock](https://www.amazon.com/uxcell-Electromagnetic-Solenoid-Assembly-Electirc/dp/B07TMWY94C) | The lock itself |
| [12V DC power supply](https://www.amazon.com/GuanTing-Universal-adapters-Converter-Transformer/dp/B086T1N5R4) | Powers the lock |
| Jumper wires | |
| USB cable | Powers the Pico |

## Docs

- [Setup](docs/setup.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Wiring diagram](docs/PicoLock.drawio.svg)

> License: MPL-2.0
