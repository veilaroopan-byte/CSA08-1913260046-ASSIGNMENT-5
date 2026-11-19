import csv
import io
import sqlite3

data = """station,date,hour,pm25,pm10,no2,temp,unit
Adyar,2026-10-01,08,48,72,18,29,C
Adyar,2026-10-01,09,NA,70,17,30,C
Guindy,2026-10-01,08,95,140,42,86,F
"""

rows = list(csv.DictReader(io.StringIO(data)))

print("Columns:", list(rows[0]))
print("Rows read:", len(rows))

con = sqlite3.connect(":memory:")

con.executescript("""
CREATE TABLE stations(
    station_id INTEGER PRIMARY KEY,
    station_name TEXT UNIQUE NOT NULL
);

CREATE TABLE readings(
    reading_id INTEGER PRIMARY KEY,
    station_id INTEGER,
    day TEXT,
    hour INTEGER,
    pm25 REAL,
    pm10 REAL,
    no2 REAL,
    temp_c REAL,
    UNIQUE(station_id, day, hour),
    FOREIGN KEY(station_id)
    REFERENCES stations(station_id)
);
""")

con.execute(
    "INSERT INTO stations(station_name) VALUES (?)",
    ("Adyar",)
)

con.execute(
    "INSERT INTO stations(station_name) VALUES (?)",
    ("Guindy",)
)

tables = con.execute("""
SELECT name FROM sqlite_master
WHERE type='table'
ORDER BY name
""").fetchall()

print("Tables created:", [x[0] for x in tables])

count = con.execute(
    "SELECT COUNT(*) FROM stations"
).fetchone()[0]

print("Station count:", count)

con.close()

