"""Laptop-defined commands and bounded, in-memory task output. Never uses a shell."""
import json
import os
import subprocess
import threading
import time
import uuid
from pathlib import Path


class Actions:
    def __init__(self, state_dir):
        self.path = state_dir / "actions.json"
        self.lock = threading.RLock()
        self.definitions = json.loads(self.path.read_text()) if self.path.exists() else {}
        self.runs = {}
        self.processes = {}

    def save(self, label, argv):
        executable = Path(argv[0])
        if not executable.is_absolute() or not executable.is_file():
            raise ValueError("Use the full path of an existing executable")
        if executable.suffix.lower() in {".bat", ".cmd", ".ps1"}:
            raise ValueError("Use an executable, such as python.exe, with the script path as an argument")
        with self.lock:
            key = uuid.uuid4().hex
            self.definitions[key] = {"id": key, "label": label, "argv": argv}
            self._persist()
            return self.definitions[key]

    def _persist(self):
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.definitions, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def remove(self, key):
        with self.lock:
            if key not in self.definitions:
                raise KeyError(key)
            del self.definitions[key]
            self._persist()

    def start(self, key):
        with self.lock:
            definition = self.definitions[key]
            if len(self.processes) >= 4:
                raise ValueError("Four tasks are already running; stop one first")
            process = subprocess.Popen(definition["argv"], shell=False, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            run_id = uuid.uuid4().hex
            self.runs[run_id] = {"id": run_id, "label": definition["label"], "state": "running",
                                 "started": time.time(), "output": "", "exit_code": None}
            self.processes[run_id] = process
            # Retain only the newest 50 completed/running records.
            for old in list(self.runs):
                if len(self.runs) <= 50:
                    break
                if old not in self.processes:
                    del self.runs[old]
            threading.Thread(target=self._watch, args=(run_id, process), daemon=True).start()
            return dict(self.runs[run_id])

    def _watch(self, run_id, process):
        import codecs
        decoder = codecs.getincrementaldecoder("utf-8")("replace")
        try:
            while chunk := process.stdout.read1(2048):
                with self.lock:
                    run = self.runs[run_id]
                    run["output"] = (run["output"] + decoder.decode(chunk))[-16000:]
            code = process.wait()
            with self.lock:
                run = self.runs[run_id]
                run["exit_code"] = code
                if run["state"] != "stopped":
                    run["state"] = "completed" if code == 0 else "failed"
        finally:
            process.stdout.close()
            with self.lock:
                self.processes.pop(run_id, None)

    def stop(self, run_id):
        import psutil
        with self.lock:
            process = self.processes.get(run_id)
            if process is None:
                return
            self.runs[run_id]["state"] = "stopped"
            try:
                parent = psutil.Process(process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                parent.terminate()
                _, alive = psutil.wait_procs(children + [parent], timeout=1)
                for proc in alive:
                    try:
                        proc.kill()
                    except psutil.NoSuchProcess:
                        pass
            except psutil.NoSuchProcess:
                pass

    def stop_all(self):
        with self.lock:
            keys = list(self.processes)
        for key in keys:
            self.stop(key)

    def snapshot(self, admin=False):
        with self.lock:
            return {"actions": [dict(v) if admin else {"id": v["id"], "label": v["label"]}
                                for v in self.definitions.values()],
                    "runs": [dict(v) for v in reversed(list(self.runs.values()))]}
