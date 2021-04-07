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
        userquery = d.query_assoc("SELECT * FROM login_credentials WHERE username = '" + username + "'")[0]
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

def get_userid():
    if 'sessionId' in request.cookies:
        if request.cookies.get('sessionId') in SESSIONS.keys():
            return SESSIONS[request.cookies.get('sessionId')].userid
    return -1        

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
        
#course
@app.route('/courses/<courseid>')
def show_course_page(courseid):
    print(courseid)
    coursepageinfo = d.query("SELECT * FROM coursehomepage WHERE courseid = '"+ courseid +"';")
    
    if checkvalidcourseid(courseid):
        return "Course ID is invalid"
    
    g.courseid = courseid
    g.description = coursepageinfo[0][1]
    g.instructors = coursepageinfo[0][2]
    g.timetable = coursepageinfo[0][3]

    return render_template('coursepage.html')

#lectures
@app.route('/courses/<string:courseid>/lectures')
def show_course_lectures(courseid):
    
    lectures = d.query_assoc("SELECT * FROM lectures WHERE courseid = '"+ courseid +"' ORDER BY lec_order;")
    
    if checkvalidcourseid(courseid):
        return "Course ID is invalid"

    g.lectures = lectures
    g.courseid = courseid

    return render_template('lectures.html')

def checkvalidcourseid(courseid):
    courses = d.query("SELECT * FROM courses WHERE courseid = '"+ courseid +"';")
    return len(courses) != 1


#lecture content
@app.route('/courses/<string:courseid>/lectures/<int:lecorder>')
def show_course_lecture_content(courseid, lecorder):
    lecture = d.query_assoc("SELECT * FROM lectures WHERE courseid = '"+courseid+"' AND lec_order="+str(lecorder)+";")

    if checkvalidcourseid(courseid):
        return "Course ID is invalid"

    if len(lecture) != 1:
        return "Error in lecture order value"

    g.lecture = lecture[0]
    g.courseid = courseid
    
    return render_template('lecturecontent.html')
    

#grades
@app.route('/courses/<string:courseid>/grades')
def show_course_grades(courseid):
    userid = get_userid()
    if userid == -1:
        return "Invalid userid, try logging in"    

    user = SESSIONS[request.cookies.get('sessionId')]
    privilege = user.privilege

    if privilege == 1:
        return show_course_grades_student(user, courseid)
    if privilege == 3:
        return show_course_grades_professor(user, courseid)
    else:
        return "Error: You aren't a student or professor"

def show_course_grades_student(user, courseid):
    grades = d.query_assoc("SELECT * FROM grades WHERE courseid = '"+courseid+"' AND userid="+str(user.userid)+";")
    
    if checkvalidcourseid(courseid):
        return "Course ID is invalid"

    print("Grades: " + str(len(grades)) + "Userid: " + str(user.userid))
    g.grades = grades
    g.courseid = courseid
    g.name = user.name
    
    return render_template('grades.html')

def show_course_grades_professor(user, courseid):
    sql = "SELECT * FROM grades WHERE "

    for c in user.courses :
        sql += " courseid = '"+c+"' OR"

    sql = sql[0:len(sql)-2]
    sql += ";"

    print("SQL:"+sql)

    grades = d.query_assoc(sql)

    if checkvalidcourseid(courseid):
        return "Course ID is invalid"

    print("Grades: " + str(len(grades)) + "Userid: " + str(user.userid))
    g.grades = grades
    g.courseid = courseid
    g.name = user.name
    g.userid = user.userid
    
    return render_template('gradesview.html')

#feedback
@app.route("/feedback", methods=['GET','POST'])
def feedback():
    userid = get_userid()
    if userid == -1:
        return "Invalid userid, try logging in"    

    user = SESSIONS[request.cookies.get('sessionId')]
    privilege = user.privilege

    if request.method == 'POST':
        return send_feedback(user)
    else:
        if privilege == 1:
            return show_feedback_page_student(user)
        elif privilege == 3:
            return show_feedback_page_professor(user)
        else:
            return "Error you aren't a student or professor, try logging in"
def show_feedback_page_student(user):

    #get list of all professors
    professors = d.query_assoc("SELECT * FROM login_credentials where privilege = 3;")
    g.professors = professors

    return render_template('feedback.html')

def show_feedback_page_professor(user):

    #get list of all feedback of a professor
    sql = "SELECT * FROM feedback WHERE userid="+str(user.userid)+";"
    
    feedback = d.query_assoc(sql)

    g.feedback = feedback

    return render_template('feedbackviewer.html')

def send_feedback(user):
    userid = request.form['userid']
    q1 = request.form['q1']
    q2 = request.form['q2']
    q3 = request.form['q3']
    q4 = request.form['q4']

    sql = "INSERT INTO 'main'.'feedback'('userid','q1','q2','q3','q4') VALUES (?,?,?,?,?);"
    d.query_t(sql,(userid, q1,q2,q3,q4))
    g.feedbacksubmitted = True

    professors = d.query_assoc("SELECT * FROM login_credentials where privilege = 3;")
    g.professors = professors

    return render_template('feedback.html')

#logout
@app.route('/logout')
def logout():
    
    #check if sessionid is in session
    sessionId = request.cookies.get('sessionId')
    if(sessionId in SESSIONS.keys()):
    #remove it from sessions dictionary
        SESSIONS.pop(sessionId, None)
    
    #return user to hompage
    return login()

#regrade request
@app.route('/courses/<string:courseid>/regrade', methods=['GET','POST'])
def regrade(courseid):
    userid = get_userid()
    if userid == -1:
        return "Invalid userid, try logging in"    

    user = SESSIONS[request.cookies.get('sessionId')]
    privilege = user.privilege

    if request.method == 'POST':
        print("Sending regrade request")
        return send_regrade(user, userid)
    else:
        if privilege == 1:
            print("showing regrade page student")
            return show_regrade_page_student(user,courseid)
        elif privilege == 3:
            print("showing regrade page professor")           
            return show_regrade_page_professor(user)
        else:
            return "Error you aren't a student or professor, try logging in"
    
def show_regrade_page_student(user,courseid):
    g.courses = (courseid,)
    
    sql = "SELECT DISTINCT * FROM assignments where courseid = '"+courseid+"' ;"
    assignmentnames = d.query_assoc(sql)
    
    g.assignmentnames = assignmentnames
        
    return render_template('regrade.html')

def send_regrade(user, userid):

    #get all variables in order
    userid = user.userid
    courseid = request.form['courseid']
    assignment_name = request.form['assignment_name']
    reason = request.form['reason']

    #send them to the database
    sql = "INSERT INTO 'main'.'regrades'('userid','courseid','assignment_name','reason') VALUES (?,?,?,?);"
    d.query_t(sql,(userid, courseid, assignment_name, reason))
    
    g.submittedsuccess = True

    return show_regrade_page_student(user, courseid)

def show_regrade_page_professor(user):
    return render_template('regradeview.html')