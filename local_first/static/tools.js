/* Tool controllers use the existing same-origin pairing cookie. */
(() => {
  let localAdmin = false, permissions = {}, activeNote = null, noteDirty = false;
  let viewing = false, viewEpoch = 0, screenUrl = null, screenshotUrl = null;
  let mediaStream = null, peer = null, signaling = null, mediaEpoch = 0, candidates = [];
  let loadedNotes = false, polling = false, lastActions = '';
  const message = (id, text) => { $(id).textContent = text; };
  const bind = (id, fn, status) => {
    $(id).onclick = async () => { try { await fn(); } catch (e) { message(status || 'error', e.message); } };
  };
  function haltScreen(clear = true) {
    viewing = false; viewEpoch++;
    if (clear) { $('screenImage').hidden = true; $('screenImage').removeAttribute('src'); }
    if (screenUrl) { URL.revokeObjectURL(screenUrl); screenUrl = null; }
    if (screenshotUrl && clear) { URL.revokeObjectURL(screenshotUrl); screenshotUrl = null; $('saveScreen').hidden = true; }
    message('screenStatus', 'Screen viewer stopped');
  }
  function stopMedia(text = 'Camera and microphone stopped') {
    mediaEpoch++;
    if (signaling) { signaling.onclose = null; signaling.close(); signaling = null; }
    if (peer) { peer.close(); peer = null; }
    if (mediaStream) { mediaStream.getTracks().forEach(t => t.stop()); mediaStream = null; }
    $('cameraVideo').srcObject = null;
    candidates = [];
    message('cameraStatus', text);
  }
  function disconnected() {
    $('permissionsPanel').hidden = true;
    haltScreen(); stopMedia();
    stopMotion('Motion stopped: laptop disconnected. Enable it again after reconnecting.');
    permissions = {};
  }
  window.addEventListener('local-first-disconnected', disconnected);
  window.addEventListener('pagehide', disconnected);
  window.addEventListener('local-first-status', e => {
    localAdmin = e.detail.admin;
    $('permissionsPanel').hidden = !localAdmin;
    $('actionEditor').hidden = !localAdmin;
    $('receiveControls').hidden = !localAdmin;
  });
  async function refreshTools() {
    if (!paired || polling) return;
    polling = true;
    try {
      const state = await api('tools');
      permissions = state.permissions;
      if (!permissions.control && (motionActive || motionPending)) stopMotion('Motion stopped: desktop control permission was removed.');
      for (const name of ['control', 'screen', 'actions', 'camera']) $('allow-' + name).checked = permissions[name];
      message('permissionStatus', Object.entries(permissions).filter(([, value]) => value).map(([name]) => name).join(', ') || 'Desktop access is off');
      if (!permissions.screen && viewing) haltScreen();
      if (!permissions.camera && (signaling || mediaStream)) stopMedia();
      if (!loadedNotes) { await loadNotes(); loadedNotes = true; }
      const stats = await api('system');
      $('systemStats').replaceChildren();
      const values = [['CPU', stats.cpu.toFixed(0) + '%'], ['Memory', stats.memory.toFixed(0) + '%'],
        ['Disk free', (stats.disk_free / 1024 ** 3).toFixed(1) + ' GiB'], ['Uptime', Math.floor(stats.uptime / 3600) + 'h'],
        ['Battery', stats.battery ? stats.battery.percent + '% ' + (stats.battery.plugged ? '· charging' : '') : 'No battery']];
      for (const [label, value] of values) { const el = document.createElement('div'); el.className = 'stat'; const strong = document.createElement('strong'); strong.textContent = value; el.append(label, strong); $('systemStats').append(el); }
      if (localAdmin || permissions.actions) await refreshActions();
      else { $('actionList').replaceChildren(); $('taskList').replaceChildren(); lastActions = ''; }
    } catch (e) { message('systemStats', 'Status unavailable: ' + e.message); }
    finally { polling = false; }
  }
  setInterval(refreshTools, 2000);
  for (const name of ['control', 'screen', 'actions', 'camera']) {
    $('allow-' + name).onchange = async () => {
      try {
        const next = Object.fromEntries(['control', 'screen', 'actions', 'camera'].map(key => [key, $('allow-' + key).checked]));
        permissions = await api('permissions', next);
        if (!permissions.control) stopMotion('Motion stopped: desktop controls are off.');
        await refreshTools();
      } catch (e) { message('permissionStatus', e.message); }
    };
  }
  document.querySelectorAll('[data-key]').forEach(button => {
    button.onclick = async () => {
      const target = button.dataset.key.startsWith('slide-') ? 'slideStatus' : 'remoteStatus';
      try { await api('control/key', {key: button.dataset.key}); message(target, 'Sent: ' + button.textContent); }
      catch (e) { message(target, e.message); }
    };
  });
  async function pointer(action, dx = 0, dy = 0) { await api('control/pointer', {action, dx, dy}); }
  document.querySelectorAll('[data-pointer]').forEach(b => b.onclick = () => pointer(b.dataset.pointer).catch(e => message('remoteStatus', e.message)));
  document.querySelectorAll('[data-scroll]').forEach(b => b.onclick = () => pointer('scroll', 0, Number(b.dataset.scroll)).catch(e => message('remoteStatus', e.message)));
  bind('sendKeys', async () => { await api('control/text', {text: $('remoteText').value}); $('remoteText').value = ''; message('remoteStatus', 'Text sent'); }, 'remoteStatus');
  let touch = null, dx = 0, dy = 0, moving = false;
  let motionActive = false, motionPending = false, motionEpoch = 0, motionEngine = null;
  let motionWatchdog = null, motionStarted = 0, lastSensor = 0, pauseUntil = 0, calibrationStarted = 0;
  function stopMotion(reason = 'Motion mouse stopped. Tap Enable motion mouse to restart.') {
    motionEpoch++; motionActive = motionPending = false;
    window.removeEventListener('devicemotion', motionSample);
    window.removeEventListener('deviceorientation', orientationSample);
    clearInterval(motionWatchdog); motionWatchdog = null; motionEngine = null;
    dx = dy = 0; touch = null;
    $('startMotion').disabled = false; $('stopMotion').disabled = true; $('calibrateMotion').disabled = true;
    $('touchpad').classList.remove('motion-active');
    message('motionStatus', reason);
  }
  function calibrateMotion() {
    if (!motionEngine) return;
    motionEngine.reset(); dx = dy = 0; calibrationStarted = performance.now();
    message('motionStatus', 'Hold the phone still for a moment to calibrate.');
  }
  function sensorSample(x, y) {
    if (!motionActive || !paired || !permissions.control || document.hidden) return;
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    const now = performance.now(); lastSensor = now;
    // Tapping should not kick the pointer. Holding the pad acts as a clutch.
    if (touch || now < pauseUntil) { motionEngine.pause(); return; }
    const wasReady = !!motionEngine.bias;
    const angle = window.screen?.orientation?.angle ?? window.orientation ?? 0;
    const delta = motionEngine.sample(x, y, now, angle, Number($('motionSensitivity').value));
    if (!delta) return;
    if (!delta.ready) {
      if (wasReady) calibrationStarted = now;
      message('motionStatus', 'Hold still to calibrate. Movement starts when ready.');
      dx = dy = 0;
      return;
    }
    if (!wasReady) message('motionStatus', motionEngine.mode === 'move' ?
      'Motion mouse ready: move the phone in short strokes. Tap the pad to click.' :
      'Tilt mouse ready: tilt to move; return to centre to stop. Tap the pad to click.');
    // Bound queued movement when the network is slower than the sensors.
    dx = Math.max(-300, Math.min(300, dx + delta.dx));
    dy = Math.max(-300, Math.min(300, dy + delta.dy));
  }
  function motionSample(event) { sensorSample(event.acceleration?.x, event.acceleration?.y); }
  function orientationSample(event) { sensorSample(event.gamma, event.beta); }
  bind('startMotion', async () => {
    stopMotion();
    const mode = $('pointerMode').value;
    if (mode === 'touch') return;
    if (!paired || !permissions.control) throw Error('Connect and enable desktop controls on the laptop first.');
    if (!window.isSecureContext) throw Error('iPhone sensors need HTTPS. Open the HTTPS pairing link; see docs/https.md in the project.');
    const Sensor = mode === 'move' ? window.DeviceMotionEvent : window.DeviceOrientationEvent;
    if (!Sensor) throw Error('This browser has no motion sensor support. Use Finger touchpad instead.');
    const epoch = motionEpoch;
    motionPending = true; $('startMotion').disabled = true; $('stopMotion').disabled = false;
    message('motionStatus', 'Allow motion access in the browser prompt.');
    try {
      // Keep this call in the original button gesture: iOS requires activation.
      if (typeof Sensor.requestPermission === 'function') {
        const result = await Sensor.requestPermission();
        if (epoch !== motionEpoch) return;
        if (result !== 'granted') throw Error('Motion permission denied. Allow Motion & Orientation access in Safari, then try again, or use Finger touchpad.');
      }
      if (epoch !== motionEpoch || !paired || !permissions.control || document.hidden) {
        if (epoch === motionEpoch) stopMotion();
        return;
      }
      motionPending = false; motionActive = true; motionEngine = new MotionMouse(mode);
      motionStarted = performance.now(); lastSensor = 0; pauseUntil = 0;
      $('calibrateMotion').disabled = false; $('touchpad').classList.add('motion-active');
      calibrateMotion();
      window.addEventListener(mode === 'move' ? 'devicemotion' : 'deviceorientation', mode === 'move' ? motionSample : orientationSample);
      motionWatchdog = setInterval(() => {
        const now = performance.now();
        if ((!lastSensor && now - motionStarted > 4000) || (lastSensor && now - lastSensor > 2000)) {
          stopMotion('No usable sensor readings. Check motion permission, or try Tilt phone / Finger touchpad.');
        } else if (!motionEngine.bias && now - calibrationStarted > 10000) {
          stopMotion('Calibration needs a still phone. Rest it briefly, then enable motion again.');
        }
      }, 250);
    } catch (e) {
      if (epoch === motionEpoch) stopMotion(e.message);
    }
  }, 'motionStatus');
  bind('stopMotion', () => stopMotion());
  bind('calibrateMotion', calibrateMotion);
  $('pointerMode').onchange = () => {
    stopMotion(); const mode = $('pointerMode').value;
    $('motionOptions').hidden = mode === 'touch';
    $('touchpadLabel').textContent = mode === 'touch' ? 'Drag here to move the pointer' : 'Tap here to click';
    $('touchpadHint').textContent = mode === 'touch' ? 'Tap to click · buttons below for scrolling' : 'Hold here to pause movement while repositioning your phone';
    $('touchpad').setAttribute('aria-label', mode === 'touch' ? 'Touchpad. Drag to move; tap to click.' : 'Motion mouse click pad. Tap to click; hold to pause sensor movement.');
    $('motionHelp').textContent = mode === 'tilt' ?
      'Hold the phone comfortably and calibrate. Tilt sideways or forward/back to move; return to the calibrated angle to stop.' :
      'Hold the phone screen-up and make short sideways or forward/back movements. Sensors can drift; this is not precise desk-position tracking.';
  };
  $('motionSensitivity').oninput = () => { $('motionSensitivityValue').textContent = Number($('motionSensitivity').value).toFixed(1) + '×'; };
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopMotion('Motion paused because the page was hidden. Enable it again to resume.'); });
  $('touchpad').onpointerdown = e => {
    if (touch) return;
    touch = {id: e.pointerId, x: e.clientX, y: e.clientY, distance: 0, started: performance.now()};
    $('touchpad').setPointerCapture(e.pointerId);
    if ($('pointerMode').value !== 'touch') { dx = dy = 0; motionEngine?.pause(); }
  };
  $('touchpad').onpointermove = e => {
    if (!touch || e.pointerId !== touch.id) return;
    const x = e.clientX - touch.x, y = e.clientY - touch.y;
    touch.distance += Math.abs(x) + Math.abs(y);
    if ($('pointerMode').value === 'touch') { dx += x * 1.8; dy += y * 1.8; }
    touch.x = e.clientX; touch.y = e.clientY;
  };
  $('touchpad').onpointerup = e => {
    if (!touch || e.pointerId !== touch.id) return;
    const isMotion = $('pointerMode').value !== 'touch';
    if (touch.distance < 5 && (!isMotion || performance.now() - touch.started < 350)) pointer('left').catch(err => message('remoteStatus', err.message));
    touch = null;
    if (isMotion) { motionEngine?.pause(); pauseUntil = performance.now() + 180; dx = dy = 0; }
  };
  $('touchpad').onpointercancel = () => { touch = null; dx = dy = 0; motionEngine?.pause(); pauseUntil = performance.now() + 180; };
  setInterval(async () => {
    if (moving || (!dx && !dy)) return;
    if (!paired || !permissions.control) { dx = dy = 0; return; }
    const x = Math.max(-500, Math.min(500, Math.round(dx))), y = Math.max(-500, Math.min(500, Math.round(dy)));
    // Carry fractional pixels forward; slow sensor movement should not vanish.
    dx -= x; dy -= y;
    if (!x && !y) return;
    moving = true;
    try { await pointer('move', x, y); } catch (e) {
      dx = dy = 0; stopMotion('Motion stopped: ' + e.message); message('remoteStatus', e.message);
    } finally { moving = false; }
  }, 16);
  async function fetchScreen(preview) {
    const r = await fetch('/api/screen?preview=' + preview);
    if (!r.ok) { let text = await r.text(); try { text = JSON.parse(text).detail; } catch {} throw Error(text); }
    return URL.createObjectURL(await r.blob());
  }
  bind('captureScreen', async () => {
    haltScreen(); const epoch = viewEpoch;
    const url = await fetchScreen(false);
    if (epoch !== viewEpoch) { URL.revokeObjectURL(url); return; }
    screenshotUrl = url; $('screenImage').src = url; $('screenImage').hidden = false;
    $('saveScreen').href = url; $('saveScreen').hidden = false; message('screenStatus', 'Screenshot captured · download to keep it');
  }, 'screenStatus');
  bind('viewScreen', async () => {
    haltScreen(); viewing = true; const epoch = viewEpoch;
    async function frame() {
      if (!viewing || epoch !== viewEpoch) return;
      try {
        const url = await fetchScreen(true);
        if (!viewing || epoch !== viewEpoch) { URL.revokeObjectURL(url); return; }
        if (screenUrl) URL.revokeObjectURL(screenUrl);
        screenUrl = url; $('screenImage').src = url; $('screenImage').hidden = false;
        message('screenStatus', 'Screen viewer connected');
        setTimeout(frame, 500);
      } catch (e) { haltScreen(); message('screenStatus', e.message); }
    }
    await frame();
  }, 'screenStatus');
  bind('stopScreen', () => haltScreen());
  function selectNote(note) {
    if (noteDirty && !confirm('Discard the unsaved note draft?')) return;
    activeNote = note; noteDirty = false;
    $('noteTitle').value = note?.title || ''; $('noteText').value = note?.text || '';
    $('deleteNote').disabled = !note;
    message('noteStatus', note ? 'Saved note loaded' : 'New note');
  }
  async function loadNotes() {
    const notes = await api('notes'); $('noteList').replaceChildren();
    for (const note of notes) { const button = document.createElement('button'); button.textContent = note.title; button.onclick = () => selectNote(note); $('noteList').append(button); }
  }
  $('noteTitle').oninput = $('noteText').oninput = () => { noteDirty = true; message('noteStatus', 'Unsaved changes'); };
  bind('newNote', () => selectNote(null));
  bind('reloadNotes', loadNotes, 'noteStatus');
  bind('saveNote', async () => {
    const title = $('noteTitle').value.trim() || 'Untitled note', text = $('noteText').value;
    const saved = await api('notes', {id: activeNote?.id || null, title, text, version: activeNote?.version || 0});
    activeNote = saved; noteDirty = $('noteText').value !== text || ($('noteTitle').value.trim() || 'Untitled note') !== title;
    $('deleteNote').disabled = false; message('noteStatus', noteDirty ? 'Earlier draft saved; newer edits are unsaved' : 'Saved on laptop'); await loadNotes();
  }, 'noteStatus');
  bind('deleteNote', async () => {
    if (!activeNote || !confirm('Delete this saved note from both devices?')) return;
    await api('notes/' + activeNote.id + '?version=' + activeNote.version, null, 'DELETE');
    noteDirty = false; selectNote(null); await loadNotes();
  }, 'noteStatus');
  async function refreshActions() {
    const data = await api('actions'), serialized = JSON.stringify(data);
    if (serialized === lastActions) return;
    lastActions = serialized;
    $('actionList').replaceChildren();
    for (const action of data.actions) {
      const row = document.createElement('div'); row.className = 'action-row';
      const run = document.createElement('button'); run.textContent = action.label;
      run.onclick = async () => { try { run.disabled = true; await api('actions/' + action.id + '/run', {}); await refreshActions(); } catch (e) { message('actionStatus', e.message); } finally { run.disabled = false; } };
      row.append(run);
      if (localAdmin) { const remove = document.createElement('button'); remove.textContent = 'Remove'; remove.className = 'danger'; remove.onclick = async () => { if (!confirm('Remove this action button?')) return; try { await api('actions/' + action.id, null, 'DELETE'); await refreshActions(); } catch (e) { message('actionStatus', e.message); } }; row.append(remove); const code = document.createElement('code'); code.textContent = JSON.stringify(action.argv); row.append(code); }
      $('actionList').append(row);
    }
    $('taskList').replaceChildren();
    for (const task of data.runs) {
      const card = document.createElement('details'); card.open = task.state === 'running';
      const title = document.createElement('summary'); title.textContent = task.label + ' · ' + task.state + (task.exit_code === null ? '' : ' · exit ' + task.exit_code);
      const output = document.createElement('pre'); output.textContent = task.output || 'No output yet'; card.append(title, output);
      if (task.state === 'running') { const stop = document.createElement('button'); stop.textContent = 'Stop task'; stop.onclick = () => api('tasks/' + task.id + '/stop', {}).then(refreshActions).catch(e => message('actionStatus', e.message)); card.append(stop); }
      $('taskList').append(card);
    }
  }
  bind('addAction', async () => {
    const argv = [$('actionExe').value.trim(), ...($('actionArgs').value ? $('actionArgs').value.split('\n') : [])];
    await api('actions', {label: $('actionLabel').value.trim(), argv});
    message('actionStatus', 'Action saved on laptop'); await refreshActions();
  }, 'actionStatus');
  bind('lockWindows', async () => { if (confirm('Lock the Windows laptop now?')) { await api('control/lock', {}); message('actionStatus', 'Lock requested'); } }, 'actionStatus');
  async function startMedia(role) {
    stopMedia(); const epoch = mediaEpoch;
    if (!permissions.camera) throw Error('Enable phone camera / microphone on the laptop first.');
    if (role === 'send') {
      if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) throw Error('Phone capture needs trusted HTTPS. Restart with --cert and --key, trust the local certificate, then scan the HTTPS QR code.');
      const mode = $('cameraMode').value;
      const stream = await navigator.mediaDevices.getUserMedia({video: mode === 'audio' ? false : {facingMode: 'environment', width: {ideal: 1280}, frameRate: {ideal: 15}}, audio: mode !== 'video'});
      if (epoch !== mediaEpoch) { stream.getTracks().forEach(t => t.stop()); return; }
      mediaStream = stream; $('cameraVideo').srcObject = stream; $('cameraVideo').muted = true;
    }
    peer = new RTCPeerConnection({iceServers: []}); const currentPeer = peer;
    if (mediaStream) mediaStream.getTracks().forEach(track => { currentPeer.addTrack(track, mediaStream); track.onended = () => stopMedia('Phone capture ended'); });
    currentPeer.ontrack = e => { $('cameraVideo').srcObject = e.streams[0]; $('cameraVideo').muted = true; message('cameraStatus', 'Feed received · tap Play received sound to hear the microphone'); };
    signaling = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/camera/' + role); const ws = signaling;
    const send = value => { if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(value)); };
    currentPeer.onicecandidate = e => { if (e.candidate) send({type: 'candidate', candidate: e.candidate.toJSON()}); };
    currentPeer.onconnectionstatechange = () => {
      if (epoch !== mediaEpoch) return;
      if (['failed', 'disconnected'].includes(currentPeer.connectionState)) stopMedia('Feed disconnected. Check local Wi-Fi, then reconnect both sides.');
      else if (currentPeer.connectionState === 'connected') message('cameraStatus', role === 'send' ? 'Phone feed connected' : 'Phone feed connected · tap Play received sound to hear audio');
    };
    ws.onclose = () => { if (epoch === mediaEpoch) stopMedia('Receiver disconnected or permission was removed. Reconnect both sides.'); };
    ws.onerror = () => { if (epoch === mediaEpoch) stopMedia('Camera connection failed. Check pairing and HTTPS.'); };
    let messages = Promise.resolve();
    ws.onmessage = e => { messages = messages.then(async () => {
      if (epoch !== mediaEpoch) return;
      const msg = JSON.parse(e.data);
      if (msg.type === 'waiting') message('cameraStatus', 'Waiting for ' + (role === 'send' ? 'laptop receiver' : 'phone feed'));
      if (msg.type === 'left') { stopMedia('Other device stopped the feed. Reconnect both sides to resume.'); return; }
      if (msg.type === 'ready' && role === 'send') { await currentPeer.setLocalDescription(await currentPeer.createOffer()); send({type: 'offer', sdp: currentPeer.localDescription.sdp}); }
      if (msg.type === 'offer' || msg.type === 'answer') {
        await currentPeer.setRemoteDescription({type: msg.type, sdp: msg.sdp});
        for (const candidate of candidates) await currentPeer.addIceCandidate(candidate);
        candidates = [];
        if (msg.type === 'offer') { await currentPeer.setLocalDescription(await currentPeer.createAnswer()); send({type: 'answer', sdp: currentPeer.localDescription.sdp}); }
      }
      if (msg.type === 'candidate') { if (currentPeer.remoteDescription) await currentPeer.addIceCandidate(msg.candidate); else candidates.push(msg.candidate); }
    }).catch(e => stopMedia(e.message)); };
  }
  bind('sendCamera', async () => { try { await startMedia('send'); } catch (e) { stopMedia(e.message); } }, 'cameraStatus');
  bind('receiveCamera', () => startMedia('receive'), 'cameraStatus');
  bind('stopCamera', () => stopMedia());
  bind('playCamera', async () => { $('cameraVideo').muted = false; await $('cameraVideo').play(); }, 'cameraStatus');
})();
