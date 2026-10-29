const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {MotionMouse} = require('../local_first/static/motion-mouse.js');

function calibrated(mode = 'move', x = 0, y = 0) {
  const mouse = new MotionMouse(mode);
  for (let t = 0; t <= 700; t += 50) mouse.sample(x, y, t);
  assert.ok(mouse.bias);
  return mouse;
}

test('still phone and small noise do not drift after calibration', () => {
  const mouse = calibrated('move', .04, -.02);
  for (let t = 750; t < 5000; t += 20) {
    const result = mouse.sample(.05, -.03, t);
    assert.equal(result.dx, 0); assert.equal(result.dy, 0);
  }
});
test('translation moves right, reverses left, and settles without endless drift', () => {
  const mouse = calibrated();
  let right = 0, left = 0;
  for (let t = 720; t <= 1000; t += 20) right += mouse.sample(1, 0, t).dx;
  for (let t = 1020; t <= 1500; t += 20) left += mouse.sample(-1, 0, t).dx;
  assert.ok(right > 0); assert.ok(left < 0);
  for (let t = 1520; t <= 2000; t += 20) mouse.sample(0, 0, t);
  assert.equal(mouse.sample(0, 0, 2020).dx, 0);
});
test('speed above the old maximum helps short strokes without amplifying stationary noise', () => {
  const normal = calibrated(), fast = calibrated();
  let normalDistance = 0, fastDistance = 0;
  for (let t = 720; t <= 1000; t += 20) {
    normalDistance += normal.sample(.5, 0, t, 0, 2).dx;
    fastDistance += fast.sample(.5, 0, t, 0, 8).dx;
  }
  assert.ok(normalDistance > 0);
  assert.ok(Math.abs(fastDistance / normalDistance - 4) < 1e-9);
  for (let t = 1020; t <= 2000; t += 20) fast.sample(.05, -.05, t, 0, 8);
  assert.equal(fast.sample(.05, -.05, 2020, 0, 8).dx, 0);
  assert.equal(fast.sample(.05, -.05, 2040, 0, 8).dy, 0);
});
test('tilt is centred, proportional and sensitivity changes gain', () => {
  const mouse = calibrated('tilt', 5, 10);
  assert.equal(mouse.sample(5.5, 10.5, 720).dx, 0);
  const first = mouse.sample(15, 10, 740, 0, 1);
  const second = mouse.sample(15, 10, 760, 0, 2);
  assert.ok(first.dx > 0); assert.equal(second.dx, first.dx * 2);
  assert.equal(mouse.sample(5, 10, 780).dx, 0);
});
test('missing sensors, long gaps and orientation changes cannot cause jumps', () => {
  const mouse = calibrated();
  assert.equal(mouse.sample(null, 0, 720), null);
  assert.equal(mouse.sample(NaN, 0, 720), null);
  assert.equal(mouse.sample(3, 0, 10000).dx, 0);
  const rotated = mouse.sample(1, 0, 10020, 90);
  assert.equal(rotated.dx, 0); assert.equal(rotated.ready, false);
  assert.equal(mouse.bias, null);
});
test('shaking during calibration restarts calibration; spikes are bounded', () => {
  const mouse = new MotionMouse();
  mouse.sample(0, 0, 0); mouse.sample(10, 0, 50);
  assert.equal(mouse.bias, null); assert.equal(mouse.count, 0);
  const stable = calibrated();
  for (let t = 720; t < 2000; t += 20) assert.ok(Math.abs(stable.sample(1000, -1000, t, 0, 8).dx) <= 120);
});
test('holding click pad clears velocity and first sample after release cannot jump', () => {
  const mouse = calibrated();
  mouse.sample(2, 0, 720); mouse.pause();
  assert.equal(mouse.sample(0, 0, 740).dx, 0);
});

