import os
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DB_NAME = 'nitda_portal.db'

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    
    # Open and execute schema.sql
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    print("Database tables created successfully")
    
    # An admin user
    password_hash = generate_password_hash('admin123')
    current_time = datetime.now()
    
    conn.execute(
        'INSERT INTO users (email, password_hash, user_type, is_admin, created_at) VALUES (?, ?, ?, ?, ?)',
        ('admin@nitda.gov.ng', password_hash, 'admin', 1, current_time)
    )
    
    conn.commit()
    print("Admin user created successfully")
    
    conn.close()

def create_upload_folder():
    os.makedirs('uploads', exist_ok=True)
    print("Uploads folder created")

if __name__ == '__main__':
    create_tables()
    create_upload_folder()
    print("Database initialization completed.")