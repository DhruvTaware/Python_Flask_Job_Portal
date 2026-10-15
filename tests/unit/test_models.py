import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import bcrypt
from app.models import User, Jobs, Application, Review, load_user


@pytest.mark.unit
class TestUserModel:
    """Unit tests for User model and authentication logic."""

    def test_create_user_success(self, db):
        """Verify User model instantiation and attribute persistence."""
        hashed_pwd = bcrypt.generate_password_hash('Secr3t!P@ss').decode('utf-8')
        user = User(
            username='AliceRecruiter',
            usertype='Company',
            email='alice@techcorp.com',
            password=hashed_pwd
        )
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == 'AliceRecruiter'
        assert user.usertype == 'Company'
        assert user.email == 'alice@techcorp.com'

    def test_user_repr(self, db):
        """Verify __repr__ string formatting of User."""
        user = User(
            id=42,
            username='repr_user',
            usertype='Job Seeker',
            email='repr@example.com',
            password='hashedpassword'
        )
        assert repr(user) == "User('42', 'repr_user', 'Job Seeker', 'repr@example.com')"

    def test_user_mixin_properties(self, db):
        """Verify Flask-Login UserMixin properties (is_authenticated, is_active, etc.)."""
        user = User(
            username='ActiveSeeker',
            usertype='Job Seeker',
            email='active@seeker.org',
            password='hashedpassword'
        )
        db.session.add(user)
        db.session.commit()

        assert user.is_authenticated is True
        assert user.is_active is True
        assert user.is_anonymous is False
        assert user.get_id() == str(user.id)

    def test_user_password_hashing_and_verification(self, db):
        """Verify bcrypt password hashing and verification."""
        raw_password = 'MySecurePassword2026!'
        hashed = bcrypt.generate_password_hash(raw_password).decode('utf-8')

        user = User(
            username='BcryptUser',
            usertype='Job Seeker',
            email='bcrypt@test.com',
            password=hashed
        )
        db.session.add(user)
        db.session.commit()

        assert bcrypt.check_password_hash(user.password, raw_password) is True
        assert bcrypt.check_password_hash(user.password, 'WrongPassword!') is False

    def test_load_user_helper(self, db):
        """Verify Flask-Login load_user callback fetches correct record."""
        user = User(
            username='LoadedUser',
            usertype='Company',
            email='loaded@example.com',
            password='hashedpassword'
        )
        db.session.add(user)
        db.session.commit()

        loaded = load_user(user.id)
        assert loaded is not None
        assert loaded.username == 'LoadedUser'

        # Non-existent user returns None
        assert load_user(99999) is None

    def test_user_unique_username_constraint(self, db):
        """Verify database enforces unique constraint on User.username."""
        u1 = User(
            username='DuplicateUser',
            usertype='Job Seeker',
            email='u1@test.com',
            password='hash'
        )
        u2 = User(
            username='DuplicateUser',
            usertype='Company',
            email='u2@test.com',
            password='hash'
        )
        db.session.add(u1)
        db.session.commit()

        db.session.add(u2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_user_unique_email_constraint(self, db):
        """Verify database enforces unique constraint on User.email."""
        u1 = User(
            username='EmailUser1',
            usertype='Job Seeker',
            email='same@email.com',
            password='hash'
        )
        u2 = User(
            username='EmailUser2',
            usertype='Company',
            email='same@email.com',
            password='hash'
        )
        db.session.add(u1)
        db.session.commit()

        db.session.add(u2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_user_jobs_and_applications_relationships(self, db):
        """Verify bi-directional relationships with Jobs and Applications."""
        company = User(
            username='CompanyRel',
            usertype='Company',
            email='company_rel@test.com',
            password='hash'
        )
        candidate = User(
            username='CandidateRel',
            usertype='Job Seeker',
            email='cand_rel@test.com',
            password='hash'
        )
        db.session.add_all([company, candidate])
        db.session.commit()

        job = Jobs(
            title='Software Engineer',
            industry='Computer And Technology',
            description='Build scalable web apps',
            job_applier=company
        )
        db.session.add(job)
        db.session.commit()

        application = Application(
            gender='Female',
            degree='cBachelor',
            industry='Computer And Technology',
            experience=2,
            cv='resume.png',
            cover_letter='Cover letter text',
            application_submiter=candidate,
            application_jober=job
        )
        db.session.add(application)
        db.session.commit()

        assert len(company.jobs) == 1
        assert company.jobs[0].title == 'Software Engineer'
        assert len(candidate.applications) == 1
        assert candidate.applications[0].degree == 'cBachelor'


@pytest.mark.unit
class TestJobModel:
    """Unit tests for Jobs model and default values."""

    def test_create_job_success(self, db):
        """Verify Jobs model persistence and attributes."""
        company = User(
            username='JobHostCorp',
            usertype='Company',
            email='host@corp.com',
            password='hash'
        )
        db.session.add(company)
        db.session.commit()

        job = Jobs(
            title='Full Stack Developer',
            industry='Computer And Technology',
            description='Python + Flask + React experience required',
            user_id=company.id
        )
        db.session.add(job)
        db.session.commit()

        assert job.id is not None
        assert job.title == 'Full Stack Developer'
        assert job.industry == 'Computer And Technology'
        assert job.user_id == company.id

    def test_job_repr(self, db):
        """Verify __repr__ string formatting of Jobs."""
        now = datetime.now()
        job = Jobs(
            id=10,
            title='Cloud Architect',
            industry='Telecommunication',
            description='Desc',
            date_posted=now
        )
        assert repr(job) == f"Jobs('10','Cloud Architect', 'Telecommunication', '{now}')"

    def test_job_date_posted_default_is_dynamic(self, db):
        """Verify date_posted default uses callable datetime.now and is generated dynamically."""
        company = User(
            username='DateTesterCorp',
            usertype='Company',
            email='date@corp.com',
            password='hash'
        )
        db.session.add(company)
        db.session.commit()

        before = datetime.now()
        job = Jobs(
            title='DevOps Engineer',
            industry='Energy',
            description='CI/CD pipeline management',
            job_applier=company
        )
        db.session.add(job)
        db.session.commit()
        after = datetime.now()

        assert job.date_posted is not None
        assert isinstance(job.date_posted, datetime)
        assert before <= job.date_posted <= after


@pytest.mark.unit
class TestApplicationModel:
    """Unit tests for Application model."""

    def test_create_application_success(self, db):
        """Verify Application model persistence and attributes."""
        company = User(username='HireCorp', usertype='Company', email='hire@corp.com', password='hash')
        seeker = User(username='SeekerOne', usertype='Job Seeker', email='seeker1@test.com', password='hash')
        db.session.add_all([company, seeker])
        db.session.commit()

        job = Jobs(title='Data Analyst', industry='Healthcare', description='Analyze medical data', job_applier=company)
        db.session.add(job)
        db.session.commit()

        app_record = Application(
            gender='Male',
            degree='bMaster',
            industry='Healthcare',
            experience=5,
            cv='randomhex1234.png',
            cover_letter='I have 5 years experience in health analytics.',
            user_id=seeker.id,
            job_id=job.id
        )
        db.session.add(app_record)
        db.session.commit()

        assert app_record.id is not None
        assert app_record.gender == 'Male'
        assert app_record.degree == 'bMaster'
        assert app_record.experience == 5
        assert app_record.cv == 'randomhex1234.png'
        assert app_record.application_submiter.username == 'SeekerOne'
        assert app_record.application_jober.title == 'Data Analyst'

    def test_application_repr(self, db):
        """Verify __repr__ string formatting of Application."""
        now = datetime.now()
        app_record = Application(
            id=7,
            gender='Others',
            date_posted=now,
            degree='aPHD',
            industry='Aerospace',
            experience=8,
            user_id=3,
            job_id=2
        )
        assert repr(app_record) == f"Application('7','Others', '{now}', 'aPHD', 'Aerospace', '8', '3', '2')"


@pytest.mark.unit
class TestReviewModel:
    """Unit tests for Review model."""

    def test_create_review_success(self, db):
        """Verify Review model persistence."""
        review = Review(
            username='HappyUser',
            review='The application submission process was seamless and intuitive!'
        )
        db.session.add(review)
        db.session.commit()

        assert review.id is not None
        assert review.username == 'HappyUser'
        assert 'seamless' in review.review

    def test_review_repr(self, db):
        """Verify __repr__ string formatting of Review."""
        review = Review(
            username='TestReviewer',
            review='Solid portal.'
        )
        assert repr(review) == "Review('TestReviewer', 'Solid portal.')"

    def test_review_unique_username_constraint(self, db):
        """Verify Review model enforces uniqueness on username in database."""
        r1 = Review(username='UniqueReviewer', review='First review')
        r2 = Review(username='UniqueReviewer', review='Second review attempt')
        db.session.add(r1)
        db.session.commit()

        db.session.add(r2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
