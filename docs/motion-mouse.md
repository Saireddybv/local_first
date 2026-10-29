# iPhone motion mouse

The Remote tool now offers three mouse modes:

- **Finger touchpad:** the original drag-to-move and tap-to-click behaviour.
- **Move phone · experimental:** use short screen-up sideways or forward/back strokes. The app uses gravity-free acceleration, stationary calibration, a noise dead zone and damped velocity. It does not measure absolute desk position; long constant-speed slides and changes in how you hold the phone can be inaccurate. This is not an optical mouse replacement.
- **Tilt phone:** tilt away from your calibrated resting angle to move; return to that angle to stop. Larger tilts move faster. This is a velocity control, not physical displacement tracking.

## Start

1. Use the [HTTPS setup](https.md), open the HTTPS address in Safari and pair normally.
2. On the laptop, allow Media, keyboard, touchpad & slides.
3. In Remote, select Move phone or Tilt phone, then tap Enable motion mouse.
4. Allow Safari's Motion & Orientation permission. Hold the phone still until the page says ready.
5. Move the phone in short strokes, or tilt it in tilt mode. Adjust Speed as needed (default 2×, range 0.5–8×).
6. Tap the large pad to left-click. Hold the pad to temporarily pause movement while repositioning the phone. Releasing a long hold does not click. The existing right-click and scroll buttons still work.

Use Calibrate / centre if the cursor drifts or your resting angle changes. Rotation between portrait and landscape triggers calibration again. Stop motion or select Finger touchpad to return to ordinary controls.

Motion stops when the page is hidden, the connection fails, desktop permission is removed, or usable sensor events stop arriving. It does not restart automatically; tap Enable again. A browser without sensors can still use the finger touchpad. Denied permissions show an error; Safari settings may need to be changed before retrying.

Move phone now has twice the previous base gain and defaults to 2× speed, giving four times the previous default movement before limits apply. Pointer delivery is attempted every 16 ms instead of 50 ms; actual delivery depends on sensor events and network response time. Only one move request is in flight at once, with bounded pending movement. Noise filtering and stationary stopping remain enabled.

Sensor samples are processed on the phone. Only relative pointer commands go to the laptop, through the existing paired, permission-checked endpoint. No accelerometer or orientation history is stored.

## Validation

Run `node --test tests/motion-mouse.test.cjs` for synthetic sensor and UI lifecycle coverage. These tests never operate the Windows desktop. Also run the Python server tests.

Before relying on this mode, test a physical iPhone: portrait/landscape, move and tilt directions, still-phone drift, sensitivity, calibration, permission denial, tap versus long hold, Safari backgrounding, Wi-Fi loss and laptop permission removal. Actual motion quality has not been measured on a physical iPhone.

API references: [DeviceMotionEvent permission](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent/requestPermission_static), [DeviceOrientationEvent permission](https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent/requestPermission_static). Sensor permissions require a user gesture and a secure context on supporting browsers.
