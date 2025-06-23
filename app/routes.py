from flask import render_template, url_for, flash, redirect, request, send_file
from app import app, db, bcrypt
from PIL import Image
import os
import secrets
from app.forms import RegistrationForm, LoginForm, ReviewForm, JobForm, ApplicationForm
from app.models import User, Jobs, Review, Application
from flask_login import login_user, current_user, logout_user, login_required
from flask import abort
import random
import requests
from app.email_utils import send_email

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

def fetch_api_jobs(keyword, location, industry):
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'what': keyword,
        'where': location,
        'category': industry,
        'results_per_page': 10,
        'content-type': 'application/json'
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        api_jobs = []
        for job in data.get('results', []):
            api_jobs.append({
                'title': job.get('title', 'N/A'),
                'company': job.get('company', {}).get('display_name', 'Unknown'),
                'location': job.get('location', {}).get('display_name', 'N/A'),
                'description': job.get('description', '')[:200],
                'salary': job.get('salary_is_predicted', '0') == '1' and "(Predicted)" or "",
                'redirect_url': job.get('redirect_url')
            })
        return api_jobs
    except Exception as e:
        print("Error fetching API jobs:", e)
        return []

def save_resume(form_file):
    _, f_ext = os.path.splitext(form_file.filename)
    random_hex = secrets.token_hex(8)
    resume_fn = random_hex + f_ext

    resume_folder = os.path.join(app.root_path, 'static', 'resume')
    os.makedirs(resume_folder, exist_ok=True)

    resume_path = os.path.join(resume_folder, resume_fn)
    form_file.save(resume_path)

    return resume_fn







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
        user = User(username=form.username.data, usertype=form.usertype.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        send_email(
            to_email=form.email.data,
            subject="🎉 Welcome to Job Portal!",
            body_html=f"""
            <h2>Welcome {form.username.data},</h2>
            <p>We're excited to have you on board. Start applying and explore your dream job today!</p>
            <p>🚀 Skills You Can Explore: API, Flask, HTML, CSS, Bootstrap</p>
            <p>— Team Job Portal</p>
            """
        )

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.usertype == 'Job Seeker':
            return redirect(url_for('show_jobs'))
        elif current_user.usertype == 'Company':
            return redirect(url_for('posted_jobs'))
        elif current_user.is_admin:  
            return redirect(url_for('admin_dashboard')) 

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if form.usertype.data == 'Admin' and user.is_admin:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('admin_dashboard'))  
            elif form.usertype.data == user.usertype:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else (
                    redirect(url_for('posted_jobs')) if user.usertype == 'Company'
                    else redirect(url_for('show_jobs'))
                )
            else:
                flash('Login Unsuccessful. Please check email, password, and user type', 'danger')
        else:
            flash('Login Unsuccessful. Please check email, password, and user type', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('show_jobs'))