// Run the real UI controller with synthetic sensors and a fake transport.
// This never captures a screen, moves the real Windows pointer, or needs a phone.
function controller(permission = async () => 'granted') {
  let now = 0;
  const elements = new Map(), listeners = new Map(), intervals = [], calls = [];
  const element = id => {
    if (!elements.has(id)) elements.set(id, {value: '', hidden: false, disabled: false, textContent: '',
      classList: {add() {}, remove() {}}, setAttribute() {}, setPointerCapture() {},
      replaceChildren() {}, append() {}, removeAttribute() {}});
    return elements.get(id);
  };
  element('pointerMode').value = 'move'; element('motionSensitivity').value = '1';
  const window = {isSecureContext: true, screen: {orientation: {angle: 0}},
    DeviceMotionEvent: {requestPermission: permission},
    DeviceOrientationEvent: {requestPermission: permission},
    addEventListener(name, fn) { if (!listeners.has(name)) listeners.set(name, new Set()); listeners.get(name).add(fn); },
    removeEventListener(name, fn) { listeners.get(name)?.delete(fn); }};
  const document = {hidden: false, querySelectorAll: () => [], createElement: () => element('generated'),
    addEventListener: window.addEventListener.bind(window)};
  const sandbox = {window, document, MotionMouse, paired: true, $: element, performance: {now: () => now},
    setInterval(fn, ms) { const timer = {fn, ms, active: true}; intervals.push(timer); return timer; },
    clearInterval(timer) { if (timer) timer.active = false; },
    api: async (path, body) => {
      calls.push({path, body});
      if (path === 'tools') return {permissions: {control: true}};
      if (path === 'notes') return [];
      if (path === 'system') return {cpu: 0, memory: 0, disk_free: 1, uptime: 0, battery: null};
      return {};
    }, URL: {revokeObjectURL() {}}, confirm: () => false};
  vm.runInNewContext(fs.readFileSync(require.resolve('../local_first/static/tools.js'), 'utf8'), sandbox);
  return {element, calls, window, document, intervals,
    async ready() { await intervals.find(t => t.ms === 2000).fn(); },
    time(value) { now = value; },
    emit(name, event) { for (const fn of listeners.get(name) || []) fn(event); },
    count(name) { return listeners.get(name)?.size || 0; }};
}
test('UI accepts sensor movement, keeps tap-to-click, and stops on disconnect', async () => {
  const ui = controller(); await ui.ready(); await ui.element('startMotion').onclick();
  assert.equal(ui.count('devicemotion'), 1);
  for (let t = 0; t <= 700; t += 50) { ui.time(t); ui.emit('devicemotion', {acceleration: {x: 0, y: 0}}); }
  for (let t = 720; t <= 900; t += 20) { ui.time(t); ui.emit('devicemotion', {acceleration: {x: 1, y: 0}}); }
  await ui.intervals.find(t => t.ms === 16).fn();
  assert.ok(ui.calls.some(c => c.path === 'control/pointer' && c.body.action === 'move' && c.body.dx > 0));
  ui.element('touchpad').onpointerdown({pointerId: 1, clientX: 5, clientY: 5});
  ui.time(1000); ui.element('touchpad').onpointerup({pointerId: 1});
  assert.equal(ui.calls.filter(c => c.body?.action === 'left').length, 1);
  ui.emit('local-first-disconnected', {});
  assert.equal(ui.count('devicemotion'), 0);
  const count = ui.calls.length;
  ui.time(1100); ui.emit('devicemotion', {acceleration: {x: 5, y: 0}});
  await ui.intervals.find(t => t.ms === 16).fn();
  assert.equal(ui.calls.length, count);
});
test('denied permission and absent readings produce recoverable errors', async () => {
  const denied = controller(async () => 'denied'); await denied.ready();
  await denied.element('startMotion').onclick();
  assert.match(denied.element('motionStatus').textContent, /denied/);
  assert.equal(denied.count('devicemotion'), 0);
  assert.equal(denied.element('startMotion').disabled, false);
  const silent = controller(); await silent.ready(); await silent.element('startMotion').onclick();
  silent.time(5000); silent.intervals.find(t => t.ms === 250).fn();
  assert.match(silent.element('motionStatus').textContent, /No usable sensor/);
  assert.equal(silent.count('devicemotion'), 0);
});
test('stopping while permission prompt is open prevents a delayed start', async () => {
  let grant;
  const ui = controller(() => new Promise(resolve => { grant = resolve; })); await ui.ready();
  const starting = ui.element('startMotion').onclick();
  await ui.element('stopMotion').onclick(); grant('granted'); await starting;
  assert.equal(ui.count('devicemotion'), 0);
  assert.equal(ui.element('stopMotion').disabled, true);
});
test('HTTP is rejected and hiding the page detaches active sensors', async () => {
  const ui = controller(); await ui.ready(); ui.window.isSecureContext = false;
  await ui.element('startMotion').onclick();
  assert.match(ui.element('motionStatus').textContent, /HTTPS/);
  ui.window.isSecureContext = true; await ui.element('startMotion').onclick();
  ui.document.hidden = true; ui.emit('visibilitychange', {});
  assert.equal(ui.count('devicemotion'), 0);
});
test('finger mode still supports dragging and tapping without sensor permission', async () => {
  const ui = controller(async () => { throw Error('Must not request sensors'); }); await ui.ready();
  ui.element('pointerMode').value = 'touch'; ui.element('pointerMode').onchange();
  const pad = ui.element('touchpad');
  pad.onpointerdown({pointerId: 1, clientX: 0, clientY: 0});
  pad.onpointermove({pointerId: 1, clientX: 20, clientY: 10});
  pad.onpointerup({pointerId: 1});
  await ui.intervals.find(t => t.ms === 16).fn();
  assert.ok(ui.calls.some(c => c.body?.action === 'move' && c.body.dx === 36));
  assert.equal(ui.calls.filter(c => c.body?.action === 'left').length, 0);
  pad.onpointerdown({pointerId: 2, clientX: 0, clientY: 0}); pad.onpointerup({pointerId: 2});
  assert.equal(ui.calls.filter(c => c.body?.action === 'left').length, 1);
});
