import sqlite3

conn = sqlite3.connect('collection.anki2')
c = conn.cursor()
c.execute("SELECT flds FROM notes WHERE flds LIKE '%3종 연기감지기%'")
rows = c.fetchall()
with open('scratch/sqlite_out.txt', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(r[0] + '\n\n')