def save_picture(form_picture):
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = f_name + f_ext
    picture_path = os.path.join(app.root_path, 'static', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route("/post_cvs/<jobid>", methods=['GET', 'POST'])
@login_required
def post_cvs(jobid):
    form = ApplicationForm()
    job = Jobs.query.filter_by(id=jobid).first()

    if form.validate_on_submit():
        cv_filename = save_resume(form.cv.data)
        application = Application(
            gender=form.gender.data,
            degree=form.degree.data,
            industry=form.industry.data,
            experience=form.experience.data,
            cover_letter=form.cover_letter.data,
            application_submiter=current_user,
            application_jober=job,
            cv=cv_filename
        )
        db.session.add(application)
        db.session.commit()

        flash("Your application has been submitted!", "success")
        return redirect(url_for('show_jobs'))

    return render_template('post_cvs.html', form=form)

@app.route("/post_jobs", methods=['GET', 'POST'])
@login_required
def post_jobs():
    form = JobForm()
    if form.validate_on_submit():
        job = Jobs(title=form.title.data,
                   industry=form.industry.data,
                   description=form.description.data,
                   salary=form.salary.data,
                   location=form.location.data,  # ✅ Added location field
                   company=current_user)
        db.session.add(job)
        db.session.commit()
        return redirect(url_for('posted_jobs'))
    return render_template('post_jobs.html', form=form)

@app.route("/review", methods=['GET', 'POST'])
@login_required
def review():
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(username=form.username.data, review=form.review.data)
        db.session.add(review)
        db.session.commit()
        flash('Thank you for providing the review!', 'success')
        return redirect(url_for('show_jobs'))
    return render_template('review.html', form=form)

@app.route("/posted_jobs")
@login_required
def posted_jobs():
    jobs = Jobs.query.filter_by(company=current_user).all()

    return render_template('show_jobs.html', jobs=jobs)

@app.route("/show_applications/<jobid>", methods=['GET', 'POST'])
@login_required
def show_applications(jobid):
    job = Jobs.query.get_or_404(jobid)
    if job.company != current_user:
        abort(403)

    applications = Application.query.filter_by(job_id=jobid).order_by(Application.degree, Application.experience.desc()).all()
    return render_template('show_applications.html', applications=applications, job=job)


@app.route("/my_applications")
@login_required
def my_applications():
    if current_user.usertype != 'Job Seeker':
        abort(403)
    applications = Application.query.filter_by(user_id=current_user.id).all()
    return render_template("my_applications.html", applications=applications)

@app.route("/reject_application/<int:application_id>", methods=['POST'])
@login_required
def reject_application(application_id):
    application = Application.query.get_or_404(application_id)
    job = application.application_jober
    if job.company != current_user:
        abort(403)

    application.status = 'Rejected'
    db.session.commit()

    # ✅ Send rejection email to applicant
    send_email(
        to_email=application.application_submiter.email,
        subject=f"Update on Your Application for {job.title}",
        body_html=f"""
        <h3>Dear {application.application_submiter.username},</h3>
        <p>Thank you for applying to <strong>{job.title}</strong> at <strong>{job.company.username}</strong>.</p>
        <p>We appreciate your interest, but unfortunately, your application was not selected this time.</p>
        <p>💡 Keep improving and never give up. Your dream job awaits!</p>
        <p>— Job Portal Team</p>
        """
    )

    flash("Application rejected successfully.", "warning")
    return redirect(url_for('show_applications', jobid=job.id))


@app.route("/delete_application/<int:application_id>", methods=['POST'])
@login_required
def delete_application(application_id):
    application = Application.query.get_or_404(application_id)
    job = application.application_jober
    if job.company != current_user:
        abort(403)

    db.session.delete(application)
    db.session.commit()
    flash("Application deleted successfully.", "danger")
    return redirect(url_for('show_applications', jobid=job.id))


@app.route("/")
@app.route("/show_jobs")
def show_jobs():
    keyword = request.args.get('keyword', '').strip()
    location = request.args.get('location', '').strip()
    industry = request.args.get('industry', '').strip()

    # Local DB Jobs
    jobs_query = Jobs.query
    if keyword:
        jobs_query = jobs_query.filter(Jobs.title.ilike(f"%{keyword}%"))
    if location:
        jobs_query = jobs_query.filter(Jobs.location == location)
    if industry:
        jobs_query = jobs_query.filter(Jobs.industry == industry)

    local_jobs = jobs_query.all()

    # Adzuna API Jobs
    api_jobs = []
    try:
        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_APP_KEY,
            'results_per_page': 6,
            'content-type': 'application/json'
        }

        if keyword:
            params['what'] = keyword
        if location:
            params['where'] = location
        if industry:
            params['category'] = industry

        response = requests.get(url, params=params)
        data = response.json()

        for job in data.get("results", []):
            api_jobs.append({
                'title': job.get('title', 'N/A'),
                'company': job.get('company', {}).get('display_name', 'N/A'),
                'location': job.get('location', {}).get('display_name', 'N/A'),
                'salary': f"{job.get('salary_min', 0):,.0f} - {job.get('salary_max', 0):,.0f}" if job.get('salary_min') else "Not disclosed",
                'description': job.get('description', '')[:150],
                'redirect_url': job.get('redirect_url', '#')
            })

    except Exception as e:
        print("Adzuna API Error:", e)

    return render_template('show_jobs.html', jobs=local_jobs, api_jobs=api_jobs)




@app.route("/resume/<id>", methods=['GET'])
def resume(id):
    cv = Application.query.get(int(id)).cv
    return render_template('resume.html', cv=cv, id=id)

@app.route("/download_resume/<filename>")
def download_resume(filename):
    resume_path = os.path.join(app.root_path, 'static', 'resume', filename)
    if os.path.exists(resume_path):
        return send_file(resume_path, as_attachment=True)
    else:
        flash('Resume file not found.', 'danger')
        return redirect(url_for('show_jobs'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access Denied!', 'danger')
        return redirect(url_for('login'))

    job_seekers = User.query.filter_by(usertype='Job Seeker').all()
    companies = User.query.filter_by(usertype='Company').all()
    jobs = Jobs.query.all()

    return render_template(
        'admin_dashboard.html',
        job_seekers=job_seekers,
        companies=companies,
        jobs=jobs
    )

@app.route("/delete_user/<int:user_id>", methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access Denied.', 'danger')
        return redirect(url_for('show_jobs'))

    user = User.query.get_or_404(user_id)

    # Delete job seeker applications
    for app_obj in user.applications:
        db.session.delete(app_obj)

    # If the user is a Company, delete jobs and their applications
    if user.usertype == 'Company':
        for job_obj in user.posted_jobs:  # corrected backref name
            for app_obj in job_obj.applications:
                db.session.delete(app_obj)
            db.session.delete(job_obj)

    db.session.delete(user)
    db.session.commit()
    flash('User and all related data deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route("/delete_job/<int:job_id>", methods=['POST'])
@login_required
def delete_job(job_id):
    job = Jobs.query.get_or_404(job_id)

    # Check if the current user is allowed to delete the job
    if not current_user.is_admin and job.user_id != current_user.id:
        flash('Access Denied: You are not allowed to delete this job.', 'danger')
        return redirect(url_for('show_jobs'))

    # Delete related applications
    for app_obj in job.applications:
        db.session.delete(app_obj)

    # Delete the job itself
    db.session.delete(job)
    db.session.commit()
    flash('Job and all related applications deleted successfully.', 'success')

    # Redirect appropriately
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('posted_jobs'))



