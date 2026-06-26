import os
import sys

# Auto-aktifkan virtual environment jika dijalankan dari Python global
venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'Scripts', 'python.exe')
if os.path.exists(venv_python) and sys.executable != venv_python:
    import subprocess
    try:
        sys.exit(subprocess.call([venv_python] + sys.argv))
    except KeyboardInterrupt:
        sys.exit(0)

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
