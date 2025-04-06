-- Database schema for NITDA SIWES/NYSC Portal

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    user_type TEXT NOT NULL, 
    is_admin INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- User profiles
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT,
    phone TEXT,
    address TEXT,
    institution TEXT,
    course TEXT,
    graduation_date TEXT,
    profile_picture TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    document_type TEXT NOT NULL, 
    filename TEXT NOT NULL,
    verified INTEGER DEFAULT 0,
    uploaded_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Applications
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    application_type TEXT NOT NULL, 
    placement_preference TEXT,
    start_date TEXT,
    duration TEXT,
    additional_info TEXT,
    status TEXT DEFAULT 'draft', 
    feedback TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Placements
CREATE TABLE IF NOT EXISTS placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER UNIQUE NOT NULL,
    department TEXT NOT NULL,
    supervisor TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications (id)
);

-- Attendance records
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placement_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    comments TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (placement_id) REFERENCES placements (id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);