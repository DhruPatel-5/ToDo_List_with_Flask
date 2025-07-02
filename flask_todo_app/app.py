# app.py

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegisterForm, LoginForm, TaskForm
from models import db, User, Task

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "danger")
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.desc()).limit(5).all()
    return render_template("dashboard.html", tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, start_date=form.start_date.data, due_date=form.due_date.data, status=form.status.data, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash("Task added!", "success")
        return redirect(url_for('dashboard'))
    return render_template("add_task.html", form=form)

@app.route('/my_tasks')
@login_required
def my_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    tasks_todo = [t for t in tasks if t.status != 'complete']
    tasks_done = [t for t in tasks if t.status == 'complete']
    return render_template("my_tasks.html", tasks=tasks_todo, tasks_done=tasks_done)

@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Unauthorized!", "danger")
        return redirect(url_for('dashboard'))
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted!", "info")
    return redirect(url_for('dashboard'))

@app.route('/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_status(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('dashboard'))
    if task.status == 'todo':
        task.status = 'inprogress'
    elif task.status == 'inprogress':
        task.status = 'complete'
    elif task.status == 'complete':
        task.status = 'todo'
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
