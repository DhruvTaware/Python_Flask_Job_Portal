import io
import pytest
from app import bcrypt
from app.models import User, Jobs, Application


@pytest.mark.integration
class TestAnonymousAccessControl:
    """Verify unauthenticated guests cannot access protected routes."""

    @pytest.mark.parametrize('endpoint', [
        '/post_jobs',
        '/posted_jobs',
        '/post_cvs/1',
        '/show_applications/1',
        '/resume/1',
        '/meeting/1',
        '/logout'
    ])
    def test_anonymous_access_redirects_to_login(self, client, endpoint):
        """Verify anonymous requests to protected routes redirect to login."""
        response = client.get(endpoint, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']


@pytest.mark.integration
class TestRoleBasedAccessControl:
    """Verify role segregation between Job Seeker and Company accounts."""

    def test_job_seeker_cannot_access_post_jobs(self, client, auth, seed_data):
        """Verify Job Seeker is forbidden from accessing the job posting page."""
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        response = client.get('/post_jobs', follow_redirects=True)
        assert response.status_code == 200
        assert b'Only registered companies can post job openings.' in response.data

    def test_job_seeker_cannot_post_jobs_via_http_post(self, client, auth, seed_data, db):
        """Verify Job Seeker cannot forge an HTTP POST to create a job."""
        initial_job_count = Jobs.query.count()
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        response = client.post('/post_jobs', data={
            'title': 'Forged Job Opening',
            'industry': 'Computer And Technology',
            'description': 'Attempting unauthorized job creation.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Only registered companies can post job openings.' in response.data
        assert Jobs.query.count() == initial_job_count

    def test_job_seeker_cannot_access_posted_jobs_management(self, client, auth, seed_data):
        """Verify Job Seeker cannot access the company posted jobs dashboard."""
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        response = client.get('/posted_jobs', follow_redirects=True)
        assert response.status_code == 200
        assert b'Only companies can access posted jobs management.' in response.data

    def test_job_seeker_cannot_access_show_applications(self, client, auth, seed_data):
        """Verify Job Seeker cannot view applicant lists."""
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        response = client.get(f'/show_applications/{seed_data["job"].id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied. Only company accounts can view applicants.' in response.data

    def test_company_cannot_apply_for_jobs(self, client, auth, seed_data):
        """Verify Company accounts cannot submit job applications."""
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )

        response = client.get(f'/post_cvs/{seed_data["job"].id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Only job seekers can apply for jobs.' in response.data


@pytest.mark.integration
class TestCrossTenantAndResourceAuthorization:
    """Verify isolation between competing companies and protection of applicant resumes."""

    @pytest.fixture(autouse=True)
    def setup_secondary_tenant_and_application(self, db, seed_data):
        """
        Setup test environment:
        1. Rival company (RivalCorp)
        2. Second job seeker (BobApplicant)
        3. Application from JaneCandidate to TestCorp's job
        """
        # Rival Company
        self.rival_company = User(
            username='RivalCorp',
            usertype='Company',
            email='hr@rivalcorp.com',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        # Unrelated job seeker
        self.unrelated_seeker = User(
            username='BobSeeker',
            usertype='Job Seeker',
            email='bob@seeker.net',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(self.rival_company)
        db.session.add(self.unrelated_seeker)
        db.session.commit()

        # Application submitted by Jane to TestCorp's job
        self.test_application = Application(
            gender='Female',
            degree='cBachelor',
            industry='Computer And Technology',
            experience=3,
            cv='jane_resume_token123.png',
            cover_letter='Jane cover letter for TestCorp QA job.',
            application_submiter=seed_data['job_seeker'],
            application_jober=seed_data['job']
        )
        db.session.add(self.test_application)
        db.session.commit()

    def test_rival_company_cannot_view_applications_of_other_company(self, client, auth, seed_data):
        """Verify Company B cannot view applicants for Company A's job."""
        auth.login(
            email='hr@rivalcorp.com',
            password='password123',
            usertype='Company'
        )

        response = client.get(f'/show_applications/{seed_data["job"].id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied. You can only view applications for jobs posted by your company.' in response.data

    def test_applicant_can_view_own_resume(self, client, auth, seed_data):
        """Verify the candidate who submitted the resume is authorized to view it."""
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        response = client.get(f'/resume/{self.test_application.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'jane_resume_token123.png' in response.data

    def test_hiring_company_can_view_applicant_resume(self, client, auth, seed_data):
        """Verify the company that posted the job is authorized to view the applicant's resume."""
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )

        response = client.get(f'/resume/{self.test_application.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'jane_resume_token123.png' in response.data

    def test_unrelated_job_seeker_cannot_view_another_applicant_resume(self, client, auth):
        """Verify Job Seeker B cannot view Job Seeker A's resume."""
        auth.login(
            email='bob@seeker.net',
            password='password123',
            usertype='Job Seeker'
        )

        response = client.get(f'/resume/{self.test_application.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied. You do not have permission to view this resume.' in response.data

    def test_rival_company_cannot_view_applicant_resume_of_another_company(self, client, auth):
        """Verify Rival Company cannot view resumes submitted to another company's job."""
        auth.login(
            email='hr@rivalcorp.com',
            password='password123',
            usertype='Company'
        )

        response = client.get(f'/resume/{self.test_application.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied. You do not have permission to view this resume.' in response.data

    def test_resume_not_found_redirects(self, client, auth, seed_data):
        """Verify non-existent resume ID redirects with not found flash."""
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )

        response = client.get('/resume/99999', follow_redirects=True)
        assert response.status_code == 200
        assert b'Resume or application not found.' in response.data

    def test_meeting_authorization_employer_and_applicant(self, client, auth, seed_data):
        """Verify interview meeting room is accessible to applicant and hiring company."""
        # Check applicant access
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )
        resp_applicant = client.get(f'/meeting/{self.test_application.id}', follow_redirects=True)
        assert resp_applicant.status_code == 200
        assert b'<h1>Interview</h1>' in resp_applicant.data

        auth.logout()

        # Check employer access
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )
        resp_employer = client.get(f'/meeting/{self.test_application.id}', follow_redirects=True)
        assert resp_employer.status_code == 200
        assert b'<h1>Interview</h1>' in resp_employer.data

    def test_unauthorized_user_cannot_join_interview_meeting(self, client, auth):
        """Verify unrelated users cannot join the interview meeting."""
        auth.login(
            email='hr@rivalcorp.com',
            password='password123',
            usertype='Company'
        )
        response = client.get(f'/meeting/{self.test_application.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Access denied. You do not have permission to join this interview.' in response.data
