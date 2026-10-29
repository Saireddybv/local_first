# Phone camera and microphone setup

Safari requires a secure context for camera/microphone capture. A plain LAN HTTP address cannot request these permissions. See [MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).

## Generate local certificates

Run Setup.bat to install the TLS helper, then from the project folder:

```powershell
.venv\Scripts\python -m local_first.tls --address 192.168.1.20 --out .certs
```

Replace the example address with your laptop's actual LAN IP shown in the launcher. This creates a personal CA and a server certificate valid for 90 days, including the chosen IP, 127.0.0.1 and localhost. It does not change Windows or iPhone trust settings. Reserve your laptop's IP in the router if you want the address to remain stable.

Keep `.certs` outside your shared files folder. Never share `ca-key.pem` or `server-key.pem`, and do not commit them. Only `Local-First-CA.cer` is for installing on your own devices.

## Device trust

The owner must install and trust the generated public CA on their own laptop and phone before using this local HTTPS server. The app does not perform that system change. Verify the certificate came from your own Local First instance before trusting it. On Windows, use the certificate installation wizard for the current user and the Trusted Root Certification Authorities store.

To move the public certificate to your phone, start Local First normally over HTTP, pair, upload only `Local-First-CA.cer` using Files, and download/open it on iPhone. Follow iOS's certificate profile installation flow and Apple's [manual certificate trust instructions](https://support.apple.com/en-gb/102390). Installation alone does not enable SSL trust. The exact prompts can vary with iOS version.

A trusted CA can authenticate websites on that device. Keep its private key private, and remove the trust root/profile when you stop using it. Do not dismiss certificate errors as a substitute for setting up trust.

## Start HTTPS and connect

Stop the previous server, then run:

```powershell
.venv\Scripts\python -m local_first --address 192.168.1.20 --cert .certs/server.pem --key .certs/server-key.pem
```

The laptop controller opens at HTTPS loopback. Scan the new HTTPS QR code and pair again; HTTP and HTTPS have separate browser sessions. If a certificate warning remains, verify trust, IP and certificate dates before proceeding.

1. On the laptop, enable Phone camera & microphone receiver.
2. In Camera / mic, click Open laptop receiver.
3. On the phone, select Camera only, Microphone only or Camera + microphone, then Start phone feed. Grant the browser permission.
4. The laptop displays the feed. Click Play received sound to hear the microphone. Use headphones to avoid feedback.
5. Stop camera / microphone on either side to end the feed. Stop sharing or turning off the laptop permission also ends it. Keep both browser pages open.

WebRTC is configured with no internet STUN/TURN service. Both devices must be reachable on the same local network; isolated guest networks may fail. If disconnected, reopen the receiver and restart the phone feed. See [WebRTC stream handling](https://webrtc.org/getting-started/remote-streams).

This is a browser video/audio receiver, not a virtual Windows webcam or microphone driver for Zoom, Teams or other apps. Installing such a driver is outside this implementation.

If the IP changes or the certificate expires, generate a new set into a new private directory, install its new public CA on your devices, and point the launcher to the new certificate/key. Remove the old trust root. The helper refuses to overwrite existing key files.
