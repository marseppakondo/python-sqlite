from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, LoginManager, login_user, logout_user, current_user
from flask_wtf import CSRFProtect # library csrf protection
from sqlalchemy import text
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'rayapbesi'


csrf = CSRFProtect(app) # mengaktifkan CSRF Protection
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(15), nullable=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

# otorisasi role
def require_role(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403) 
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/')
@login_required
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# autentikasi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        return "Login Gagal", 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
@login_required
@require_role('admin')
def add_student():
    name =  request.form['name'].strip()
    age_rw = request.form['age'].strip()
    grade = request.form['grade'].strip().upper()
    
    # name = request.form['name']
    # age = request.form['age']
    # grade = request.form['grade']
    
    # validasi nama
    if not re.match("^[A-Za-z ]+$", name):
        return "Nama tidak valid. Hanya huruf dan spasi yang diizinkan.", 400
    
    # validasi umur
    try: 
        age = int(age_rw)
        if age < 0:
            raise ValueError
    except ValueError:
        return "Umur tidak valid.", 400
    
    # # validasi grade
    allowGrades = ['A', 'B', 'C', 'D', 'E']
    if grade not in allowGrades:
        return "Grade tidak valid.", 400


    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)

     # Parameterized query
    query = "INSERT INTO student (name, age, grade) VALUES (?, ?, ?)"
    cursor.execute(query, (name, age, grade))

    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>', methods=['POST']) 
@login_required
@require_role('admin')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))
# @app.route('/delete/<string:id>') 
# @login_required

# def delete_student(id):
#     # RAW Query
#     db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
#     db.session.commit()
#     return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def edit_student(id):
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        age_rw = request.form['age'].strip()
        grade = request.form['grade'].strip().upper()

        # name = request.form['name']
        # age = request.form['age']
        # grade = request.form['grade']

        # validasi nama
        if not re.match("^[A-Za-z ]+$", name):
            return "Nama tidak valid. Hanya huruf dan spasi yang diizinkan.", 400
        
        # validasi umur
        try:
            age = int(age_rw)
            if age < 0:
                raise ValueError
        except ValueError:
            return "Umur tidak valid.", 400
        
        # validasi grade
        allowGrades = ['A', 'B', 'C', 'D', 'E']
        if grade not in allowGrades:
            return "Grade tidak valid.", 400 
        
        # RAW Query
        # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))

        db.session.execute(
            text(f"UPDATE student SET name=:name , age=:age , grade=:grade WHERE id=:id"),
            {'name': name, 'age': age, 'grade': grade, 'id': id}
        )
        
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        # student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        
        student = db.session.execute(
            text(f"SELECT * FROM student WHERE id=:id "), {"id":id}
        ).fetchone()
        return render_template('edit.html', student=student)

# Bonus CSRF
@app.route('/edit_username/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_username(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        username = request.form['username'].strip()
        user.username = username
        db.session.commit()
        return redirect(url_for('index'))
    else:
        user = db.session.execute(
            text(f"SELECT * FROM user WHERE id=:id "), {"id":id}
        ).fetchone()
        return render_template('edit_username.html', user=user)
    

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

