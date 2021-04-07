import database as d
import re
import hashlib
import random
import string
from flask import Flask, render_template, request, g, redirect, url_for, make_response
import random as rand

COURSES = ('CSCA08','CSCA48','CSCB20','CSCB63')
PROFID = {10,11,12,13}

#delete all data in tables
d.query("DELETE FROM assignments;")
d.query("DELETE FROM grades;")
d.query("DELETE FROM coursehomepage;")
d.query("DELETE FROM lectures;")
d.query("DELETE FROM feedback;")
d.query("DELETE FROM regrades;")

#insert dummy 

#for each course
for c in COURSES:

    #insert assignments  
    for i in range(1,5):
        d.query_t("INSERT INTO 'main'.'assignments'('courseid','assignment_name','due_date','total_marks','course_percentage') VALUES (?,?,?,?,?);", (c, "Assignment " + str(i), "2021-04-2{day}T20:00:00".format(day = i), 10, 0.25))

    #insert grades
    for w in range(1,9):
        for i in range(1,5): #for each assignment
            d.query_t("INSERT INTO 'main'.'grades'('userid','courseid','assignment_name','grade') VALUES (?,?,?,?);", (w, c, "Assignment " + str(i), round(rand.random(),2)))

    #insert dummycourse info    
    d.query_t("INSERT INTO 'main'.'coursehomepage'('courseid','coursedescription','courseinstructors','coursetimetable') VALUES (?,?,?,?);",(c, "This is course description" + c, "These are instructors for" + c, "This is the timetable for " + c))

    #insert lectures
    for i in range(1,5):
        d.query_t("INSERT INTO 'main'.'lectures'('courseid','lec_order','lec_title','html') VALUES (?,?,?,?);",(c, i, 'Week' + str(i), 'This is the html stuff for week' + str(i)) )

    #insert regrade requests
    for w in range(1,5):
        d.query_t("INSERT INTO 'main'.'regrades'('userid','courseid','assignment_name','reason') VALUES (?,?,?,?);", (w, c, 'Assignment 1', 'This is dummy reason'))
        d.query_t("INSERT INTO 'main'.'regrades'('userid','courseid','assignment_name','reason') VALUES (?,?,?,?);", (w, c, 'Assignment 2', 'We want more marks'))
        d.query_t("INSERT INTO 'main'.'regrades'('userid','courseid','assignment_name','reason') VALUES (?,?,?,?);", (w, c, 'Assignment 3', 'We can do better :('))

#for each prof insert dummy data
for p in PROFID:
    sql = "INSERT INTO 'main'.'feedback'('userid','q1','q2','q3','q4') VALUES (?,?,?,?,?);"
    d.query_t(sql, (p, "Good speaker"+str(p), "nothing", "intersting topics", "prepare before labs"))
    d.query_t(sql, (p, "Enthusiastic"+str(p), "Nothingmuch", "cool topics", "labs need more content"))
    d.query_t(sql, (p, "Great Explainer"+str(p), "Nothing much", "topics are related to course", "create a ta website"))

