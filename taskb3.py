import csv
import io
import sqlite3
import time
import cProfile
import pstats

from collections import defaultdict
import pandas as pd


DAYS = 365 * 24


# Generate sample air-quality data
def make_csv(stations):

    out = io.StringIO()
    w = csv.writer(out)

    w.writerow(["station", "day", "pm25"])

    for s in range(stations):
        for h in range(DAYS):

            day = h // 24

            value = float(
                (s * 13 + h % 97) % 180
            )

            w.writerow([
                f"S{s+1}",
                day,
                value
            ])

    return out.getvalue()


# Method 1: Using Python loops
def loop_means(text):

    sums = defaultdict(float)
    counts = defaultdict(int)

    for row in csv.DictReader(io.StringIO(text)):

        key = (
            row["station"],
            int(row["day"])
        )

        sums[key] += float(row["pm25"])
        counts[key] += 1

    return {
        k: sums[k] / counts[k]
        for k in sums
    }


# Method 2: Using Pandas
def pandas_means(text):

    frame = pd.read_csv(io.StringIO(text))

    result = frame.groupby(
        ["station", "day"]
    )["pm25"].mean()

    return result.to_dict()


# Method 3: Using SQL
def sql_means(text):

    con = sqlite3.connect(":memory:")

    con.execute("""
        CREATE TABLE r(
            station TEXT,
            day INTEGER,
            pm25 REAL
        )
    """)

    rows = csv.DictReader(io.StringIO(text))

    con.executemany(
        "INSERT INTO r VALUES (?,?,?)",
        (
            (
                x["station"],
                int(x["day"]),
                float(x["pm25"])
            )
            for x in rows
        )
    )

    result = {
        (station, day): avg
        for station, day, avg in con.execute("""
            SELECT station, day, AVG(pm25)
            FROM r
            GROUP BY station, day
        """).fetchall()
    }

    con.close()

    return result


# Compare performance of all three methods
for stations in (1, 12, 120):

    print("\nTesting", stations, "stations")

    text = make_csv(stations)

    times = {}
    results = {}

    methods = [
        ("loop", loop_means),
        ("pandas", pandas_means),
        ("sql", sql_means)
    ]

    for name, fn in methods:

        start = time.perf_counter()

        results[name] = fn(text)

        times[name] = (
            time.perf_counter() - start
        )

    # Compare all calculated averages
    agree = (
        results["loop"].keys()
        == results["pandas"].keys()
        == results["sql"].keys()
    )

    if agree:
        agree = all(
            abs(
                results["loop"][k]
                - results["pandas"][k]
            ) < 1e-9
            and
            abs(
                results["loop"][k]
                - results["sql"][k]
            ) < 1e-9
            for k in results["loop"]
        )

    print(
        stations,
        "stations,",
        stations * DAYS,
        "rows; groups:",
        len(results["loop"]),
        "agree:",
        agree,
        "seconds:",
        {
            k: round(v, 3)
            for k, v in times.items()
        }
    )


# Profile Python loop performance
print("\nProfiling Python loop method")

sample = make_csv(12)

prof = cProfile.Profile()

prof.enable()

loop_means(sample)

prof.disable()

pstats.Stats(
    prof
).sort_stats("cumulative").print_stats(8)
