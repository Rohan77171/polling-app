# Polling Application

A full-stack web-based polling application built with Flask, featuring user authentication, real-time voting, and time-limited polls.

## Features

- 🔐 User Registration & Authentication
- 📊 Poll Creation & Management
- 🗳️ One-Vote-Per-User System
- ⏰ Time-Limited Polls
- 📱 Responsive Design
- 📈 Real-time Results
- 🔒 Secure Password Hashing

## Technology Stack

- **Backend**: Flask, Python
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login, Werkzeug Security

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/polling-app.git
cd polling-app

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate

3. Install Dependencies
```bash
pip install -r requirements.txt

4. Run the Application
```bash
python app.py

5. Open http://localhost:5000 in your browser

## Project Structure 

polling-app/
├── app.py              # Main application
├── models.py           # Database models
├── requirements.txt    # Dependencies
├── README.md          # Documentation
├── .gitignore         # Git ignore rules
├── templates/         # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── create_poll.html
│   ├── poll_results.html
│   └── profile.html
└── static/            # Static files
    ├── style.css
    └── script.js

## Usage

1. Register a new account

2. Login with your credentials

3. Create polls with multiple options

4. Set expiration times for polls

5. Vote on active polls

6. View real-time results

## License

MIT License
