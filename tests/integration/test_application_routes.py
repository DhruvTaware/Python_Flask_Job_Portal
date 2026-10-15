import io
import pytest
from app.models import Application, Jobs


@pytest.mark.integration
class TestApplicationWorkflowsIntegration:
    """Integration tests for job application submission and resume handling."""

    def test_application_submission_valid_resume_success(self, client, auth, seed_data, db):
        """Verify job seeker can submit an application with a valid PNG image resume."""
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        resume_payload = (io.BytesIO(b"\x89PNG\r\n\x1a\nfake_image_content"), 'my_resume.png')

        response = client.post(
            f'/post_cvs/{seed_data["job"].id}',
            data={
                'gender': 'Male',
                'degree': 'bMaster',
                'industry': 'Computer And Technology',
                'experience': 5,
                'cover_letter': 'I am well-versed in integration testing and CI/CD pipelines.',
                'cv': resume_payload
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Your application has been submitted successfully!' in response.data

        # Verify application record created in DB
        app_record = Application.query.filter_by(
            user_id=seed_data['job_seeker'].id,
            job_id=seed_data['job'].id
        ).first()

        assert app_record is not None
        assert app_record.degree == 'bMaster'
        assert app_record.experience == 5
        assert app_record.cv.endswith('.png')
        assert app_record.cv != 'my_resume.png', "Uploaded resume filename must be randomized for security!"

    def test_application_submission_valid_jpg_resume_success(self, client, auth, seed_data, db):
        """Verify job seeker can submit an application with a JPG format resume."""
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        resume_payload = (io.BytesIO(b"\xff\xd8\xff\xe0fake_jpeg_content"), 'resume_scan.jpg')

        response = client.post(
            f'/post_cvs/{seed_data["job"].id}',
            data={
                'gender': 'Female',
                'degree': 'cBachelor',
                'industry': 'Computer And Technology',
                'experience': 3,
                'cover_letter': 'Experienced QA analyst with automation credentials.',
                'cv': resume_payload
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Your application has been submitted successfully!' in response.data

        app_record = Application.query.filter_by(user_id=seed_data['job_seeker'].id).first()
        assert app_record is not None
        assert app_record.cv.endswith('.jpg')

    def test_application_submission_missing_resume_rejected(self, client, auth, seed_data, db):
        """Verify application submission without a resume file is rejected."""
        initial_app_count = Application.query.count()
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        # Submit form with empty/missing file
        response = client.post(
            f'/post_cvs/{seed_data["job"].id}',
            data={
                'gender': 'Male',
                'degree': 'cBachelor',
                'industry': 'Computer And Technology',
                'experience': 2,
                'cover_letter': 'Cover letter submitted without a resume attachment.',
                'cv': (io.BytesIO(b''), '')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        # Should stay on page and render form error
        assert b'This field is required' in response.data or b'Please upload your resume' in response.data
        assert Application.query.count() == initial_app_count

    def test_application_submission_unsupported_file_extension_rejected(self, client, auth, seed_data, db):
        """
        Verify application submission with unsupported file extensions (.pdf, .docx) is rejected.
        The portal enforces image-based resumes (.jpg, .png, .bmp).
        """
        initial_app_count = Application.query.count()
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        pdf_payload = (io.BytesIO(b"%PDF-1.4 fake pdf data"), 'unsupported_document.pdf')

        response = client.post(
            f'/post_cvs/{seed_data["job"].id}',
            data={
                'gender': 'Female',
                'degree': 'aPHD',
                'industry': 'Computer And Technology',
                'experience': 6,
                'cover_letter': 'Cover letter with PDF attachment.',
                'cv': pdf_payload
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Images only' in response.data
        assert Application.query.count() == initial_app_count

    def test_application_submission_executable_rejected(self, client, auth, seed_data, db):
        """Verify malicious executable upload attempt (.exe) is rejected."""
        initial_app_count = Application.query.count()
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        exe_payload = (io.BytesIO(b"MZ\x90\x00malicious binary content"), 'exploit.exe')

        response = client.post(
            f'/post_cvs/{seed_data["job"].id}',
            data={
                'gender': 'Others',
                'degree': 'cBachelor',
                'industry': 'Computer And Technology',
                'experience': 1,
                'cover_letter': 'Exploit attempt.',
                'cv': exe_payload
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Images only' in response.data
        assert Application.query.count() == initial_app_count

    def test_application_submission_nonexistent_job_fails(self, client, auth, seed_data, db):
        """Verify applying to a non-existent job ID redirects with danger flash."""
        auth.login(
            email=seed_data['job_seeker'].email,
            password=seed_data['raw_password'],
            usertype='Job Seeker'
        )

        resume_payload = (io.BytesIO(b"fake image"), 'resume.png')

        response = client.post(
            '/post_cvs/99999',  # Non-existent job ID
            data={
                'gender': 'Male',
                'degree': 'cBachelor',
                'industry': 'Computer And Technology',
                'experience': 1,
                'cover_letter': 'Valid letter',
                'cv': resume_payload
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Job not found.' in response.data
