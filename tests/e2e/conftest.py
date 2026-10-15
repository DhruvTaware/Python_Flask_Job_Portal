import os
import time
import socket
import threading
import pytest
from sqlalchemy import create_engine
from werkzeug.serving import make_server

# Redirect temp directories to Drive E to avoid os error 112 on low-disk C:
TEMP_DIR = r"E:\temp"
os.makedirs(TEMP_DIR, exist_ok=True)
os.environ["TEMP"] = TEMP_DIR
os.environ["TMP"] = TEMP_DIR
os.environ["SE_CACHE_PATH"] = os.path.join(TEMP_DIR, "selenium")

from app import app, db as _db, bcrypt
from app.models import User, Jobs, Application
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def find_free_port():
    """Find and return an open port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@pytest.fixture(scope='module')
def live_server():
    """
    Module-scoped live HTTP server fixture for Selenium E2E testing.
    Uses an isolated temporary SQLite database and runs Flask on an ephemeral port.
    Guarantees app/site.db is completely untouched.
    """
    port = find_free_port()
    db_path = os.path.join(TEMP_DIR, f"stqa_e2e_{int(time.time() * 1000)}.db")
    test_engine = create_engine(
        f'sqlite:///{db_path}',
        connect_args={'check_same_thread': False}
    )

    original_engines = _db._app_engines.get(app)
    original_uri = app.config.get('SQLALCHEMY_DATABASE_URI')

    _db._app_engines[app] = {None: test_engine}
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    static_dir = os.path.join(app.root_path, 'static')
    before_files = set(os.listdir(static_dir)) if os.path.exists(static_dir) else set()

    with app.app_context():
        _db.create_all()

        hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
        company = User(
            username='SeleniumCorp',
            usertype='Company',
            email='recruiting@seleniumcorp.com',
            password=hashed_pwd
        )
        seeker = User(
            username='SeleniumCandidate',
            usertype='Job Seeker',
            email='candidate@selenium.org',
            password=hashed_pwd
        )
        _db.session.add(company)
        _db.session.add(seeker)
        _db.session.commit()

        job = Jobs(
            title='Senior Automation Engineer',
            industry='Computer And Technology',
            description='Automating end-to-end user journeys using Selenium WebDriver.',
            job_applier=company
        )
        _db.session.add(job)
        _db.session.commit()

        server_context = {
            'base_url': f'http://127.0.0.1:{port}',
            'company_email': 'recruiting@seleniumcorp.com',
            'seeker_email': 'candidate@selenium.org',
            'raw_password': 'password123',
            'job_id': job.id,
            'job_title': job.title
        }

    # Start live server on ephemeral port in daemon thread
    server = make_server('127.0.0.1', port, app)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    yield server_context

    # Teardown: shutdown server, clean database, and restore environment
    server.shutdown()

    with app.app_context():
        _db.drop_all()

    test_engine.dispose()

    if original_engines:
        _db._app_engines[app] = original_engines
    app.config['SQLALCHEMY_DATABASE_URI'] = original_uri

    # Clean up static files uploaded during testing
    if os.path.exists(static_dir):
        after_files = set(os.listdir(static_dir))
        for new_file in (after_files - before_files):
            try:
                os.remove(os.path.join(static_dir, new_file))
            except OSError:
                pass

    # Remove temporary database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


@pytest.fixture(scope='function')
def browser():
    """
    Function-scoped Selenium Chrome WebDriver fixture configured for headless execution.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)

    yield driver

    driver.quit()
