import logging
import time
import cProfile
import pstats
import io

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(message)s"
)

def clean(values):

    valid = []

    for row_no, value in enumerate(values, start=1):

        try:
            number = float(value)

            assert number >= 0, "Negative PM2.5"

            valid.append(number)

        except (ValueError, TypeError) as exc:
            logging.warning(
                "row %d rejected: %s",
                row_no, exc
            )

        except AssertionError as exc:
            logging.warning(
                "row %d rejected: %s",
                row_no, exc
            )

    return valid


raw = ["48", "NA", "-5", "95", "121"]

start = time.perf_counter()

cleaned = clean(raw)

elapsed = time.perf_counter() - start

print("Cleaned:", cleaned)

print(
    "Elapsed seconds:",
    round(elapsed, 6)
)


def workload():
    return clean(raw * 1000)


profile = cProfile.Profile()

profile.enable()

workload()

profile.disable()

stream = io.StringIO()

pstats.Stats(
    profile,
    stream=stream
).sort_stats("cumulative").print_stats(5)

print("PROFILE")
print(stream.getvalue())
