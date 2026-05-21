import sqlite3
conn = sqlite3.connect('app.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables:", tables)
conn.close()