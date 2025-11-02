from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Poll, Option, Vote
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///polls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_poll_expiry():
    """Check and update poll active status based on expiry time"""
    polls = Poll.query.filter(Poll.is_active == True).all()
    for poll in polls:
        if poll.expires_at and poll.expires_at < datetime.utcnow():
            poll.is_active = False
    db.session.commit()

@app.route('/')
def index():
    check_poll_expiry()
    polls = Poll.query.order_by(Poll.created_at.desc()).all()
    return render_template('index.html', polls=polls, current_time=datetime.utcnow())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    user_polls = Poll.query.filter_by(user_id=current_user.id).order_by(Poll.created_at.desc()).all()
    return render_template('profile.html', user_polls=user_polls, current_time=datetime.utcnow())

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_poll():
    if request.method == 'POST':
        question = request.form['question']
        options = request.form.getlist('options')
        duration = request.form.get('duration', '0')
        
        if question and len(options) >= 2:
            # Calculate expiry time
            expires_at = None
            if duration != '0':
                hours = int(duration)
                expires_at = datetime.utcnow() + timedelta(hours=hours)
            
            poll = Poll(
                question=question,
                user_id=current_user.id,
                expires_at=expires_at
            )
            db.session.add(poll)
            db.session.commit()
            
            for option_text in options:
                if option_text.strip():
                    option = Option(text=option_text, poll_id=poll.id)
                    db.session.add(option)
            
            db.session.commit()
            flash('Poll created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please provide a question and at least 2 options.', 'error')
    
    return render_template('create_poll.html')

@app.route('/poll/<int:poll_id>')
def view_poll(poll_id):
    check_poll_expiry()
    poll = Poll.query.get_or_404(poll_id)
    
    # Check if user has already voted
    has_voted = False
    if current_user.is_authenticated:
        has_voted = Vote.query.filter_by(user_id=current_user.id, poll_id=poll_id).first() is not None
    
    return render_template('poll_results.html', poll=poll, has_voted=has_voted, current_time=datetime.utcnow())

@app.route('/vote/<int:poll_id>', methods=['POST'])
@login_required
def vote(poll_id):
    check_poll_expiry()
    poll = Poll.query.get_or_404(poll_id)
    
    # Check if poll is active
    if not poll.is_active:
        return jsonify({'error': 'This poll has ended.'}), 400
    
    # Check if user has already voted
    existing_vote = Vote.query.filter_by(user_id=current_user.id, poll_id=poll_id).first()
    if existing_vote:
        return jsonify({'error': 'You have already voted in this poll.'}), 400
    
    option_id = request.json.get('option_id')
    option = Option.query.get_or_404(option_id)
    
    if option.poll_id != poll_id:
        return jsonify({'error': 'Invalid option for this poll'}), 400
    
    # Record the vote
    option.votes += 1
    vote = Vote(user_id=current_user.id, poll_id=poll_id, option_id=option_id)
    db.session.add(vote)
    db.session.commit()
    
    return jsonify({'success': True, 'new_votes': option.votes})

@app.route('/results/<int:poll_id>')
def get_results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    results = [{'text': option.text, 'votes': option.votes} for option in poll.options]
    
    # Check if user has voted
    has_voted = False
    if current_user.is_authenticated:
        has_voted = Vote.query.filter_by(user_id=current_user.id, poll_id=poll_id).first() is not None
    
    return jsonify({
        'results': results,
        'has_voted': has_voted,
        'is_active': poll.is_active,
        'expires_at': poll.expires_at.isoformat() if poll.expires_at else None
    })

@app.route('/delete_poll/<int:poll_id>', methods=['POST'])
@login_required
def delete_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    
    # Check if user owns the poll
    if poll.user_id != current_user.id:
        flash('You can only delete your own polls!', 'error')
        return redirect(url_for('profile'))
    
    db.session.delete(poll)
    db.session.commit()
    flash('Poll deleted successfully!', 'success')
    return redirect(url_for('profile'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)