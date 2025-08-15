from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import pandas as pd
from datetime import datetime
import uuid
from utils.resume_parser import ResumeParser
from utils.skill_extractor import SkillExtractor
from utils.semantic_matcher import SemanticMatcher
from utils.job_recommendations import JobRecommendationEngine
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_screening.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='hr')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)  # JSON string
    experience_level = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    skills = db.Column(db.Text)  # JSON string
    experience = db.Column(db.Text)  # JSON string
    education = db.Column(db.Text)  # JSON string
    raw_text = db.Column(db.Text)
    match_score = db.Column(db.Float, default=0)
    matched_skills = db.Column(db.Text)  # JSON string
    skill_gaps = db.Column(db.Text)  # JSON string
    semantic_score = db.Column(db.Float, default=0)
    job_id = db.Column(db.Integer, db.ForeignKey('job_description.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    job_descriptions = JobDescription.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', job_descriptions=job_descriptions)

@app.route('/create_job', methods=['GET', 'POST'])
@login_required
def create_job():
    if request.method == 'POST':
        data = request.get_json()
        
        # Extract skills from job description
        extracted_skills = SkillExtractor.extract_skills_from_jd(data['description'])
        all_skills = list(set(data.get('required_skills', []) + extracted_skills))
        
        job = JobDescription(
            title=data['title'],
            company=data['company'],
            description=data['description'],
            required_skills=json.dumps(all_skills),
            experience_level=data['experience_level'],
            location=data.get('location', ''),
            user_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        
        return jsonify({'success': True, 'job_id': job.id})
    
    return render_template('create_job.html')

@app.route('/upload_resumes/<int:job_id>', methods=['POST'])
@login_required
def upload_resumes(job_id):
    job = JobDescription.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    files = request.files.getlist('resumes')
    results = []
    
    for file in files:
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse resume
            resume_text = ResumeParser.extract_text_from_pdf(filepath)
            parsed_data = ResumeParser.parse_resume(resume_text, filename)
            
            # Calculate match scores
            required_skills = json.loads(job.required_skills)
            match_score = ResumeParser.calculate_match_score(parsed_data, required_skills)
            skill_analysis = ResumeParser.analyze_skill_gap(parsed_data, required_skills)
            semantic_analysis = SemanticMatcher.semantic_match(resume_text, job.description)
            
            # Save to database
            resume = Resume(
                filename=filename,
                name=parsed_data.get('name', ''),
                email=parsed_data.get('email', ''),
                phone=parsed_data.get('phone', ''),
                skills=json.dumps(parsed_data.get('skills', [])),
                experience=json.dumps(parsed_data.get('experience', [])),
                education=json.dumps(parsed_data.get('education', [])),
                raw_text=resume_text,
                match_score=max(match_score, semantic_analysis['similarity_score']),
                matched_skills=json.dumps(skill_analysis['matched']),
                skill_gaps=json.dumps(skill_analysis['missing']),
                semantic_score=semantic_analysis['similarity_score'],
                job_id=job_id,
                user_id=current_user.id
            )
            db.session.add(resume)
            results.append({
                'filename': filename,
                'name': parsed_data.get('name', ''),
                'match_score': resume.match_score
            })
    
    db.session.commit()
    return jsonify({'success': True, 'results': results})

@app.route('/job_results/<int:job_id>')
@login_required
def job_results(job_id):
    job = JobDescription.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    resumes = Resume.query.filter_by(job_id=job_id).order_by(Resume.match_score.desc()).all()
    
    # Prepare data for charts
    resume_data = []
    for resume in resumes:
        resume_data.append({
            'id': resume.id,
            'name': resume.name or resume.filename,
            'email': resume.email,
            'match_score': resume.match_score,
            'semantic_score': resume.semantic_score,
            'matched_skills': json.loads(resume.matched_skills or '[]'),
            'skill_gaps': json.loads(resume.skill_gaps or '[]'),
            'skills': json.loads(resume.skills or '[]')
        })
    
    return render_template('job_results.html', job=job, resumes=resume_data)

@app.route('/resume_details/<int:resume_id>')
@login_required
def resume_details(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    job = JobDescription.query.get(resume.job_id)
    
    # Generate job recommendations
    resume_data = {
        'skills': json.loads(resume.skills or '[]'),
        'experience': json.loads(resume.experience or '[]'),
        'education': json.loads(resume.education or '[]')
    }
    
    recommendations = JobRecommendationEngine.generate_recommendations(resume_data)
    feedback = JobRecommendationEngine.generate_feedback(
        resume_data, 
        json.loads(job.required_skills) if job else []
    )
    
    return jsonify({
        'resume': {
            'name': resume.name,
            'email': resume.email,
            'phone': resume.phone,
            'skills': json.loads(resume.skills or '[]'),
            'experience': json.loads(resume.experience or '[]'),
            'education': json.loads(resume.education or '[]'),
            'match_score': resume.match_score,
            'semantic_score': resume.semantic_score,
            'matched_skills': json.loads(resume.matched_skills or '[]'),
            'skill_gaps': json.loads(resume.skill_gaps or '[]')
        },
        'job': {
            'title': job.title if job else '',
            'company': job.company if job else '',
            'required_skills': json.loads(job.required_skills) if job else []
        },
        'recommendations': recommendations,
        'feedback': feedback
    })

@app.route('/export_csv/<int:job_id>')
@login_required
def export_csv(job_id):
    job = JobDescription.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    resumes = Resume.query.filter_by(job_id=job_id).order_by(Resume.match_score.desc()).all()
    
    data = []
    for resume in resumes:
        data.append({
            'Name': resume.name or resume.filename,
            'Email': resume.email or '',
            'Phone': resume.phone or '',
            'Match Score': f"{resume.match_score:.1f}%",
            'Semantic Score': f"{resume.semantic_score:.1f}%",
            'Matched Skills': '; '.join(json.loads(resume.matched_skills or '[]')),
            'Missing Skills': '; '.join(json.loads(resume.skill_gaps or '[]')),
            'Total Skills': len(json.loads(resume.skills or '[]'))
        })
    
    df = pd.DataFrame(data)
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Convert to bytes
    csv_data = io.BytesIO()
    csv_data.write(output.getvalue().encode('utf-8'))
    csv_data.seek(0)
    
    return send_file(
        csv_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'resume_analysis_{job.title}_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@app.route('/skill_analysis_chart/<int:job_id>')
@login_required
def skill_analysis_chart(job_id):
    job = JobDescription.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    resumes = Resume.query.filter_by(job_id=job_id).all()
    
    # Prepare chart data
    chart_data = {
        'match_scores': [resume.match_score for resume in resumes],
        'names': [resume.name or resume.filename for resume in resumes],
        'skill_categories': {},
        'top_skills': {}
    }
    
    # Analyze skill categories
    all_skills = []
    for resume in resumes:
        skills = json.loads(resume.skills or '[]')
        all_skills.extend(skills)
    
    # Count skill frequency
    from collections import Counter
    skill_counts = Counter(all_skills)
    chart_data['top_skills'] = dict(skill_counts.most_common(10))
    
    return jsonify(chart_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)