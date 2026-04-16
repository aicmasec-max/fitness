from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"

# Initialize DB
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        steps_goal INTEGER,
        calorie_goal INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        duration INTEGER,
        calories INTEGER,
        date TEXT,
        notes TEXT,
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        count INTEGER
    )''')

    conn.commit()
    conn.close()

init_db()

# Register
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password,steps_goal,calorie_goal) VALUES (?,?,?,?)",
                  (request.form['username'], request.form['password'], 10000, 500))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template("register.html")

# Login
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        user = c.execute("SELECT * FROM users WHERE username=? AND password=?",
                         (request.form['username'], request.form['password'])).fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')
    return render_template("login.html")

# Dashboard
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Add workout
    if request.method == 'POST':
        c.execute('''INSERT INTO workouts 
            (user_id,type,duration,calories,date,notes,timestamp)
            VALUES (?,?,?,?,?,?,?)''',
            (
                session['user_id'],
                request.form['type'],
                request.form['duration'],
                request.form['calories'],
                request.form['date'],
                request.form['notes'],
                datetime.now()
            ))

    # Get data
    workouts = c.execute("SELECT * FROM workouts WHERE user_id=?",
                         (session['user_id'],)).fetchall()

    conn.commit()
    conn.close()

    return render_template("dashboard.html", workouts=workouts)

# Add Steps
@app.route('/add_steps')
def add_steps():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    existing = c.execute("SELECT * FROM steps WHERE user_id=? AND date=?",
                         (session['user_id'], today)).fetchone()

    if existing:
        c.execute("UPDATE steps SET count = count + 500 WHERE id=?", (existing[0],))
    else:
        c.execute("INSERT INTO steps (user_id,date,count) VALUES (?,?,?)",
                  (session['user_id'], today, 500))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

app.run(debug=True)
