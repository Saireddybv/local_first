/* Sensor mapping is independent of transport so it can be tested without a phone. */
(function (root) {
  const clamp = (value, limit) => Math.max(-limit, Math.min(limit, value));
  const deadzone = (value, threshold) => Math.sign(value) * Math.max(0, Math.abs(value) - threshold);
  class MotionMouse {
    constructor(mode = 'move') { this.mode = mode; this.reset(); }
    reset() {
      this.last = null; this.start = null; this.count = 0; this.sum = [0, 0];
      this.min = [Infinity, Infinity]; this.max = [-Infinity, -Infinity];
      this.bias = null; this.velocity = [0, 0]; this.quiet = 0; this.angle = null;
    }
    pause() { this.last = null; this.velocity = [0, 0]; this.quiet = 0; }
    sample(x, y, timestamp, angle = 0, sensitivity = 1) {
      if (![x, y, timestamp, angle, sensitivity].every(Number.isFinite)) return null;
      // Device axes -> current screen axes. Positive output y points down.
      angle = ((angle % 360) + 360) % 360;
      if (this.angle !== null && this.angle !== angle) this.reset();
      this.angle = angle;
      const radians = angle * Math.PI / 180;
      const values = [x * Math.cos(radians) - y * Math.sin(radians),
        -(x * Math.sin(radians) + y * Math.cos(radians))];
      if (!this.bias) {
        if (this.start === null) this.start = timestamp;
        values.forEach((v, i) => {
          this.sum[i] += v; this.min[i] = Math.min(this.min[i], v); this.max[i] = Math.max(this.max[i], v);
        });
        this.count++;
        const tolerance = this.mode === 'move' ? .45 : 3;
        if (this.max.some((v, i) => v - this.min[i] > tolerance)) {
          this.reset(); this.angle = angle;
          return {dx: 0, dy: 0, ready: false};
        }
        if (timestamp - this.start >= 650 && this.count >= 8) {
          this.bias = this.sum.map(v => v / this.count);
          this.last = timestamp;
        }
        return {dx: 0, dy: 0, ready: !!this.bias};
      }
      const elapsed = this.last === null ? 0 : (timestamp - this.last) / 1000;
      this.last = timestamp;
      // Never integrate time spent suspended, or jump when events resume.
      if (elapsed <= 0 || elapsed > .2) {
        this.velocity = [0, 0]; this.quiet = 0;
        return {dx: 0, dy: 0, ready: true};
      }
      const dt = Math.min(elapsed, .05);
      const centered = values.map((v, i) => v - this.bias[i]);
      let delta;
      if (this.mode === 'tilt') {
        // Tilt is a velocity joystick: level stops; larger tilt moves faster.
        delta = centered.map(v => clamp(deadzone(v, 2), 25) * 22 * dt);
      } else {
        // Short translation gestures only. Damping bounds accelerometer drift;
        // this deliberately does not claim optical-mouse position tracking.
        const acceleration = centered.map(v => deadzone(clamp(v, 4), .12));
        this.quiet = acceleration.every(v => v === 0) ? this.quiet + dt : 0;
        this.velocity = this.velocity.map((v, i) => this.quiet >= .12 ? 0 :
          clamp(v * Math.exp(-5 * dt) + acceleration[i] * dt, .65));
        delta = this.velocity.map(v => v * dt * 4000);
      }
      const gain = Math.max(.5, Math.min(8, sensitivity));
      return {dx: clamp(delta[0] * gain, 120), dy: clamp(delta[1] * gain, 120), ready: true};
    }
  }
  root.MotionMouse = MotionMouse;
  if (typeof module !== 'undefined' && module.exports) module.exports = {MotionMouse};
})(typeof window !== 'undefined' ? window : globalThis);
