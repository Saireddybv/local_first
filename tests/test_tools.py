import ipaddress
import sys
import time
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from local_first.server import create_app
from test_server import clients, paired


def enable(laptop, **permissions):
    response = laptop.post('/api/permissions', json=permissions)
    assert response.status_code == 200


def test_controls_require_laptop_switch_and_validate(clients):
    app, laptop, phone = paired(clients)
    desktop = app.state.tools.desktop = Mock()
    assert phone.post('/api/permissions', json={'control': True}).status_code == 403
    assert phone.post('/api/control/key', json={'key': 'play'}).status_code == 403
    desktop.key.assert_not_called()
    enable(laptop, control=True)
    assert phone.post('/api/control/key', json={'key': 'play'}).status_code == 200
    desktop.key.assert_called_once_with(0xB3)
    assert phone.post('/api/control/key', json={'key': 'execute'}).status_code == 422
    assert phone.post('/api/control/pointer', json={'action':'move','dx':501}).status_code == 422
    assert phone.post('/api/control/text', json={'text':'hello 😀'}).status_code == 200
    desktop.text.assert_called_once_with('hello 😀')
    assert laptop.post('/api/stop').status_code == 200
    assert not app.state.tools.permissions.control
    assert phone.post('/api/control/key', json={'key':'play'}).status_code == 401


def test_screen_gate_and_failure(clients):
    app, laptop, phone = paired(clients)
    app.state.tools.desktop = Mock()
    app.state.tools.desktop.screenshot.return_value = b'png-bytes'
    assert phone.get('/api/screen').status_code == 403
    enable(laptop, screen=True)
    response = phone.get('/api/screen')
    assert response.content == b'png-bytes'
    assert 'attachment' in response.headers['content-disposition']
    app.state.tools.desktop.screenshot.side_effect = OSError('Desktop unavailable')
    assert phone.get('/api/screen').status_code == 503
    enable(laptop)
    assert phone.get('/api/screen?preview=true').status_code == 403


def test_persistent_notes_and_conflicts(clients):
    app, laptop, phone = paired(clients)
    note = phone.post('/api/notes', json={'title':'Shopping','text':'Milk'}).json()
    changed = laptop.post('/api/notes', json={**note, 'text':'Milk and eggs'})
    assert changed.status_code == 200
    assert phone.post('/api/notes', json={**note, 'text':'Old draft'}).status_code == 409
    assert phone.delete('/api/notes/' + note['id'] + '?version=1').status_code == 409
    restarted = create_app(app.state.folder)
    other = TestClient(restarted)
    other.get('/admin/' + restarted.state.admin)
    saved = other.get('/api/notes').json()[0]
    assert saved['text'] == 'Milk and eggs'
    assert other.get('/api/files/.local-first/notes.sqlite3').status_code != 200
    assert other.delete('/api/notes/' + note['id'] + '?version=2').status_code == 200
    assert other.get('/api/notes').json() == []


def test_actions_allowlist_runs_and_output(clients):
    app, laptop, phone = paired(clients)
    command = {'label':'Test task','argv':[sys.executable,'-u','-c','print("finished test")']}
    assert phone.post('/api/actions', json=command).status_code == 403
    action = laptop.post('/api/actions', json=command).json()
    assert phone.post('/api/actions/' + action['id'] + '/run').status_code == 403
    enable(laptop, actions=True)
    assert phone.post('/api/actions/missing/run').status_code == 404
    run = phone.post('/api/actions/' + action['id'] + '/run').json()
    deadline = time.monotonic()+5
    while time.monotonic() < deadline:
        snapshot = phone.get('/api/actions').json()
        if snapshot['runs'][0]['state'] != 'running':
            break
        time.sleep(.02)
    assert snapshot['runs'][0]['state'] == 'completed'
    assert snapshot['runs'][0]['exit_code'] == 0
    assert 'finished test' in snapshot['runs'][0]['output']
    assert 'argv' not in snapshot['actions'][0]
    assert laptop.delete('/api/actions/' + action['id']).status_code == 200
    assert laptop.get('/api/actions').json()['actions'] == []


def test_stop_terminates_started_tasks(clients):
    app, laptop, phone = paired(clients)
    action = laptop.post('/api/actions', json={'label':'Sleeper','argv':[sys.executable,'-c','import time; time.sleep(60)']}).json()
    enable(laptop, actions=True)
    run = phone.post('/api/actions/' + action['id'] + '/run').json()
    process = app.state.tools.actions.processes[run['id']]
    try:
        assert laptop.post('/api/stop').status_code == 200
        process.wait(timeout=4)
        assert process.poll() is not None
        assert app.state.tools.actions.runs[run['id']]['state'] == 'stopped'
    finally:
        if process.poll() is None:
            process.kill()


def test_camera_signaling_roles_and_revocation(clients):
    app, laptop, phone = paired(clients)
    headers = {'Origin':'http://testserver'}
    with pytest.raises(WebSocketDisconnect):
        with phone.websocket_connect('/ws/camera/send', headers=headers):
            pass
    enable(laptop, camera=True)
    with pytest.raises(WebSocketDisconnect):
        with phone.websocket_connect('/ws/camera/receive', headers=headers):
            pass
    with laptop.websocket_connect('/ws/camera/receive', headers=headers) as receiver:
        assert receiver.receive_json()['type'] == 'waiting'
        with phone.websocket_connect('/ws/camera/send', headers=headers) as sender:
            assert sender.receive_json()['type'] == 'waiting'
            assert sender.receive_json()['type'] == 'ready'
            assert receiver.receive_json()['type'] == 'ready'
            sender.send_json({'type':'offer','sdp':'test-offer'})
            assert receiver.receive_json()['sdp'] == 'test-offer'
            receiver.send_json({'type':'answer','sdp':'test-answer'})
            assert sender.receive_json()['sdp'] == 'test-answer'
        assert receiver.receive_json()['type'] == 'left'
    assert not app.state.tools.peers


def test_status_and_unpaired_denial(clients):
    app, laptop, phone = clients
    for route in ['/api/notes','/api/system','/api/actions','/api/tools','/api/screen']:
        assert phone.get(route).status_code == 401
    paired(clients)
    data = phone.get('/api/system').json()
    assert 0 <= data['memory'] <= 100
    assert data['disk_free'] > 0


def test_tls_certificate_scope_and_no_overwrite(tmp_path):
    cryptography = pytest.importorskip('cryptography')
    from cryptography import x509
    from local_first.tls import generate
    generate('192.168.1.42', tmp_path)
    certificate = x509.load_pem_x509_certificate((tmp_path/'server.pem').read_bytes())
    names = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert ipaddress.ip_address('192.168.1.42') in names.get_values_for_type(x509.IPAddress)
    assert ipaddress.ip_address('127.0.0.1') in names.get_values_for_type(x509.IPAddress)
    with pytest.raises(ValueError, match='already exist'):
        generate('192.168.1.42', tmp_path)
