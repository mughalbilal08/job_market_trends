from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import logging
import os
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
server = os.getenv("DB_SERVER")
dbname = os.getenv("DB_NAME")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://{user}:{password}@{server}/{dbname}?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'SimpleCache'
db = SQLAlchemy(app)
cache = Cache(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    skills = db.Column(db.String(200), nullable=True)
    saved_jobs = db.relationship('SavedJob', backref='user', lazy=True)

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.BigInteger, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    remote_allowed = db.Column(db.Boolean, default=False)
    experience_level = db.Column(db.String(50), nullable=True)
    skills_desc = db.Column(db.Text, nullable=True)

# Initialize database and load jobs
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    top_jobs = Job.query.limit(5).all()
    top_jobs_data = [{
        'job_id': job.job_id,
        'title': job.title,
        'company_name': job.company_name,
        'location': job.location,
        'remote_allowed': job.remote_allowed
    } for job in top_jobs]
    return render_template('index.html', top_jobs=top_jobs_data)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            flash('Password must be 8+ characters with uppercase and digit.', 'error')
            return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('signup'))
        user = User(email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            logger.info(f"User {email} logged in successfully")
            return redirect(url_for('dashboard', page=1, active_section='home'))
        flash('Invalid credentials.', 'error')
        logger.warning(f"Failed login attempt for {email}")
    return render_template('login.html')

@app.route('/dashboard/<int:page>', methods=['GET', 'POST'])
def dashboard(page=1):
    if 'user_id' not in session:
        logger.warning("Unauthorized access to /dashboard")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    saved_jobs = SavedJob.query.filter_by(user_id=user.id).all()
    saved_job_ids = [int(sj.job_id) for sj in saved_jobs]
    logger.info(f"Saved job IDs for user {user.id}: {saved_job_ids}")
    per_page = 50
    query = Job.query
    active_section = request.args.get('active_section', 'home')
    saved_jobs_data = []
    if saved_job_ids:
        saved_query = Job.query.filter(Job.job_id.in_(saved_job_ids))
        saved_jobs_data = [{
            'job_id': job.job_id,
            'title': job.title,
            'company_name': job.company_name,
            'location': job.location,
            'remote_allowed': job.remote_allowed,
            'experience_level': job.experience_level,
            'skills_desc': job.skills_desc
        } for job in saved_query.all()]
    logger.info(f"Saved jobs data for user {user.id}: {saved_jobs_data}")
    if request.method == 'POST':
        active_section = request.form.get('active_section', 'search')
        if 'show_available' not in request.form:
            skill = request.form.get('skill', '').lower().strip()
            location = request.form.get('location', '').lower().strip()
            job_type = request.form.get('job_type', '')
            experience = request.form.get('experience', '')
            logger.info(f"Search query received: skill={skill}, location={location}, job_type={job_type}, experience={experience}")
            if skill:
                query = query.filter(Job.skills_desc.ilike(f'%{skill}%'))
                logger.debug(f"Applied skill filter: {skill}")
            if location:
                query = query.filter(Job.location.ilike(f'%{location}%'))
                logger.debug(f"Applied location filter: {location}")
            if job_type:
                query = query.filter(Job.remote_allowed == (job_type == 'remote'))
                logger.debug(f"Applied job_type filter: {job_type}")
            if experience and experience.lower() != 'all experience levels':
                query = query.filter(Job.experience_level.ilike(experience))
                logger.debug(f"Applied experience filter: {experience}")
            logger.debug(f"Executing query: {str(query)}")
            pagination = query.order_by(Job.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
            jobs_data = [{
                'job_id': job.job_id,
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'remote_allowed': job.remote_allowed,
                'experience_level': job.experience_level,
                'skills_desc': job.skills_desc
            } for job in pagination.items]
            logger.info(f"Search returned {len(jobs_data)} jobs")
            if jobs_data:
                logger.info(f"Full job results: {jobs_data}")
                logger.debug(f"Sample job: {jobs_data[0]}")
    else:
        pagination = query.order_by(Job.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        jobs_data = [{
            'job_id': job.job_id,
            'title': job.title,
            'company_name': job.company_name,
            'location': job.location,
            'remote_allowed': job.remote_allowed,
            'experience_level': job.experience_level,
            'skills_desc': job.skills_desc
        } for job in pagination.items]
    return render_template('dashboard.html', jobs=jobs_data, saved_jobs=saved_jobs_data, saved_job_ids=saved_job_ids, user=user, no_jobs=len(jobs_data) == 0, active_section=active_section, pagination=pagination, page=page)

@app.route('/save_job/<job_id>', methods=['POST'])
def save_job(job_id):
    if 'user_id' not in session:
        logger.warning("Unauthorized access to /save_job")
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    user_id = session['user_id']
    existing_job = SavedJob.query.filter_by(user_id=user_id, job_id=int(job_id)).first()
    if not existing_job:
        try:
            saved_job = SavedJob(job_id=int(job_id), user_id=user_id)
            db.session.add(saved_job)
            db.session.commit()
            logger.info(f"Job {job_id} saved for user {user_id}")
            return jsonify({'success': True, 'message': 'Job saved successfully!'})
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving job {job_id} for user {user_id}: {e}")
            return jsonify({'success': False, 'message': f'Failed to save job: {str(e)}'}), 500
    else:
        logger.info(f"Job {job_id} already saved for user {user_id}")
        return jsonify({'success': False, 'message': 'Job already saved.'}), 400

@app.route('/unsave_job/<job_id>', methods=['POST'])
def unsave_job(job_id):
    if 'user_id' not in session:
        logger.warning("Unauthorized access to /unsave_job")
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    user_id = session['user_id']
    saved_job = SavedJob.query.filter_by(user_id=user_id, job_id=int(job_id)).first()
    if saved_job:
        try:
            db.session.delete(saved_job)
            db.session.commit()
            logger.info(f"Job {job_id} unsaved for user {user_id}")
            return jsonify({'success': True, 'message': 'Job unsaved successfully!'})
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error unsaving job {job_id} for user {user_id}: {e}")
            return jsonify({'success': False, 'message': f'Failed to unsave job: {str(e)}'}), 500
    else:
        logger.info(f"Job {job_id} not found in saved jobs for user {user_id}")
        return jsonify({'success': False, 'message': 'Job not found in saved jobs.'}), 400

@app.route('/saved_jobs/<int:page>')
def saved_jobs(page=1):
    if 'user_id' not in session:
        logger.warning("Unauthorized access to /saved_jobs")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    per_page = 50
    saved_jobs = SavedJob.query.filter_by(user_id=user.id)
    saved_job_ids = [int(sj.job_id) for sj in saved_jobs.all()]
    logger.info(f"Saved job IDs for user {user.id}: {saved_job_ids}")
    if saved_job_ids:
        query = Job.query.filter(Job.job_id.in_(saved_job_ids))
        pagination = query.order_by(Job.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        saved_jobs_data = [{
            'job_id': job.job_id,
            'title': job.title,
            'company_name': job.company_name,
            'location': job.location,
            'remote_allowed': job.remote_allowed,
            'experience_level': job.experience_level,
            'skills_desc': job.skills_desc
        } for job in pagination.items]
    else:
        saved_jobs_data = []
        pagination = type('obj', (), {'has_prev': False, 'has_next': False, 'prev_num': 0, 'next_num': 0, 'iter_pages': lambda: []})()
    logger.info(f"Saved jobs data for user {user.id}: {saved_jobs_data}")
    return render_template('saved_jobs.html', saved_jobs=saved_jobs_data, saved_job_ids=saved_job_ids, pagination=pagination, page=page, active_section='saved')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        logger.warning("Unauthorized access to /profile")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.skills = request.form.get('skills')
        db.session.commit()
        flash('Profile updated.', 'success')
        logger.info(f"Profile updated for user {user.id}")
    return render_template('dashboard.html', user=user, profile=True, active_section='profile')

@app.route('/logout')
def logout():
    logger.info(f"User {session.get('user_id')} logged out")
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/trends')
def trends():
    if 'user_id' not in session:
        logger.warning("Unauthorized access to /trends")
        return redirect(url_for('login'))
    return redirect(url_for('dashboard', page=1, active_section='trends'))

@app.route('/data/<filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

if __name__ == '__main__':
    app.run(debug=True)