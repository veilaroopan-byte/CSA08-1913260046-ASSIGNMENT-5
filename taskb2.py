import csv
import io
import sqlite3

readings = [
    ("Adyar", "2026-10-01", 48.0),
    ("Guindy", "2026-10-01", 95.0),
    ("Guindy", "2026-10-03", 121.0),
    ("Adyar", "2026-10-04", 60.0)
]

con = sqlite3.connect(":memory:")

con.execute("""
CREATE TABLE aq(
    station TEXT,
    day TEXT,
    pm25 REAL
)
""")

con.executemany(
    "INSERT INTO aq VALUES (?,?,?)",
    readings
)

con.commit()


def station_average(name):

    row = con.execute(
        "SELECT AVG(pm25) FROM aq WHERE station=?",
        (name,)
    ).fetchone()

    return round(row[0], 1) if row[0] is not None else None


print(
    station_average("Adyar"),
    station_average("Guindy")
)

print(
    station_average("Adyar' OR '1'='1")
)


cases = {
    "missing_column":
        "station,date\nAdyar,2026-10-01\n",

    "wrong_delimiter":
        "station;date;pm25\nAdyar;2026-10-01;48\n",

    "empty": ""
}


for label, text in cases.items():

    try:

        reader = csv.DictReader(
            io.StringIO(text)
        )

        fields = reader.fieldnames or []

        required = {
            "station", "date", "pm25"
        }

        if not required.issubset(fields):
            raise ValueError(
                "required columns missing or delimiter incorrect"
            )

        print(label, "OK", list(reader))

    except ValueError as exc:

        print(
            label,
            "REJECTED:",
            exc)

print(
    "Safe quote search:",
    station_average("Adyar' OR '1'='1"))

con.close()

