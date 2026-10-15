import io
import pytest
from werkzeug.datastructures import FileStorage
from app.forms import RegistrationForm, LoginForm, JobForm, ApplicationForm, ReviewForm
from app.models import User


def validate_form(form_class, test_app, data):
    """Helper to instantiate and validate a WTForms form within a Flask request context."""
    with test_app.test_request_context('/', method='POST', data=data):
        form = form_class()
        is_valid = form.validate()
        return is_valid, form.errors


def make_test_file(filename, content=b"dummy image bytes", content_type="image/png"):
    """Helper to generate a FileStorage object for file upload testing."""
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
        content_type=content_type
    )


@pytest.mark.unit
class TestRegistrationForm:
    """Unit tests for RegistrationForm including Equivalence Partitioning and BVA."""

    def test_registration_form_valid_job_seeker(self, test_app):
        """Equivalence Class: Valid Job Seeker input."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'JaneDoe',
            'email': 'jane.doe@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        })
        assert valid is True
        assert errors == {}

    def test_registration_form_valid_company(self, test_app):
        """Equivalence Class: Valid Company input."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Company',
            'username': 'GlobalTech',
            'email': 'recruiting@globaltech.com',
            'password': 'CompanyPassword123!',
            'confirm_password': 'CompanyPassword123!'
        })
        assert valid is True
        assert errors == {}

    def test_registration_form_missing_required_fields(self, test_app):
        """Equivalence Class: Missing mandatory fields."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': '',
            'username': '',
            'email': '',
            'password': '',
            'confirm_password': ''
        })
        assert valid is False
        assert 'usertype' in errors
        assert 'username' in errors
        assert 'email' in errors
        assert 'password' in errors

    @pytest.mark.parametrize("invalid_email", [
        'plainaddress',
        '@missinguser.com',
        'user@.com',
        'user@domain..com'
    ])
    def test_registration_form_invalid_email_formats(self, test_app, invalid_email):
        """Equivalence Partitioning: Malformed email strings."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'ValidUser',
            'email': invalid_email,
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is False
        assert 'email' in errors

    def test_registration_form_password_mismatch(self, test_app):
        """Equivalence Class: password does not match confirm_password."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'ValidUser',
            'email': 'user@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword456!'
        })
        assert valid is False
        assert 'confirm_password' in errors

    # --- Boundary Value Analysis: Username (min=2, max=20) ---

    def test_registration_username_below_min_boundary(self, test_app):
        """BVA: Length = 1 (Below min=2 -> Invalid)."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'A',
            'email': 'bva1@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is False
        assert 'username' in errors

    def test_registration_username_at_min_boundary(self, test_app):
        """BVA: Length = 2 (At min=2 -> Valid)."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'AB',
            'email': 'bva2@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is True
        assert errors == {}

    def test_registration_username_just_above_min_boundary(self, test_app):
        """BVA: Length = 3 (Above min=2 -> Valid)."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'ABC',
            'email': 'bva3@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is True
        assert errors == {}

    def test_registration_username_just_below_max_boundary(self, test_app):
        """BVA: Length = 19 (Below max=20 -> Valid)."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'A' * 19,
            'email': 'bva19@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is True
        assert errors == {}

    def test_registration_username_at_max_boundary(self, test_app):
        """BVA: Length = 20 (At max=20 -> Valid)."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'A' * 20,
            'email': 'bva20@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is True
        assert errors == {}

    def test_registration_username_above_max_boundary(self, test_app):
        """BVA: Length = 21 (Above max=20 -> Invalid)."""
        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'A' * 21,
            'email': 'bva21@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is False
        assert 'username' in errors

    # --- Custom Database Validators: Unique Username & Email ---

    def test_registration_duplicate_username_fails(self, test_app, db):
        """Verify custom validator rejects duplicate username."""
        existing_user = User(
            username='ExistingUser',
            usertype='Job Seeker',
            email='existing@test.com',
            password='hash'
        )
        db.session.add(existing_user)
        db.session.commit()

        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Company',
            'username': 'ExistingUser',
            'email': 'newemail@test.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is False
        assert 'username' in errors
        assert 'That username is already taken' in errors['username'][0]

    def test_registration_duplicate_email_fails(self, test_app, db):
        """Verify custom validator rejects duplicate email."""
        existing_user = User(
            username='UniqueUser1',
            usertype='Company',
            email='duplicate@test.com',
            password='hash'
        )
        db.session.add(existing_user)
        db.session.commit()

        valid, errors = validate_form(RegistrationForm, test_app, {
            'usertype': 'Job Seeker',
            'username': 'UniqueUser2',
            'email': 'duplicate@test.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert valid is False
        assert 'email' in errors
        assert 'That email is already taken' in errors['email'][0]


@pytest.mark.unit
class TestLoginForm:
    """Unit tests for LoginForm."""

    def test_login_form_valid_data(self, test_app):
        """Equivalence Class: Valid login inputs."""
        valid, errors = validate_form(LoginForm, test_app, {
            'usertype': 'Company',
            'email': 'company@login.com',
            'password': 'MyPassword123!',
            'remember': True
        })
        assert valid is True
        assert errors == {}

    def test_login_form_missing_fields(self, test_app):
        """Equivalence Class: Missing mandatory login inputs."""
        valid, errors = validate_form(LoginForm, test_app, {
            'usertype': '',
            'email': '',
            'password': ''
        })
        assert valid is False
        assert 'email' in errors
        assert 'password' in errors

    def test_login_form_invalid_email_format(self, test_app):
        """Equivalence Class: Malformed email in login form."""
        valid, errors = validate_form(LoginForm, test_app, {
            'usertype': 'Job Seeker',
            'email': 'invalid_email_without_at',
            'password': 'Password123!'
        })
        assert valid is False
        assert 'email' in errors


@pytest.mark.unit
class TestJobForm:
    """Unit tests for JobForm including BVA on job title."""

    def test_job_form_valid_data(self, test_app):
        """Equivalence Class: Valid job posting input."""
        valid, errors = validate_form(JobForm, test_app, {
            'title': 'Senior QA Engineer',
            'industry': 'Computer And Technology',
            'description': 'Responsible for STQA, test automation, and code coverage.'
        })
        assert valid is True
        assert errors == {}

    def test_job_form_missing_required_fields(self, test_app):
        """Equivalence Class: Missing title or description."""
        valid, errors = validate_form(JobForm, test_app, {
            'title': '',
            'industry': 'Computer And Technology',
            'description': ''
        })
        assert valid is False
        assert 'title' in errors
        assert 'description' in errors

    def test_job_form_invalid_industry_choice(self, test_app):
        """Equivalence Class: Selection outside defined industry choices."""
        valid, errors = validate_form(JobForm, test_app, {
            'title': 'Astronomer',
            'industry': 'Unknown_Industry_Not_In_Choices',
            'description': 'Observe deep space objects.'
        })
        assert valid is False
        assert 'industry' in errors

    # --- Boundary Value Analysis: Title (min=2, max=100) ---

    def test_job_title_below_min_boundary(self, test_app):
        """BVA: Title Length = 1 (Below min=2 -> Invalid)."""
        valid, errors = validate_form(JobForm, test_app, {
            'title': 'Q',
            'industry': 'Computer And Technology',
            'description': 'Short title test.'
        })
        assert valid is False
        assert 'title' in errors

    def test_job_title_at_min_boundary(self, test_app):
        """BVA: Title Length = 2 (At min=2 -> Valid)."""
        valid, errors = validate_form(JobForm, test_app, {
            'title': 'QA',
            'industry': 'Computer And Technology',
            'description': 'Min boundary title test.'
        })
        assert valid is True
        assert errors == {}

    def test_job_title_at_max_boundary(self, test_app):
        """BVA: Title Length = 100 (At max=100 -> Valid)."""
        valid, errors = validate_form(JobForm, test_app, {
            'title': 'T' * 100,
            'industry': 'Computer And Technology',
            'description': 'Max boundary title test.'
        })
        assert valid is True
        assert errors == {}

    def test_job_title_above_max_boundary(self, test_app):
        """BVA: Title Length = 101 (Above max=100 -> Invalid)."""
        valid, errors = validate_form(JobForm, test_app, {
            'title': 'T' * 101,
            'industry': 'Computer And Technology',
            'description': 'Exceeded boundary title test.'
        })
        assert valid is False
        assert 'title' in errors


@pytest.mark.unit
class TestApplicationForm:
    """Unit tests for ApplicationForm, file upload restrictions, and input types."""

    def test_application_form_valid_data(self, test_app):
        """Equivalence Class: Complete valid application with PNG image resume."""
        file_obj = make_test_file('candidate_cv.png')
        valid, errors = validate_form(ApplicationForm, test_app, {
            'gender': 'Female',
            'degree': 'cBachelor',
            'industry': 'Computer And Technology',
            'experience': 3,
            'cover_letter': 'Experienced test engineer ready to deliver quality.',
            'cv': file_obj
        })
        assert valid is True
        assert errors == {}

    def test_application_form_missing_required_cover_letter(self, test_app):
        """Equivalence Class: Missing mandatory cover letter."""
        file_obj = make_test_file('candidate_cv.jpg')
        valid, errors = validate_form(ApplicationForm, test_app, {
            'gender': 'Male',
            'degree': 'bMaster',
            'industry': 'Finance And Economic',
            'experience': 5,
            'cover_letter': '',
            'cv': file_obj
        })
        assert valid is False
        assert 'cover_letter' in errors

    def test_application_form_missing_file_upload(self, test_app):
        """Equivalence Class: Missing file upload (FileRequired)."""
        valid, errors = validate_form(ApplicationForm, test_app, {
            'gender': 'Male',
            'degree': 'bMaster',
            'industry': 'Healthcare',
            'experience': 2,
            'cover_letter': 'Cover letter text'
        })
        assert valid is False
        assert 'cv' in errors
        assert 'Please upload your resume' in errors['cv'][0]

    @pytest.mark.parametrize("supported_ext", ['cv.jpg', 'cv.png', 'cv.bmp'])
    def test_application_form_supported_file_extensions(self, test_app, supported_ext):
        """Equivalence Class: Supported file types (jpg, png, bmp)."""
        file_obj = make_test_file(supported_ext)
        valid, errors = validate_form(ApplicationForm, test_app, {
            'gender': 'Others',
            'degree': 'aPHD',
            'industry': 'Pharmaceutical',
            'experience': 7,
            'cover_letter': 'Ph.D. researcher application.',
            'cv': file_obj
        })
        assert valid is True
        assert errors == {}

    @pytest.mark.parametrize("unsupported_ext", [
        'resume.pdf',
        'document.docx',
        'payload.exe',
        'notes.txt',
        'archive.zip'
    ])
    def test_application_form_unsupported_file_extensions(self, test_app, unsupported_ext):
        """Equivalence Class: Unsupported and potentially hazardous file types."""
        file_obj = make_test_file(unsupported_ext, content_type='application/octet-stream')
        valid, errors = validate_form(ApplicationForm, test_app, {
            'gender': 'Male',
            'degree': 'cBachelor',
            'industry': 'Transportation',
            'experience': 1,
            'cover_letter': 'Applying with unsupported format.',
            'cv': file_obj
        })
        assert valid is False
        assert 'cv' in errors
        assert 'Images only' in errors['cv'][0]

    def test_application_form_non_integer_experience(self, test_app):
        """Equivalence Class: Non-integer string passed to IntegerField."""
        file_obj = make_test_file('cv.png')
        valid, errors = validate_form(ApplicationForm, test_app, {
            'gender': 'Male',
            'degree': 'cBachelor',
            'industry': 'Aerospace',
            'experience': 'four_years',
            'cover_letter': 'Experienced pilot.',
            'cv': file_obj
        })
        assert valid is False
        assert 'experience' in errors


@pytest.mark.unit
class TestReviewForm:
    """Unit tests for ReviewForm."""

    def test_review_form_valid_data(self, test_app):
        """Equivalence Class: Valid review inputs."""
        valid, errors = validate_form(ReviewForm, test_app, {
            'username': 'SatisfiedEmployer',
            'review': 'Found incredible talent on this portal within 48 hours!'
        })
        assert valid is True
        assert errors == {}

    def test_review_form_missing_username(self, test_app):
        """Equivalence Class: Missing mandatory username."""
        valid, errors = validate_form(ReviewForm, test_app, {
            'username': '',
            'review': 'Great website overall.'
        })
        assert valid is False
        assert 'username' in errors

    def test_review_form_missing_review_body(self, test_app):
        """Equivalence Class: Missing mandatory review text."""
        valid, errors = validate_form(ReviewForm, test_app, {
            'username': 'ReviewerName',
            'review': ''
        })
        assert valid is False
        assert 'review' in errors
