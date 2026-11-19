import sqlite3

con = sqlite3.connect(":memory:")

con.execute("""
CREATE TABLE readings(
    station TEXT,
    day TEXT,
    hour INTEGER,
    pm25 REAL,
    temp_c REAL
)
""")

data = [
    ("Adyar", "2026-10-01", 8, 48, 29),
    ("Adyar", "2026-10-01", 9, 52, 30),
    ("Guindy", "2026-10-01", 8, 95, 30),
    ("Guindy", "2026-10-01", 9, 121, 31),
    ("Adyar", "2026-10-02", 8, 42, 28),
    ("Guindy", "2026-10-02", 8, 110, 32)
]

con.executemany(
    "INSERT INTO readings VALUES (?,?,?,?,?)",
    data
)

daily = con.execute("""
SELECT station, day,
MIN(pm25), MAX(pm25),
ROUND(AVG(pm25), 2), COUNT(pm25)
FROM readings
GROUP BY station, day
ORDER BY station, day
""").fetchall()

for row in daily:
    print(row)

hourly = con.execute("""
SELECT hour, ROUND(AVG(pm25), 2)
FROM readings
GROUP BY hour
ORDER BY AVG(pm25) DESC
""").fetchall()

print("Worst hours first:", hourly)

con.close()
