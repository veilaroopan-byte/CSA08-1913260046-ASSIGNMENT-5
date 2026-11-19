import re
import sqlite3
import time

POSITIVE = {
    "good", "clean", "fast",
    "helpful", "improved"
}

NEGATIVE = {
    "bad", "dirty", "slow",
    "rude", "smoke", "broken"
}

NEGATORS = {
    "not", "never", "no"
}


def score(text):

    words = re.findall(
        r"[a-z]+",
        text.lower()
    )

    total = 0

    for i, word in enumerate(words):

        value = (
            1 if word in POSITIVE
            else -1 if word in NEGATIVE
            else 0
        )

        if i > 0 and words[i-1] in NEGATORS:
            value *= -1

        total += value

    return total


def label(text):

    value = score(text)

    if value > 0:
        return "positive"

    if value < 0:
        return "negative"

    return "neutral"


complaints = [
    "Roads are clean and the bus was fast.",
    "Smoke from the factory, air is bad.",
    "The staff were not helpful.",
    "Not bad, service improved.",
    "The air is dirty near the school.",
    "The bus service is slow.",
    "The repair team was helpful.",
    "The road is clean but traffic is slow.",
    "No smoke today and the air is good.",
    "The sensor is broken and the report is bad."
]

complaints = (complaints * 5)[:50]

labels = [
    label(x)
    for x in complaints
]

manual = []

for x in complaints:

    text = x.lower()

    if (
        "clean" in text or
        "helpful" in text or
        "improved" in text or
        "not bad" in text
    ):
        manual.append("positive")

    elif (
        "bad" in text or
        "dirty" in text or
        "smoke" in text or
        "slow" in text or
        "broken" in text or
        "not helpful" in text
    ):
        manual.append("negative")

    else:
        manual.append("neutral")


agree = sum(
    a == b
    for a, b in zip(labels, manual)
)

print("Complaints:", len(complaints))

print(
    "Agreement:",
    agree,
    "/",
    len(complaints),
    "=",
    round(100 * agree / len(complaints), 1),
    "%"
)

for text, tag in zip(
    complaints[:4],
    labels[:4]
):
    print(tag, "|", text)


con = sqlite3.connect(":memory:")

con.execute("""
CREATE TABLE readings(
    station TEXT,
    day TEXT,
    pm25 REAL
)
""")

rows = [
    (
        f"S{i % 120}",
        f"2026-10-{i % 30 + 1:02d}",
        float(i % 150)
    )
    for i in range(200000)
]

con.executemany(
    "INSERT INTO readings VALUES (?,?,?)",
    rows
)

query = """
SELECT AVG(pm25)
FROM readings
WHERE station=? AND day=?
"""

params = ("S17", "2026-10-18")

start = time.perf_counter()

for _ in range(30):
    con.execute(
        query,
        params
    ).fetchone()

before = time.perf_counter() - start

con.execute("""
CREATE INDEX idx_station_day
ON readings(station, day)
""")

start = time.perf_counter()

for _ in range(30):
    con.execute(
        query,
        params
    ).fetchone()

after = time.perf_counter() - start

print(
    "Query seconds before index:",
    round(before, 4)
)

print(
    "Query seconds after index:",
    round(after, 4)
)

con.close()
