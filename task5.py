import re
from collections import Counter

POS = {
    "good", "clean", "helpful",
    "improved", "fast"
}

NEG = {
    "bad", "dirty", "rude",
    "slow", "smoke", "broken"
}

NEGATORS = {"not", "never", "no"}


def tokens(text):
    return re.findall(
        r"[a-z]+",
        text.lower()
    )


def sentiment(text):

    words = tokens(text)
    total = 0

    for i, word in enumerate(words):

        value = (
            1 if word in POS
            else -1 if word in NEG
            else 0
        )

        if i and words[i-1] in NEGATORS:
            value *= -1

        total += value

    return total


def summarise(text, limit=2):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    words = [
        w for w in tokens(text)
        if len(w) > 3
    ]

    freq = Counter(words)

    scored = []

    for index, sentence in enumerate(sentences):

        score = sum(
            freq[w]
            for w in tokens(sentence)
            if len(w) > 3
        )

        scored.append(
            (score, -index, sentence)
        )

    return [
        s for _, _, s in
        sorted(scored, reverse=True)[:limit]
    ]


complaint = (
    "Roads are clean. "
    "Smoke is bad near school. "
    "Buses are slow."
)

print("Sentiment:", sentiment(complaint))

print("Summary:", summarise(complaint))
