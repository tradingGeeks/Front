import sqlite3

db = sqlite3.connect("scraping_failure.db")
cur = db.cursor()
cur.execute("SELECT * FROM fail")
data = cur.fetchall()
db.commit()
db.close()
print(data)