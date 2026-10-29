import pytest
from fastapi.testclient import TestClient
from local_first.server import create_app

@pytest.fixture
def clients(tmp_path):
    app = create_app(tmp_path)
    laptop = TestClient(app)
    phone = TestClient(app)
    laptop.get('/admin/' + app.state.admin)
    return app, laptop, phone

def paired(clients):
    app, laptop, phone = clients
    r = phone.post('/api/pair', json={'invite': app.state.invite})
    assert r.status_code == 200
    pending = laptop.get('/api/status').json()['pending'][0]
    assert pending['code'] == r.json()['code']
    assert laptop.post('/api/approve/' + pending['id']).status_code == 200
    return app, laptop, phone

def test_pairing_and_revocation(clients):
    app, laptop, phone = clients
    assert phone.get('/api/files').status_code == 401
    assert phone.post('/api/pair', json={'invite':'wrong'}).status_code == 403
    paired(clients)
    assert phone.get('/api/files').status_code == 200
    assert phone.post('/api/stop').status_code == 403
    assert phone.post('/api/clipboard/read').status_code == 403
    assert laptop.post('/api/stop').status_code == 200
    assert phone.get('/api/files').status_code == 401
    assert phone.post('/api/pair', json={'invite': app.state.invite}).status_code == 403

def test_file_roundtrip_and_duplicate(clients):
    app, laptop, phone = paired(clients)
    assert phone.put('/api/files/photo.jpg', content=b'example').status_code == 200
    assert laptop.get('/api/files/photo.jpg').content == b'example'
    assert laptop.put('/api/files/photo.jpg', content=b'changed').status_code == 409
    assert (app.state.folder/'photo.jpg').read_bytes() == b'example'
    assert not list(app.state.folder.glob('*.part'))
    assert phone.put('/api/files/bad:name', content=b'x').status_code == 400
    assert phone.put('/api/files/.hidden', content=b'x').status_code == 400

def test_pad_conflicts(clients):
    app, laptop, phone = paired(clients)
    assert laptop.post('/api/pad', json={'text':'hello','version':0}).status_code == 200
    assert phone.post('/api/pad', json={'text':'lost','version':0}).status_code == 409
    assert phone.get('/api/status').json()['pad']['text'] == 'hello'

def test_cross_origin_and_websocket(clients):
    app, laptop, phone = paired(clients)
    assert laptop.post('/api/stop', headers={'Origin':'http://evil.example'}).status_code == 403
    from starlette.websockets import WebSocketDisconnect
    with pytest.raises(WebSocketDisconnect):
        with TestClient(app).websocket_connect('/ws/audio', headers={'Origin':'http://testserver'}):
            pass

def test_assets_are_local(clients):
    app,laptop,phone=clients
    for path in ('/','/static/app.js','/static/style.css'):
        response=phone.get(path)
        assert response.status_code==200
        assert 'cdn.' not in response.text
    assert laptop.get('/api/qr').headers['content-type'].startswith('image/svg+xml')

def test_remove_file(clients):
    app, laptop, phone = paired(clients)
    assert phone.put('/api/files/note.txt', content=b'hi').status_code == 200
    assert phone.delete('/api/files/note.txt').status_code == 200
    assert not (app.state.folder / 'note.txt').exists()
    assert phone.delete('/api/files/note.txt').status_code == 404
    assert phone.delete('/api/files/..%5Cx').status_code in (400, 404)
    laptop.post('/api/stop')
    assert phone.delete('/api/files/note.txt').status_code == 401
