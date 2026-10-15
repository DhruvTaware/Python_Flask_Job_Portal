import os
import tempfile
import pytest
from sqlalchemy import create_engine
from app import app as flask_app, db as _db, bcrypt
from app.models import User, Jobs, Application, Review


@pytest.fixture(scope='session')
def base_app():
    """Configure base application settings for test session."""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SECRET_KEY'] = 'stqa-test-secret-key-12345'
    return flask_app


@pytest.fixture(scope='function')
def test_app(base_app):
    """
    Function-scoped fixture creating a dedicated, temporary SQLite test database.
    Rebinds Flask-SQLAlchemy's engine to guarantee 100% isolation from app/site.db.
    """
    temp_dir = r"E:\temp"
    os.makedirs(temp_dir, exist_ok=True)
    db_fd, db_path = tempfile.mkstemp(suffix='.db', prefix='stqa_test_', dir=temp_dir)
    os.close(db_fd)

    test_engine = create_engine(f'sqlite:///{db_path}')
    original_engines = _db._app_engines.get(base_app)
    original_uri = base_app.config.get('SQLALCHEMY_DATABASE_URI')

    _db._app_engines[base_app] = {None: test_engine}
    base_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    static_dir = os.path.join(base_app.root_path, 'static')
    before_files = set(os.listdir(static_dir)) if os.path.exists(static_dir) else set()

    with base_app.app_context():
        _db.create_all()
        yield base_app
        _db.session.remove()
        _db.drop_all()

    # Restore original engine pointing to app/site.db
    if original_engines:
        _db._app_engines[base_app] = original_engines
    base_app.config['SQLALCHEMY_DATABASE_URI'] = original_uri

    # Dispose test engine to release SQLite file lock on Windows
    test_engine.dispose()

    # Clean up test-created files in static directory
    if os.path.exists(static_dir):
        after_files = set(os.listdir(static_dir))
        for new_file in (after_files - before_files):
            try:
                os.remove(os.path.join(static_dir, new_file))
            except OSError:
                pass

    # Cleanup temporary SQLite file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


@pytest.fixture(scope='function')
def db(test_app):
    """Yield database session within test app context."""
    with test_app.app_context():
        yield _db


@pytest.fixture(scope='function')
def client(test_app):
    """Flask test client for simulating HTTP requests."""
    return test_app.test_client()


@pytest.fixture(scope='function')
def seed_data(test_app, db):
    """
    Seeds a standard test dataset for integration and regression testing.
    """
    hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')

    company = User(
        username='TestCorp',
        usertype='Company',
        email='hr@testcorp.com',
        password=hashed_pwd
    )
    job_seeker = User(
        username='JaneCandidate',
        usertype='Job Seeker',
        email='jane@example.com',
        password=hashed_pwd
    )
    db.session.add(company)
    db.session.add(job_seeker)
    db.session.commit()

    job = Jobs(
        title='QA Automation Engineer',
        industry='Computer And Technology',
        description='Looking for an STQA expert with Selenium and pytest experience.',
        job_applier=company
    )
    db.session.add(job)
    db.session.commit()

    return {
        'company': company,
        'job_seeker': job_seeker,
        'job': job,
        'raw_password': 'password123'
    }


class AuthHelper:
    """Helper class to simulate login and logout in tests."""
    def __init__(self, client):
        self.client = client

    def login(self, email, password, usertype):
        return self.client.post('/login', data={
            'email': email,
            'password': password,
            'usertype': usertype,
            'remember': False
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def auth(client):
    return AuthHelper(client)
