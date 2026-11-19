import csv
import io
import sqlite3

RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
Adyar,2026-10-04,1200
"""


def load_clean(text):

    rows = []

    for r in csv.DictReader(io.StringIO(text)):

        raw = r["pm25"].strip()

        if raw == "" or raw.upper() == "NA":
            continue

        try:
            value = float(raw)
        except ValueError:
            continue

        if not 0 <= value <= 999:
            continue

        rows.append((
            r["station"].strip(),
            r["date"],
            value
        ))

    return rows


def min_max(values):

    if not values:
        return []

    low = min(values)
    high = max(values)

    if low == high:
        return [0.0 for _ in values]

    return [
        round((v-low)/(high-low), 3)
        for v in values
    ]


clean = load_clean(RAW)

print("Cleaned:", clean)

print(
    "Normalised:",
    min_max([pm for _, _, pm in clean])
)

con = sqlite3.connect(":memory:")

con.execute("""
CREATE TABLE aq(
    station TEXT,
    day TEXT,
    pm25 REAL,
    PRIMARY KEY(station, day)
)
""")

con.executemany(
    "INSERT INTO aq VALUES (?,?,?)",
    clean
)

print(
    "SQL rows:",
    con.execute(
        "SELECT COUNT(*) FROM aq"
    ).fetchone()[0]
)

print(
    "Adyar mean:",
    con.execute(
        "SELECT ROUND(AVG(pm25),2) "
        "FROM aq WHERE station=?",
        ("Adyar",)
    ).fetchone()[0]
)

print(
    "Station means:",
    con.execute("""
    SELECT station, ROUND(AVG(pm25),2)
    FROM aq
    GROUP BY station
    """).fetchall()
)

con.close()

