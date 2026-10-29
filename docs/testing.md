# Release acceptance

Automated tests exercise pairing, authorization, revocation, duplicate uploads, traversal rejection, file round trips and pad conflicts. They do not prove Windows hardware capture or iPhone playback.

Before calling this release ready, test on Windows and a physical iPhone:

- Setup once; disable internet while retaining local Wi-Fi. Start and scan QR. Compare/approve codes. Confirm no external asset requests in browser Network tools.
- Attempt access from an unpaired second browser; confirm file/text/audio access is denied.
- Upload a photo/document from iPhone, verify bytes on Windows, and download a Windows file to Safari Files. Test duplicate names, upload cancellation, a large file and loss of Wi-Fi.
- Type on both devices, test conflict preservation, explicit Windows clipboard actions and Safari manual copying.
- Play Windows sound, tap Listen, verify stereo audio and Stop audio. Disconnect/reconnect Wi-Fi and verify understandable status. Check capture-device failures.
- Stop sharing: phone access and audio end; new pairing uses a fresh QR. Close launcher: port closes and active transfers end.
- Check narrow phone layout, keyboard navigation and error text.

Record actual outcomes and device/OS versions in your PR. No physical iPhone acceptance result is claimed by the automated suite.

## Extended acceptance checks

Automated tests mock the Windows adapter; they do not press keys, capture private screens or lock your workstation.

- With desktop switches off, confirm phone controls/screens/actions/camera fail clearly. Only the laptop can enable switches. Stop sharing resets them all.
- Enable controls, focus a disposable text editor, and test Unicode text, arrow keys, pointer movement, clicks and scroll. Try media buttons with a music app and slide buttons with a disposable presentation. Check that elevated/locked desktops fail understandably.
- Enable screen access; capture/download a screenshot, then start/stop the viewer. Test multi-monitor capture and permission removal while viewing.
- Save notes from each device, restart the server, and verify persistence. Edit the same note simultaneously and confirm a conflict preserves the draft. Delete a test note.
- Define a harmless command, such as Python printing a message, and run it from the phone. Verify output, exit codes, failure states and Stop. Try a sleeping task and verify Stop sharing terminates it. Never use destructive commands for testing.
- Compare laptop metrics with Task Manager. Check systems with and without batteries.
- Generate certificates into a temporary folder; trust the public CA only on test devices. Start HTTPS, open the laptop receiver, and send video-only, audio-only and combined phone feeds. Verify sound requires a user tap, camera permission denial is explained, and both Stop and pairing revocation turn off the phone capture indicator.
- Use a second isolated browser to verify it cannot claim the laptop receiver role or edit actions.

Current automated result: 14 passing tests on Windows/Python 3.11. Physical iPhone input, media, screenshot and WebRTC acceptance must still be performed on the intended devices.

Browser verification on the local test server: desktop and 390-pixel layouts rendered; horizontal overflow was fixed and rechecked (390px viewport / 390px document). A note was saved through the UI and loaded after reload. A disabled media control returned the expected laptop-permission message. The browser error log was empty. This used a temporary data folder and did not operate the real desktop or a physical iPhone.

## Motion mouse

Run `node --test tests/motion-mouse.test.cjs` (Node 22+) for 12 sensor and UI tests covering calibration, drift damping, direction, permission denial, missing sensors, cancelled prompts, disconnect, backgrounding and touchpad regression. Follow [physical iPhone acceptance](motion-mouse.md) for hardware validation.
Motion browser check: at a 390px viewport, the document remained 390px wide. Synthetic acceleration events calibrated and produced rightward pointer commands against a mock desktop; Stop detached motion. No JavaScript errors were reported. Physical iPhone motion quality remains unverified.
