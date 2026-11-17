"""Play2Go entry point. Set App py file to fitjournal_server.py."""
import hashlib
import json
import time
from collections import deque
from threading import Lock
import os
from pathlib import Path

from flask import abort, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from waitress import serve

from fitjournal import create_app


def build_app():
    data_dir = Path(__file__).resolve().parent / 'fitjournal-data'
    data_dir.mkdir(exist_ok=True, mode=0o700)
    app = create_app({'DATABASE': str(data_dir / 'journal.sqlite3')})
    # Bind publicly on the allocation, while retaining owner authentication.
    app.before_request_funcs[None].pop(0)
    config_file = data_dir / 'access.json'
    attempts = deque()
    attempt_lock = Lock()

    @app.before_request
    def access():
        if request.endpoint == 'static':
            return None
        if not config_file.exists():
            return render_template('setup_pending.html'), 503
        try:
            config = json.loads(config_file.read_text())
            password_hash = config['password_hash']
            if not password_hash.startswith(('scrypt:', 'pbkdf2:')):
                abort(503)
        except (ValueError, KeyError):
            abort(503)
        if request.method == 'POST':
            import secrets
            token = request.form.get('csrf', '')
            if not secrets.compare_digest(token.encode(), session.get('csrf', '!').encode()):
                abort(400)
        if request.endpoint == 'login':
            return None
        if session.get('owner') != hashlib.sha256(password_hash.encode()).hexdigest():
            return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            with attempt_lock:
                now = time.monotonic()
                while attempts and attempts[0] < now - 300:
                    attempts.popleft()
                if len(attempts) >= 10:
                    abort(429)
                attempts.append(now)
            config = json.loads(config_file.read_text())
            if check_password_hash(config['password_hash'], request.form.get('password', '')):
                session.clear()
                session['owner'] = hashlib.sha256(config['password_hash'].encode()).hexdigest()
                return redirect(url_for('index'))
            error = 'Неверный пароль.'
        return render_template('login.html', error=error)

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    app.config.update(MAX_CONTENT_LENGTH=65536, SESSION_COOKIE_SAMESITE='Lax')
    return app


if __name__ == '__main__':
    serve(build_app(), host='0.0.0.0', port=int(os.environ.get('SERVER_PORT', '20261')), threads=2)
