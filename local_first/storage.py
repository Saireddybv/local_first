"""Persistent shared notes with optimistic concurrency, outside the file share."""
import sqlite3
import time
import uuid
from contextlib import contextmanager


class Notes:
    def __init__(self, path):
        self.path = path
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY, title TEXT, text TEXT, version INTEGER, updated REAL)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def list(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM notes ORDER BY updated DESC")]

    def save(self, note_id, title, text, version):
        with self.connect() as db:
            if note_id is None:
                note_id = uuid.uuid4().hex
                db.execute("INSERT INTO notes VALUES (?, ?, ?, 1, ?)", (note_id, title, text, time.time()))
            else:
                result = db.execute("UPDATE notes SET title=?, text=?, version=version+1, updated=? WHERE id=? AND version=?",
                                    (title, text, time.time(), note_id, version))
                if result.rowcount != 1:
                    raise ValueError("Note changed or was deleted. Copy your draft, then reload notes.")
            return dict(db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone())

    def delete(self, note_id, version):
        with self.connect() as db:
            result = db.execute("DELETE FROM notes WHERE id=? AND version=?", (note_id, version))
            if result.rowcount != 1:
                raise ValueError("Note changed or was deleted; reload before deleting.")
