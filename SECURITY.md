# Security

Use only trusted private networks. HTTP and WebSocket traffic is unencrypted; pairing is access control, not protection against network interception. Do not forward this port to the internet.

The laptop controller requires a random secret and a loopback connection. Phones require an expiring pairing request explicitly approved by the laptop. Sessions and invitations are random and memory-only; cookies are HttpOnly and SameSite Strict. Cross-origin requests are rejected. Stop sharing revokes sessions and rotates invitations. There is no global keyboard listener or automatic clipboard collection.

Every approved device can read/write the shared pad and upload, download and remove files in the configured folder. Uploads are bounded to 10 GiB, filenames are validated, partial files are cleaned up, and existing files are not overwritten. There is no total disk quota; monitor available space. Pairing is limited to 20 outstanding requests. Run as an ordinary user.

Report vulnerabilities privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Do not file a public issue first, and do not include secrets or personal data.

## Extended tool permissions

Desktop control, screen capture, actions and phone-camera signaling each require a laptop-only switch. Controls send keys/text to whichever Windows app has focus; do not enable them for people you do not trust. Screen access can reveal all monitors. Captures are held in memory; only a user download saves them. Windows may block input into elevated apps or its secure desktop.

Notes and action definitions are stored under `.local-first` inside the configured folder; HTTP file routes reject hidden paths. Notes persist in SQLite; action definitions persist in JSON. Local users with filesystem access can read them. Remote devices cannot define commands. A saved command can perform whatever its arguments request, so the laptop owner must review it before enabling actions. Task output is shared with approved devices only when actions are enabled. Do not add commands that print credentials.

HTTPS is optional for the original tools and required by Safari for phone capture. The certificate helper creates a personal CA and a 90-day server certificate; it does not install trust roots. Keep private keys outside the shared files folder and source control. Trust only the public CA certificate on your own devices, remove it when no longer needed, and regenerate/retrust when its validity or the laptop IP changes. WebRTC signaling is authenticated; its media is encrypted by WebRTC and has no cloud relay.
