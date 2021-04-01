import sqlite3
import hashlib
from flask import Flask, render_template, request, g, redirect, url_for

SESSIONS = dict() #contains sessiond_id and userid
DATABASE = './database.db'

#check login credentials
def check_login(username, password):
    con = sqlite3.connect('database2.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM login_credentials')
    rows = cur.fetchall()
    for row in rows:
        if row[1] == username and row[2] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

#The function get_db gets the databse
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

#Creating Flask Instance
app = Flask(__name__)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#Check Login
@app.route('/')
def root():
    session_id = request.cookies.get('session_id')
    if session_id in SESSIONS.keys():
        return "You're Logged in" + SESSIONS[session_id]
    else:
        return redirect(url_for('login'))

#Login Page
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        print("Attempted Login With:" + request.form['username'] + request.form['password'])
        return do_the_login(request.form['username'],request.form['password'])
    else:
        return show_login_page()

def do_the_login(username,password):
    if check_login(username,password):
        return "Login Success"
    return "Login Failed"

def show_login_page():
    #return "Login Page"
    return redirect(url_for('static', filename='login.html'))
