import sqlite3

#This module will contain all functions required for a database

DATABASE_PATH = "database.db"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def query(sql):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

def query_t(sql, values):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(sql, values)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows

#creates a list of dicts where the key in each dict is the column
def query_assoc(sql):
    con = sqlite3.connect(DATABASE_PATH)
    con.row_factory = dict_factory 
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    con.close()
    return rows

def num_entries(sql, values=None):
    con = sqlite3.connect(DATABASE_PATH)
    con.row_factory = dict_factory 
    cur = con.cursor()
    cur.execute(sql, values)
    rows = cur.fetchall()
    con.close()
    return len(rows)
