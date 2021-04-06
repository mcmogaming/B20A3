import database as d
import re
import hashlib
import random
import string
from flask import Flask, render_template, request, g, redirect, url_for, make_response


SESSIONS = dict() #contains sessiond_id and userid
PRIVILEGES = {"Guest":0,"Student":1,"Teaching Assistant":2,"Professor":3,"Admin":4,}

#Creating Flask Instance
app = Flask(__name__)

def check_session():
    sessionId = request.cookies.get('sessionId')
    if not (sessionId in SESSIONS.keys()):
        print('FAILED Session Check')
        return True
    else:
        print('PASSED Session Check')
        return False

#Check Login
@app.route('/')
def root():
    session_id = request.cookies.get('session_id')
    if session_id in SESSIONS.keys():
        return "You're Logged in" + SESSIONS[session_id]
    else:
        return show_login_page()

#Login Page
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        print('Attempted Login With:' + request.form['username'] + request.form['password'])
        return do_the_login(request.form['username'],request.form['password'])
    else:
        return show_login_page()

def do_the_login(username,password):
    if check_login(username,password):
        if 'sessionId' in request.cookies:
            print('Pass')
        else:
            print('Fail')    
        sessionId = newSessionID()
        userquery = d.query_assoc('SELECT * FROM login_credentials WHERE username = '' + username + ''')[0]
        user = User(userquery)
        SESSIONS[sessionId] = user
        resp = make_response(redirect('/dashboard'))
        resp.set_cookie('sessionId', sessionId, max_age=60*30)
        return resp
    return show_login_page(login_failed = True)

def show_login_page(login_failed=False):
    #return 'Login Page'
    print("showing login page")
    return render_template('login.html', login_failed=login_failed)

def check_login(username, password):
    rows = d.query('SELECT * FROM login_credentials')
    for row in rows:
        if row[1] == username and row[2] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False    

#Register Page
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        return do_register()
    else:
        return show_register_page()

def do_register():
    r = request
    userid = r.form['userid']    
    username = r.form['username']
    password = r.form['password']
    password_r = r.form['password_r']
    fullname = r.form['fullname']
    courses = r.form['courses']
    privilege = r.form['privilege']


    #check inputed values
    sql = "SELECT * FROM 'main'.'login_credentials' WHERE 'username' = ? OR 'userid' = ? "
    num_entries = d.num_entries(sql, (username, userid))
    if num_entries != 0:
        print("Username/UserID already exists")
        g.loginexists = True
        return show_register_page()
    if password != password_r:
        print("Password Don't Match")
        g.passwordnotmatch = True
        return show_register_page()
    if not re.match('^[a-zA-Z0-9]*$',username):
        print("Username not Alphanumeric")       
        g.invalid_username = True
        return show_register_page()
    if not re.match('^[a-zA-Z0-9]*$',password):
        print("Password not Alphanumeric")       
        g.invalid_password = True
        return show_register_page()
    # if not re.match('^[a-zA-Z]*$',fullname):
    #     g.invalid_fullname = True
    #     show_register_page()    
    if not re.match('^[0-9]*$',userid):
        print("userid not numeric")         
        g.invalid_userid = True
        return show_register_page()
    #post them in database
    sql = "INSERT INTO login_credentials (userid, username, hashedpwd, name, privilege, courses) VALUES (?, ?, ?, ?, ?, ?)"
    privilege = PRIVILEGES[privilege]
    d.query_t(sql,(userid, username, hashlib.md5(password.encode()).hexdigest(), fullname, privilege, courses))
    g.accountcreated = True
    print("Account Created Successfully")
    return show_login_page()

def show_register_page():
    return render_template('register.html')



#Dashboard Page
@app.route('/dashboard')
def show_dashboard():
    if check_session():
        return redirect('/login')
    else:
        user = SESSIONS.get(request.cookies.get('sessionId'))
        #setup profile
        g.username = user.username
        g.name = user.name
        g.courses = user.courses
        g.privilege = user.privilege_title

        #setup courses
        return render_template('dashboard.html')

#Home Page
@app.route('/home')
def show_homepage():
    if check_session():
        return redirect('/login')
    else:
        user = SESSIONS.get(request.cookies.get('sessionId'))
        #setup profile
        g.username = user.username
        g.name = user.name
        g.courses = user.courses
        g.privilege = user.privilege_title

        #setup courses
        return render_template('home.html')

#session
def newSessionID():
    print('Generating a new SessionID')
    letters = string.ascii_letters
    sessionId = ''.join(random.choice(letters) for i in range(256))
    print(sessionId)
    return sessionId

def getSessionId():
    return request.cookies.get('sessionId')

#classes
class User:
    def __init__(self, sqlquery):
        self.userid = sqlquery['userid']
        self.username = sqlquery['username']
        self.name = sqlquery['name']
        self.courses = str(sqlquery['courses']).split(',')
        self.privilege = sqlquery['privilege']
        if self.privilege  == 0:
            self.privilege_title = 'Guest'
        elif self.privilege  == 1:
            self.privilege_title = 'Student'
        elif self.privilege  == 2:
            self.privilege_title = 'Teaching Assistant'
        elif self.privilege  == 3:
            self.privilege_title = 'Professor'
        elif self.privilege  == 4:
            self.privilege_title = 'Admin'
        else:
            self.privilege_title = 'Unknown'
        
