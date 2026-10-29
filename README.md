# Local First

**Your Windows laptop and your phone, working together over your own Wi-Fi. No cloud, no account, no app to install.**

Open one local address on your phone and you can move files both ways, share text, or hear your laptop's audio through the phone. Optional tools turn the phone into a remote control for the laptop. Everything stays on your local network, and nothing needs internet access once it's installed.

[![Tests](https://github.com/Saireddybv/local_first/actions/workflows/tests.yml/badge.svg)](https://github.com/Saireddybv/local_first/actions/workflows/tests.yml)
![Platform](https://img.shields.io/badge/laptop-Windows%2010%20%7C%2011-blue)
![Phone](https://img.shields.io/badge/phone-any%20modern%20browser-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## What it does

| Tool | What you can do |
| --- | --- |
| **Files** | Send photos and documents from phone to laptop and back. Works up to 10 GiB per file. |
| **Clip** | Shared text pad between both screens, with buttons to read/write the Windows clipboard. |
| **Audio** | Hear all of your laptop's sound on your phone. Handy when the laptop speakers are broken. |
| **Notes** | Short notes saved on the laptop and visible from both devices. |
| **Remote, slides and media** *(opt-in)* | Type, move the mouse, scroll, control music or advance presentation slides from your phone. |
| **Screen** *(opt-in)* | Take a screenshot of the laptop or watch its screen from the phone. |
| **Actions** *(opt-in)* | Run commands you've saved yourself on the laptop with one tap. |
| **System** | Check laptop battery, CPU and memory from another room. |
| **Camera / mic** *(opt-in, HTTPS)* | Use the phone's camera or microphone as a live feed on the laptop. |

*Opt-in* tools stay off until you switch them on **on the laptop**. **Stop sharing** turns them all off again.

## What you need

- A Windows 10 or 11 laptop
- [Python 3.11 or newer](https://www.python.org/downloads/windows/) (keep **"py launcher"** ticked in the installer)
- A phone (iPhone or Android) on the **same Wi-Fi** as the laptop. Guest networks often block devices from seeing each other.

## Quick start

1. **Download** this project: click the green **Code** button, choose **Download ZIP** and unzip it. Or run:
   ```bash
   git clone https://github.com/Saireddybv/local_first.git
   ```
2. **Double-click `Start Local First.bat`.** The first run installs everything it needs, which takes about a minute. Keep this window open while you use the app. If Windows Firewall asks, allow Python on **Private networks**.
3. A page opens on the laptop with a **QR code**. Scan it with your phone camera and tap **Request pairing**.
4. Check that the **six-digit code** matches on both screens, then click **Approve** on the laptop.
5. Pick **Files**, **Clip** or **Audio** on your phone.

To stop, close the launcher window or press **Ctrl+C**. You'll need to pair again next time.

## Everyday use

**Files** are saved in `D:\Local First Files` if you have a D: drive, otherwise in `~\Local First Files`. Approved devices can see every ordinary file in that folder. Downloading doesn't delete anything. If a file with the same name already exists, the upload is rejected rather than overwriting it.

**Clip** shares only the text you type in its pad. The laptop's buttons explicitly read or write the Windows clipboard. Phone browsers may block clipboard access over HTTP, so on the phone you may need to select the text and use Copy/Paste from the menu. If both devices edit at once, you get a conflict warning and your unsaved draft is kept. Pad text lives in memory and isn't saved.

**Audio** streams whatever Windows is playing. Tap **Start listening**, keep the browser in the foreground and don't mute Windows or the app that's playing.

**Stop sharing** (on the laptop) signs out every phone, clears the pad, creates a fresh pairing QR, ends audio and camera, turns off all opt-in tools and stops tasks started through Local First. Saved files, notes and actions are kept.

## Options

Run these from a terminal in the project folder, or add them to `Start Local First.bat`:

| Option | What it does |
| --- | --- |
| `--folder "D:\Shared"` | Shares a different folder |
| `--port 8001` | Uses a different port if 8000 is busy |
| `--address 192.168.1.20` | Sets the laptop IP for the QR code, if it picked the wrong network adapter |
| `--cert ... --key ...` | Enables HTTPS, which the phone camera/mic needs. See [HTTPS setup](docs/https.md). |

```powershell
.venv\Scripts\python -m local_first --folder "D:\Shared" --port 8001
```

## Troubleshooting

| Problem | Fix |
| --- | --- |
| **Phone can't open the QR link** | In Windows Wi-Fi settings, set the network to **Private**. Allow Python through the firewall. Make sure both devices are on the same non-guest Wi-Fi. |
| **QR code shows the wrong IP** | Start with `--address <your laptop's Wi-Fi IP>`. You can find it with `ipconfig`. |
| **"Python was not found"** | Install Python from python.org with the **py launcher** option, then run the `.bat` again. |
| **Port already in use** | Start with `--port 8001`. |
| **Audio is silent** | Check that Windows isn't muted and that sound is playing through the default output device. |
| **Audio stops when the phone locks** | Keep the browser in the foreground and turn off Auto-Lock while listening. |
| **Camera/mic says it needs a secure page** | This is expected. Safari requires HTTPS for the camera. Follow [docs/https.md](docs/https.md). |
| **Something broke during setup** | Delete the `.venv` folder and run `Setup.bat` again. |

## Security in one paragraph

Use Local First only on Wi-Fi you trust, and never forward its port to the internet. Every phone has to be approved on the laptop with a matching code. Sessions are random, kept in memory only and end when you press Stop sharing or close the app. Plain HTTP traffic isn't encrypted, so anyone already on your network could observe it. Opt-in tools such as remote control and screen viewing are powerful, so turn them on only for your own devices. Full details are in [SECURITY.md](SECURITY.md).

## Development

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -c requirements-lock.txt -e ".[dev,tls]"
.venv\Scripts\python -m pytest
node --test tests/motion-mouse.test.cjs
.venv\Scripts\python -m local_first
```

| Path | Contents |
| --- | --- |
| `local_first/` | App: server, pairing, tools, audio capture and the browser UI in `static/` |
| `tests/` | Pairing, permissions, transfers, notes, controls, tasks and signaling tests |
| `docs/` | [Architecture](docs/architecture.md), [manual acceptance checks](docs/testing.md), [HTTPS](docs/https.md), [motion mouse](docs/motion-mouse.md) |

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Automated tests cover the server logic. Real iPhone playback and desktop control still need the manual checks in `docs/testing.md`.

## Background

Local First grew out of separate single-purpose tools. The Audio tool is based on [Broken Speaker](https://github.com/Saireddybv/broken_speaker), which is still available on its own if audio is all you need. File transfer and Clip replace their earlier standalone servers. The old global keyboard capture from those prototypes was deliberately not carried over.

## License

[MIT](LICENSE)
