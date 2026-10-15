import io
import pytest
from app.models import User, Jobs, Application, Review


@pytest.mark.smoke
def test_app_is_testing_mode(test_app):
    """Verify application is running in TESTING mode with isolated DB."""
    assert test_app.config['TESTING'] is True
    assert 'stqa_test_' in test_app.config['SQLALCHEMY_DATABASE_URI']


@pytest.mark.smoke
def test_database_isolation_from_production(test_app, db):
    """
    Critical STQA Check:
    Verify that test database has zero contamination from original site.db records.
    Original site.db contains 5 users ('Google', 'Amazon', etc.).
    A fresh test DB must have 0 users.
    """
    users = User.query.all()
    assert len(users) == 0, "Test database is not isolated! Production data was found."


@pytest.mark.smoke
def test_homepage_loads(client):
    """Verify public homepage loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Job Portal' in response.data


@pytest.mark.smoke
def test_show_jobs_page_loads(client):
    """Verify /show_jobs endpoint loads successfully."""
    response = client.get('/show_jobs')
    assert response.status_code == 200
    assert b'Job Portal' in response.data


@pytest.mark.smoke
def test_register_page_loads(client):
    """Verify registration page loads successfully."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Join Today' in response.data


@pytest.mark.smoke
def test_login_page_loads(client):
    """Verify login page loads successfully."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Log In' in response.data


@pytest.mark.smoke
def test_user_registration_flow(client, db):
    """Verify new user can register and is saved in isolated database."""
    response = client.post('/register', data={
        'usertype': 'Job Seeker',
        'username': 'SmokeTester',
        'email': 'smoketester@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your account has been created!' in response.data

    user = User.query.filter_by(email='smoketester@example.com').first()
    assert user is not None
    assert user.username == 'SmokeTester'
    assert user.usertype == 'Job Seeker'


@pytest.mark.smoke
def test_company_login_and_post_job(client, auth, seed_data, db):
    """Verify company can log in and post a new job."""
    # Log in as seeded Company
    login_resp = auth.login(
        email='hr@testcorp.com',
        password='password123',
        usertype='Company'
    )
    assert login_resp.status_code == 200

    # Post a new job
    post_resp = client.post('/post_jobs', data={
        'title': 'Senior QA Lead',
        'industry': 'Computer And Technology',
        'description': 'Leading our software testing and quality assurance team.'
    }, follow_redirects=True)

    assert post_resp.status_code == 200
    assert b'Job opening has been posted successfully!' in post_resp.data

    job = Jobs.query.filter_by(title='Senior QA Lead').first()
    assert job is not None
    assert job.user_id == seed_data['company'].id


@pytest.mark.smoke
def test_job_application_submission_with_resume(client, auth, seed_data, db):
    """Verify candidate can submit an application with an uploaded image resume."""
    auth.login(
        email='jane@example.com',
        password='password123',
        usertype='Job Seeker'
    )

    # Fake resume image data
    resume_file = (io.BytesIO(b"fake image data"), "test_resume.png")

    response = client.post(f'/post_cvs/{seed_data["job"].id}', data={
        'gender': 'Female',
        'degree': 'cBachelor',
        'industry': 'Computer And Technology',
        'experience': 4,
        'cover_letter': 'Excited to apply for this QA role!',
        'cv': resume_file
    }, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b'Your application has been submitted successfully!' in response.data

    app_record = Application.query.filter_by(job_id=seed_data['job'].id).first()
    assert app_record is not None
    assert app_record.user_id == seed_data['job_seeker'].id
    assert app_record.cv.endswith('.png')
    assert app_record.cv != 'test_resume.png', "Resume filename should be sanitized/randomized!"


@pytest.mark.smoke
def test_application_authorization_protection(client, auth, seed_data, db):
    """
    STQA Security Verification:
    Verify that another company cannot view applications for jobs it does not own.
    """
    # Create a rival company
    from app import bcrypt
    rival_corp = User(
        username='RivalCorp',
        usertype='Company',
        email='rival@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8')
    )
    db.session.add(rival_corp)
    db.session.commit()

    # Log in as RivalCorp and try to access TestCorp's job applications
    auth.login(email='rival@example.com', password='password123', usertype='Company')
    response = client.get(f'/show_applications/{seed_data["job"].id}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Access denied' in response.data
