import sqlite3
from flask import Flask, render_template, request, g

@app.route("/test", methods=["POST"])
def test():
    return _test(request.form["test"])

@app.route("/index")
def index():
    return _test("My Test Data")

def _test(argument):
    return "TEST: %s" % argument