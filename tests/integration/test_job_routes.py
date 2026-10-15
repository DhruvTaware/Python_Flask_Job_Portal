import pytest
from app.models import Jobs, User


@pytest.mark.integration
class TestJobWorkflowsIntegration:
    """Integration tests for company job posting, validation, and listing."""

    def test_company_job_posting_success(self, client, auth, seed_data, db):
        """Verify company can post a job and it is persisted in the database."""
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )

        response = client.post('/post_jobs', data={
            'title': 'Lead DevOps Engineer',
            'industry': 'Computer And Technology',
            'description': 'Responsible for CI/CD pipelines, Docker, and Kubernetes clusters.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Job opening has been posted successfully!' in response.data

        # Verify job is persisted and properly associated with the company
        job = Jobs.query.filter_by(title='Lead DevOps Engineer').first()
        assert job is not None
        assert job.industry == 'Computer And Technology'
        assert job.user_id == seed_data['company'].id
        assert 'Kubernetes' in job.description

    def test_job_posting_missing_title_rejected(self, client, auth, seed_data, db):
        """Verify job posting fails when mandatory title field is missing."""
        initial_job_count = Jobs.query.count()
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )

        response = client.post('/post_jobs', data={
            'title': '',  # Missing title
            'industry': 'Computer And Technology',
            'description': 'Description without title.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'This field is required' in response.data or b'Please fill out this field' in response.data
        assert Jobs.query.count() == initial_job_count

    def test_job_posting_missing_description_rejected(self, client, auth, seed_data, db):
        """Verify job posting fails when mandatory description field is missing."""
        initial_job_count = Jobs.query.count()
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )

        response = client.post('/post_jobs', data={
            'title': 'Valid Title',
            'industry': 'Healthcare',
            'description': ''  # Missing description
        }, follow_redirects=True)

        assert response.status_code == 200
        assert Jobs.query.count() == initial_job_count

    def test_posted_jobs_lists_only_company_own_jobs(self, client, auth, seed_data, db):
        """
        Verify /posted_jobs displays only the jobs posted by the authenticated company,
        not jobs belonging to other companies.
        """
        from app import bcrypt
        # Create a second company with its own job
        other_company = User(
            username='OtherCorp',
            usertype='Company',
            email='hr@othercorp.com',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(other_company)
        db.session.commit()

        other_job = Jobs(
            title='OtherCorp Secret Project',
            industry='Telecommunication',
            description='Proprietary telecom role.',
            job_applier=other_company
        )
        db.session.add(other_job)
        db.session.commit()

        # Log in as the first company (TestCorp)
        auth.login(
            email=seed_data['company'].email,
            password=seed_data['raw_password'],
            usertype='Company'
        )

        response = client.get('/posted_jobs', follow_redirects=True)
        assert response.status_code == 200
        # Should see its own job from seed_data
        assert seed_data['job'].title.encode('utf-8') in response.data
        # Should NOT see OtherCorp's job
        assert b'OtherCorp Secret Project' not in response.data

    def test_public_show_jobs_displays_all_jobs(self, client, seed_data):
        """Verify public /show_jobs endpoint displays available jobs."""
        response = client.get('/show_jobs')
        assert response.status_code == 200
        assert seed_data['job'].title.encode('utf-8') in response.data
