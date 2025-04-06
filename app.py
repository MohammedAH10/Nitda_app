from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3
import os

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
app.config['DATABASE'] = 'nitda_portal.db'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database setup
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db_connection()
        with open('schema.sql') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

# User model for Login
class User(UserMixin):
    def __init__(self, id, email, password_hash, user_type, is_admin=False):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.user_type = user_type
        self.is_admin = is_admin

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return User(
                id=user['id'],
                email=user['email'],
                password_hash=user['password_hash'],
                user_type=user['user_type'],
                is_admin=bool(user['is_admin'])
            )
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type'] 
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user:
            flash('Email already exists')
            conn.close()
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)
        
        conn.execute(
            'INSERT INTO users (email, password_hash, user_type, created_at) VALUES (?, ?, ?, ?)',
            (email, password_hash, user_type, datetime.now())
        )
        conn.commit()
        
        # Fetch the newly created user
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        # Create user profile
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO profiles (user_id, created_at) VALUES (?, ?)',
            (user['id'], datetime.now())
        )
        conn.commit()
        conn.close()
        
        flash('Account created successfully. Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(
                id=user['id'],
                email=user['email'],
                password_hash=user['password_hash'],
                user_type=user['user_type'],
                is_admin=bool(user['is_admin'])
            )
            login_user(user_obj)
            
            next_page = request.args.get('next')
            if not next_page or url_for('index') not in next_page:
                next_page = url_for('dashboard')
            
            return redirect(next_page)
        
        flash('Invalid email or password')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user profile and application data
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM profiles WHERE user_id = ?', (current_user.id,)).fetchone()
    
    applications = conn.execute(
        'SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC', 
        (current_user.id,)
    ).fetchall()
    
    # Calculate profile completion percentage
    completion_percentage = 0
    if profile:
        fields = ['full_name', 'phone', 'address', 'institution', 'course', 'graduation_date']
        completed_fields = sum(1 for field in fields if profile[field] is not None)
        completion_percentage = int((completed_fields / len(fields)) * 100)
    
    conn.close()
    
    return render_template(
        'dashboard.html',
        profile=profile,
        applications=applications,
        completion_percentage=completion_percentage
    )

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM profiles WHERE user_id = ?', (current_user.id,)).fetchone()
    
    if request.method == 'POST':
        # Update profile information
        full_name = request.form['full_name']
        phone = request.form['phone']
        address = request.form['address']
        institution = request.form['institution']
        course = request.form['course']
        graduation_date = request.form['graduation_date']
        
        conn.execute(
            '''UPDATE profiles SET 
               full_name = ?, phone = ?, address = ?, institution = ?, 
               course = ?, graduation_date = ?, updated_at = ? 
               WHERE user_id = ?''',
            (full_name, phone, address, institution, course, graduation_date, datetime.now(), current_user.id)
        )
        conn.commit()
        flash('Profile updated successfully')
        return redirect(url_for('profile'))
    
    conn.close()
    return render_template('profile.html', profile=profile)

@app.route('/documents', methods=['GET', 'POST'])
@login_required
def documents():
    if request.method == 'POST':
        document_type = request.form['document_type']
        document = request.files['document']
        
        if document:
            filename = secure_filename(f"{current_user.id}_{document_type}_{document.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            document.save(filepath)
            
            # Save document infomation to database
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO documents (user_id, document_type, filename, uploaded_at) VALUES (?, ?, ?, ?)',
                (current_user.id, document_type, filename, datetime.now())
            )
            conn.commit()
            conn.close()
            
            flash('Document uploaded successfully')
            return redirect(url_for('documents'))
    
    # Get user's documents
    conn = get_db_connection()
    documents = conn.execute(
        'SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC',
        (current_user.id,)
    ).fetchall()
    conn.close()
    
    return render_template('documents.html', documents=documents)

@app.route('/application', methods=['GET', 'POST'])
@login_required
def application():
    if request.method == 'POST':
        application_type = request.form['application_type']
        placement_preference = request.form['placement_preference']
        start_date = request.form['start_date']
        duration = request.form['duration']
        additional_info = request.form['additional_info']
        
        # Check if all required documents are uploaded
        conn = get_db_connection()
        documents = conn.execute(
            'SELECT document_type FROM documents WHERE user_id = ?',
            (current_user.id,)
        ).fetchall()
        document_types = [doc['document_type'] for doc in documents]
        
        required_docs = []
        if application_type == 'siwes':
            required_docs = ['school_id', 'introduction_letter', 'transcript']
        else:  # nysc
            required_docs = ['nysc_callup_letter', 'state_code', 'degree_certificate', 'valid_id']
        
        missing_docs = [doc for doc in required_docs if doc not in document_types]
        
        if missing_docs:
            flash(f"Missing required documents: {', '.join(missing_docs)}")
            conn.close()
            return redirect(url_for('documents'))
        
        # Save application
        conn.execute(
            '''INSERT INTO applications 
               (user_id, application_type, placement_preference, start_date, 
                duration, additional_info, status, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (current_user.id, application_type, placement_preference, start_date, 
             duration, additional_info, 'pending', datetime.now())
        )
        conn.commit()
        conn.close()
        
        flash('Application submitted successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('application.html', user_type=current_user.user_type)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    applications = conn.execute(
        '''SELECT a.*, u.email, p.full_name 
           FROM applications a
           JOIN users u ON a.user_id = u.id
           JOIN profiles p ON a.user_id = p.user_id
           ORDER BY a.created_at DESC'''
    ).fetchall()
    
    # Get statistics
    siwes_count = conn.execute("SELECT COUNT(*) FROM applications WHERE application_type = 'siwes'").fetchone()[0]
    nysc_count = conn.execute("SELECT COUNT(*) FROM applications WHERE application_type = 'nysc'").fetchone()[0]
    pending_count = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'pending'").fetchone()[0]
    approved_count = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'approved'").fetchone()[0]
    
    conn.close()
    
    return render_template(
        'admin/dashboard.html',
        applications=applications,
        stats={
            'siwes': siwes_count,
            'nysc': nysc_count,
            'pending': pending_count,
            'approved': approved_count
        }
    )

@app.route('/admin/application/<int:app_id>', methods=['GET', 'POST'])
@login_required
def admin_application(app_id):
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        status = request.form['status']
        feedback = request.form['feedback']
        
        conn = get_db_connection()
        conn.execute(
            'UPDATE applications SET status = ?, feedback = ?, updated_at = ? WHERE id = ?',
            (status, feedback, datetime.now(), app_id)
        )
        conn.commit()
        
        # Get user email for notification
        application = conn.execute(
            'SELECT u.email FROM applications a JOIN users u ON a.user_id = u.id WHERE a.id = ?',
            (app_id,)
        ).fetchone()
        
        conn.close()
        
        flash('Application updated successfully')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    application = conn.execute(
        '''SELECT a.*, u.email, p.* 
           FROM applications a
           JOIN users u ON a.user_id = u.id
           JOIN profiles p ON a.user_id = p.user_id
           WHERE a.id = ?''',
        (app_id,)
    ).fetchone()
    
    # Get user documents
    documents = conn.execute(
        'SELECT * FROM documents WHERE user_id = ?',
        (application['user_id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/application.html', application=application, documents=documents)

# Run the app
if __name__ == '__main__':
    app.run()