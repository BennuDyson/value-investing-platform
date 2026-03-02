import sqlite3

con = sqlite3.connect("value_investing.db")
cur = con.cursor()

print("Tables:")
tables = cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
).fetchall()

for t in tables:
    print("-", t[0])

print("\nRow counts:")
for t in tables:
    table = t[0]
    try:
        n = cur.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
        print(f"{table}: {n}")
    except Exception as e:
        print(f"{table}: error ({e})")