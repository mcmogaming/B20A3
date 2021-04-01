import sqlite3

con = sqlite3.connect('database2.db')
cur = con.cursor()

cur.execute('SELECT * FROM login_credentials')
row = cur.fetchall()
print(row)
print(len(row))
print(row[1])


#print all rows in login_credentials