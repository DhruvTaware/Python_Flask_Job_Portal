from flask import render_template, url_for, flash, redirect, request, send_file, abort
from app import app, db, bcrypt
from PIL import Image
import os
import secrets
import random
from app.forms import RegistrationForm, LoginForm, ReviewForm, JobForm, ApplicationForm
from app.models import User, Jobs, Review, Application
from flask_login import login_user, current_user, logout_user, login_required

DEFAULT_REVIEWS = [
    {
        'username': 'Vedant Patil',
        'review': 'I hired multiple people using this website. Thank you'
    },
    {
        'username': 'Neha Thakare',
        'review': 'It could be better'
    },
    {
        'username': 'Dhruv Taware',
        'review': 'Best website ever'
    }
]


def get_random_reviews():
    try:
        review_objs = Review.query.all()
        if len(review_objs) < 3:
            return DEFAULT_REVIEWS
        return random.sample(review_objs, 3)
    except Exception:
        return DEFAULT_REVIEWS


@app.context_processor
def inject_random_reviews():
    return dict(Random_Review=get_random_reviews())


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext.lower()
    picture_path = os.path.join(app.root_path, 'static', picture_fn)
    form_picture.save(picture_path)
    return picture_fn


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.usertype == 'Job Seeker':
            return redirect(url_for('show_jobs'))
        elif current_user.usertype == 'Company':
            return redirect(url_for('posted_jobs'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            usertype=form.usertype.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, Random_Review=get_random_reviews())


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.usertype == 'Job Seeker':
            return redirect(url_for('show_jobs'))
        elif current_user.usertype == 'Company':
            return redirect(url_for('posted_jobs'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if form.usertype.data == user.usertype and form.usertype.data == 'Company':
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('posted_jobs'))
            elif form.usertype.data == user.usertype and form.usertype.data == 'Job Seeker':
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('show_jobs'))
            else:
                flash('Login Unsuccessful. Please check email, password and usertype', 'danger')
        else:
            flash('Login Unsuccessful. Please check email, password and usertype', 'danger')
            return render_template('login.html', form=form, Random_Review=get_random_reviews())
    return render_template('login.html', form=form, Random_Review=get_random_reviews())


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('show_jobs'))


@app.route("/post_cvs/<jobid>", methods=['GET', 'POST'])
@login_required
def post_cvs(jobid):
    if current_user.usertype != 'Job Seeker':
        flash('Only job seekers can apply for jobs.', 'warning')
        return redirect(url_for('show_jobs'))
    job = db.session.get(Jobs, int(jobid))
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('show_jobs'))
    form = ApplicationForm()
    if form.validate_on_submit():
        if not form.cv.data:
            flash('Please upload your resume file.', 'danger')
            return render_template('post_cvs.html', form=form, Random_Review=get_random_reviews())
        picture_file = save_picture(form.cv.data)
        application = Application(
            gender=form.gender.data,
            degree=form.degree.data,
            industry=form.industry.data,
            experience=form.experience.data,
            cover_letter=form.cover_letter.data,
            application_submiter=current_user,
            application_jober=job,
            cv=picture_file
        )
        db.session.add(application)
        db.session.commit()
        flash('Your application has been submitted successfully!', 'success')
        return redirect(url_for('show_jobs'))
    return render_template('post_cvs.html', form=form, Random_Review=get_random_reviews())


@app.route("/post_jobs", methods=['GET', 'POST'])
@login_required
def post_jobs():
    if current_user.usertype != 'Company':
        flash('Only registered companies can post job openings.', 'warning')
        return redirect(url_for('show_jobs'))
    form = JobForm()
    if form.validate_on_submit():
        job = Jobs(
            title=form.title.data,
            industry=form.industry.data,
            description=form.description.data,
            job_applier=current_user
        )
        db.session.add(job)
        db.session.commit()
        flash('Job opening has been posted successfully!', 'success')
        return redirect(url_for('posted_jobs'))
    return render_template('post_jobs.html', form=form, Random_Review=get_random_reviews())


@app.route("/review", methods=['GET', 'POST'])
@login_required
def review():
    form = ReviewForm()
    if form.validate_on_submit():
        existing_review = Review.query.filter_by(username=form.username.data).first()
        if existing_review:
            existing_review.review = form.review.data
        else:
            new_review = Review(username=form.username.data, review=form.review.data)
            db.session.add(new_review)
        db.session.commit()
        flash('Thank you for providing the review!', 'success')
        return redirect(url_for('show_jobs'))
    return render_template('review.html', form=form, Random_Review=get_random_reviews())


@app.route("/posted_jobs")
@login_required
def posted_jobs():
    if current_user.usertype != 'Company':
        flash('Only companies can access posted jobs management.', 'warning')
        return redirect(url_for('show_jobs'))
    jobs = Jobs.query.filter_by(user_id=current_user.id).all()
    return render_template('show_jobs.html', jobs=jobs, Random_Review=get_random_reviews())


@app.route("/show_applications/<jobid>", methods=['GET'])
@login_required
def show_applications(jobid):
    if current_user.usertype != 'Company':
        flash('Access denied. Only company accounts can view applicants.', 'danger')
        return redirect(url_for('show_jobs'))
    job = db.session.get(Jobs, int(jobid))
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('posted_jobs'))
    if job.user_id != current_user.id:
        flash('Access denied. You can only view applications for jobs posted by your company.', 'danger')
        return redirect(url_for('posted_jobs'))
    applications = Application.query.filter_by(job_id=job.id).order_by(
        Application.degree, Application.experience.desc()
    ).all()
    return render_template('show_applications.html', applications=applications, Random_Review=get_random_reviews())


@app.route("/meeting/<application_id>")
@login_required
def meeting(application_id):
    application = db.session.get(Application, int(application_id))
    if not application:
        flash('Interview meeting not found.', 'danger')
        return redirect(url_for('show_jobs'))
    job = db.session.get(Jobs, application.job_id)
    is_applicant = (application.user_id == current_user.id)
    is_employer = (job and job.user_id == current_user.id)
    if not (is_applicant or is_employer):
        flash('Access denied. You do not have permission to join this interview.', 'danger')
        return redirect(url_for('show_jobs'))
    applicant = db.session.get(User, application.user_id)
    return render_template('meeting.html', applicant=applicant, Random_Review=get_random_reviews())


@app.route("/")
@app.route("/show_jobs")
def show_jobs():
    jobs = Jobs.query.all()
    return render_template('show_jobs.html', jobs=jobs, Random_Review=get_random_reviews())


@app.route("/resume/<id>", methods=['GET'])
@login_required
def resume(id):
    application = db.session.get(Application, int(id))
    if not application:
        flash('Resume or application not found.', 'danger')
        return redirect(url_for('show_jobs'))
    job = db.session.get(Jobs, application.job_id)
    is_applicant = (application.user_id == current_user.id)
    is_employer = (job and job.user_id == current_user.id)
    if not (is_applicant or is_employer):
        flash('Access denied. You do not have permission to view this resume.', 'danger')
        return redirect(url_for('show_jobs'))
    cv = application.cv
    return render_template('resume.html', cv=cv, Random_Review=get_random_reviews(), id=id)
