import statistics

def clean_rows(rows):

    seen = set()
    cleaned = []
    previous = {}

    for station, day, hour, pm25, pm10, no2, temp, unit in rows:

        station = station.strip().title()
        key = (station, day, int(hour))

        if key in seen:
            continue

        seen.add(key)

        def number(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        p25 = number(pm25)
        p10 = number(pm10)
        n2 = number(no2)
        t = number(temp)

        if p25 is not None and not 0 <= p25 <= 999:
            p25 = None

        if p10 is not None and not 0 <= p10 <= 2000:
            p10 = None

        if n2 is not None and not 0 <= n2 <= 2000:
            n2 = None

        if t is not None and unit.upper() == "F":
            t = (t - 32) * 5 / 9

        if p25 is None and station in previous:
            p25 = previous[station]

        if p25 is not None:
            previous[station] = p25

        cleaned.append((
            station, day, int(hour), p25,
            p10, n2, round(t, 2) if t is not None else None
        ))

    return cleaned


sample = [
    ("Adyar", "2026-10-01", 8, "48", "72", "18", "29", "C"),
    ("Adyar", "2026-10-01", 9, "NA", "70", "17", "30", "C"),
    ("Adyar", "2026-10-01", 9, "60", "75", "20", "31", "C"),
    ("Guindy", "2026-10-01", 8, "95", "140", "42", "86", "F"),
    ("Guindy", "2026-10-01", 9, "-5", "150", "45", "88", "F")
]

result = clean_rows(sample)

for row in result:
    print(row)

values = [48.0, 95.0, 121.0]

low = min(values)
high = max(values)

scaled = [
    round((x - low) / (high - low), 3)
    for x in values
]

mean = statistics.mean(values)
sd = statistics.pstdev(values)

z = [
    round((x - mean) / sd, 3)
    for x in values
]

print("Min-max:", scaled)
print("Z-score:", z)
