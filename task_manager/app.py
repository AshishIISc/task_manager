import os
import uuid
import re
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_login import (LoginManager, UserMixin, login_user, logout_user, login_required,
                         current_user)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://ashishkumar:password123@localhost:5432/postgres'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/task_manager.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Task Manager startup')

# Extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect to login page if user is not authenticated
login_manager.login_message_category = 'info'


# --- Models ---
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256)) # Store hash, not plaintext
    tasks = db.relationship('Task', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Task(db.Model):
    id = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, default='in progress') # 'in progress' or 'completed'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Task {self.name}>"


# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


def validate_task_name(form, field):
    if not re.match(r'^[A-Za-z\s]+$', field.data):
        raise ValidationError('Task name can only contain alphabets and spaces.')


class AddTaskForm(FlaskForm):
    name = StringField(
        'Task Name',
        validators=[
            DataRequired(),
            Length(min=1, max=120),
            validate_task_name
        ]
    )
    submit = SubmitField('Add Task')


class UpdateTaskForm(FlaskForm):
    name = StringField(
        'Task Name',
        validators=[
            DataRequired(),
            Length(min=1, max=120),
            validate_task_name
        ]
    )
    status = SelectField(
        'Status',
        choices=[
            ('in progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Update Task')


# --- Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login unsuccessfulyl. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/', methods=['GET'])
@login_required
def index():
    add_form = AddTaskForm()
    update_form = UpdateTaskForm()
    
    status_filter = request.args.get('status_filter', 'all')

    query = Task.query.filter_by(user_id=current_user.id)
    
    valid_statuses = ['in progress', 'completed', 'failed']
    if status_filter in valid_statuses:
        query = query.filter(Task.status == status_filter)
    elif status_filter != 'all':
        flash(f"Invalid status filter '{status_filter}'. Showing all tasks.", 'warning')
        status_filter = 'all'

    tasks = query.order_by(Task.timestamp.desc()).all()
    
    app.logger.info(f"User {current_user.username} viewed tasks with filter: {status_filter}")

    return render_template(
        'tasks.html',
        title='Your Tasks',
        tasks=tasks,
        add_form=add_form,
        update_form=update_form,
        current_filter=status_filter
    )


@app.route('/add', methods=['POST'])
@login_required
def add_task():
    form = AddTaskForm()
    if form.validate_on_submit():
        task = Task(name=form.name.data, author=current_user)
        try:
            db.session.add(task)
            db.session.commit()
            flash('Task added successfully!', 'success')
            app.logger.info(f"Task '{task.name}' (ID: {task.id}) added successfully by user {current_user.username}.")
        except Exception as e:
            db.session.rollback()
            flash('Error adding task.', 'danger')
            app.logger.error(f"Error adding task for user {current_user.username}: {e}", exc_info=True)

    else:
        # Collect errors if validation fails
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
                app.logger.warning(f"Validation error adding task for user {current_user.username}. Field: {field}, Error: {error}")
    return redirect(url_for('index'))


@app.route('/update/<task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('You do not have permission to edit this task.', 'danger')
        app.logger.warning(f"User {current_user.username} attempted to edit task ID {task_id} without permission.")
        return redirect(url_for('index'))

    form = UpdateTaskForm(request.form) # Populate form with request data

    if form.validate_on_submit():
        original_name = task.name
        task.name = form.name.data
        task.status = form.status.data
        try:
            db.session.commit()
            flash('Task updated successfully!', 'success')
            app.logger.info(f"Task '{original_name}' (ID: {task.id}) updated to Name: '{task.name}', Status: '{task.status}' by user {current_user.username}.")
        except Exception as e:
            db.session.rollback()
            flash('Error updating task.', 'danger')
            app.logger.error(f"Error updating task ID {task_id} for user {current_user.username}: {e}", exc_info=True)
    else:
        # Collect errors if validation fails
        log_msg_prefix = f"Validation error updating task ID {task_id} for user {current_user.username}."
        for field, errors in form.errors.items():
            for error in errors:
                 # Use field.label.text if available, otherwise field name
                field_name = getattr(getattr(form, field, None), 'label', None)
                if field_name:
                    field_name = field_name.text
                else:
                    field_name = field.capitalize() # Fallback
                flash(f"Error updating task in {field_name}: {error}", 'danger')
                app.logger.warning(f"{log_msg_prefix} Field: {field_name}, Error: {error}")

    # Even if update fails validation, redirect to index to show flash messages
    return redirect(url_for('index'))


@app.route('/delete/<task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('You do not have permission to delete this task.', 'danger')
        app.logger.warning(f"User {current_user.username} attempted to delete task ID {task_id} without permission.")
        return redirect(url_for('index')) # Or abort(403)

    if task.status == 'completed':
        task_name_for_log = task.name # Store name before deleting
        try:
            db.session.delete(task)
            db.session.commit()
            flash('Task deleted successfully!', 'success')
            app.logger.info(f"Task '{task_name_for_log}' (ID: {task_id}) deleted successfully by user {current_user.username}.")
        except Exception as e:
            db.session.rollback()
            flash('Error deleting task.', 'danger')
            app.logger.error(f"Error deleting task ID {task_id} for user {current_user.username}: {e}", exc_info=True)
    else:
        flash('Task must be marked as "completed" before deletion.', 'warning')
        app.logger.warning(f"User {current_user.username} attempted to delete incomplete task ID {task_id} (Status: {task.status}).")
    return redirect(url_for('index'))

# --- Database Initialization and Dummy User ---


def create_db_and_user():
    with app.app_context():
        db.create_all()
        # Create a dummy user if none exists
        if not Users.query.filter_by(username='testuser').first():
            dummy_user = Users(username='testuser')
            # !!! Use a more secure password or method in production !!!
            dummy_user.set_password('password123')
            db.session.add(dummy_user)
            db.session.commit()
            print("Database created and dummy user 'testuser' (password: 'password123') added.")
        else:
            print("Database already exists or dummy user already present.")


if __name__ == '__main__':
    create_db_and_user() # Ensure DB and user exist before running
    app.logger.info('Starting Flask development server.') # Log server start
    app.run(port=8001, debug=True) # Debug mode for development 