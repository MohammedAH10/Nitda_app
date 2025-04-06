# NITDA SIWES/NYSC Application Portal

## Features

- User authentication (registration, login, logout)
- Profile management
- Document uploads
- Application submission and tracking
- Admin dashboard for application review
- Responsive UI using Bootstrap

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install the required packages:
   ```
   pip install flask flask-login werkzeug
   ```

4. Initialize the database:
   ```
   python init_db.py
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

### User Flow

1. Register for an account as either a SIWES or NYSC applicant
2. Complete your profile information
3. Upload required documents
4. Submit your application
5. Track application status from your dashboard

### Admin Access

- Admin URL: `http://127.0.0.1:5000/admin/dashboard`
- Default admin credentials:
  - Email: admin@nitda.gov.ng
  - Password: admin123

## Project Structure

```
nitda_app
├── app.py                 # Main application file
├── schema.sql             # Database schema
├── init_db.py             # Database initialization script
├── uploads/               # Directory for uploaded documents
├── templates/
│   ├── base.html          # Base template with common elements
│   ├── index.html         # Homepage
│   ├── register.html      # Registration page
│   ├── login.html         # Login page
│   ├── dashboard.html     # User dashboard
│   ├── profile.html       # User profile management
│   ├── documents.html     # Document upload and management
│   ├── application.html   # Application form
│   ├── admin/
│       ├── dashboard.html # Admin dashboard
│       └── application.html # Application review page
└── README.md              # This file
```
