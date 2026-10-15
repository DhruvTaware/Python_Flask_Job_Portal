import pytest
from app import bcrypt
from app.models import User


@pytest.mark.integration
class TestRegistrationIntegration:
    """Integration tests for user registration HTTP flows and persistence."""

    def test_job_seeker_registration_success(self, client, db):
        """Verify successful registration of a Job Seeker user."""
        response = client.post('/register', data={
            'username': 'IntegrationSeeker',
            'usertype': 'Job Seeker',
            'email': 'int_seeker@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow_redirects=False)

        # Expect redirect to login page
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

        # Verify user is persisted in the isolated test database
        user = User.query.filter_by(email='int_seeker@example.com').first()
        assert user is not None
        assert user.username == 'IntegrationSeeker'
        assert user.usertype == 'Job Seeker'
        assert bcrypt.check_password_hash(user.password, 'Password123!')

    def test_company_registration_success(self, client, db):
        """Verify successful registration of a Company user."""
        response = client.post('/register', data={
            'username': 'IntegrationCorp',
            'usertype': 'Company',
            'email': 'int_corp@example.com',
            'password': 'CompanyPass123!',
            'confirm_password': 'CompanyPass123!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Your account has been created!' in response.data

        company = User.query.filter_by(username='IntegrationCorp').first()
        assert company is not None
        assert company.usertype == 'Company'
        assert company.email == 'int_corp@example.com'

    def test_registration_duplicate_username_fails(self, client, seed_data, db):
        """Verify registration is rejected when username already exists."""
        initial_user_count = User.query.count()
        response = client.post('/register', data={
            'username': seed_data['job_seeker'].username,  # Duplicate
            'usertype': 'Job Seeker',
            'email': 'unique_email@test.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'That username is already taken' in response.data
        assert User.query.count() == initial_user_count

    def test_registration_duplicate_email_fails(self, client, seed_data, db):
        """Verify registration is rejected when email already exists."""
        initial_user_count = User.query.count()
        response = client.post('/register', data={
            'username': 'UniqueNewUser',
            'usertype': 'Job Seeker',
            'email': seed_data['company'].email,  # Duplicate
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'That email is already taken' in response.data
        assert User.query.count() == initial_user_count

    def test_registration_password_mismatch_fails(self, client, db):
        """Verify registration fails when passwords do not match."""
        initial_user_count = User.query.count()
        response = client.post('/register', data={
            'username': 'MismatchUser',
            'usertype': 'Job Seeker',
            'email': 'mismatch@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword456!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Field must be equal to password' in response.data
        assert User.query.count() == initial_user_count

    def test_authenticated_user_redirected_from_register(self, client, auth, seed_data):
        """Verify authenticated users are redirected away from the registration page."""
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )
        response = client.get('/register', follow_redirects=False)
        assert response.status_code == 302
        assert '/show_jobs' in response.headers['Location']


@pytest.mark.integration
class TestLoginIntegration:
    """Integration tests for user login, credentials verification, and session state."""

    def test_job_seeker_login_success(self, client, seed_data):
        """Verify valid job seeker login redirects to show_jobs."""
        response = client.post('/login', data={
            'email': seed_data['job_seeker'].email,
            'password': seed_data['raw_password'],
            'usertype': 'Job Seeker',
            'remember': False
        }, follow_redirects=False)

        assert response.status_code == 302
        assert '/show_jobs' in response.headers['Location']

    def test_company_login_success(self, client, seed_data):
        """Verify valid company login redirects to posted_jobs."""
        response = client.post('/login', data={
            'email': seed_data['company'].email,
            'password': seed_data['raw_password'],
            'usertype': 'Company',
            'remember': False
        }, follow_redirects=False)

        assert response.status_code == 302
        assert '/posted_jobs' in response.headers['Location']

    def test_login_invalid_password_rejected(self, client, seed_data):
        """Verify login fails with wrong password."""
        response = client.post('/login', data={
            'email': seed_data['company'].email,
            'password': 'WrongPassword999',
            'usertype': 'Company',
            'remember': False
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Login Unsuccessful. Please check email, password and usertype' in response.data

    def test_login_nonexistent_email_rejected(self, client, db):
        """Verify login fails when email does not exist."""
        response = client.post('/login', data={
            'email': 'nobody@nonexistent.org',
            'password': 'SomePassword123',
            'usertype': 'Job Seeker',
            'remember': False
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Login Unsuccessful. Please check email, password and usertype' in response.data

    def test_login_mismatched_usertype_rejected(self, client, seed_data):
        """
        Verify login fails when user credentials are valid but incorrect user type is selected.
        e.g., Company account attempts login selecting 'Job Seeker'.
        """
        response = client.post('/login', data={
            'email': seed_data['company'].email,
            'password': seed_data['raw_password'],
            'usertype': 'Job Seeker',  # Incorrect usertype for company account
            'remember': False
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Login Unsuccessful. Please check email, password and usertype' in response.data

    def test_login_redirects_to_next_parameter(self, client, seed_data):
        """Verify redirect to the 'next' parameter upon successful login."""
        response = client.post('/login?next=%2Fpost_jobs', data={
            'email': seed_data['company'].email,
            'password': seed_data['raw_password'],
            'usertype': 'Company',
            'remember': False
        }, follow_redirects=False)

        assert response.status_code == 302
        assert response.headers['Location'] == '/post_jobs'

    def test_authenticated_user_redirected_from_login(self, client, auth, seed_data):
        """Verify authenticated company user is redirected away from login."""
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )
        response = client.get('/login', follow_redirects=False)
        assert response.status_code == 302
        assert '/posted_jobs' in response.headers['Location']

    def test_logout_workflow(self, client, auth, seed_data):
        """Verify logout clears session and redirects to show_jobs."""
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/show_jobs' in response.headers['Location']

        # Confirm user is logged out by attempting to access a protected page
        protected_resp = client.get('/post_jobs', follow_redirects=False)
        assert protected_resp.status_code == 302
        assert '/login' in protected_resp.headers['Location']
