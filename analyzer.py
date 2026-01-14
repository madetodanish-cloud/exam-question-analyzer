import re
from collections import defaultdict
from difflib import SequenceMatcher

def clean_question(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def split_into_questions(text):
    lines = text.split("\n")
    questions = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue

        # detect new question
        if re.match(r'^(q\.?\s*\d+|\d+[\.\)])', line.lower()):
            if buffer:
                questions.append(buffer.strip())
            buffer = line
        else:
            buffer += " " + line

    if buffer:
        questions.append(buffer.strip())

    return questions

def find_repeated_questions(texts, threshold=0.60):
    all_questions = defaultdict(list)

    # extract questions per year
    for year, text in texts.items():
        qs = split_into_questions(text)
        for q in qs:
            cleaned = clean_question(q)
            if len(cleaned) > 20:
                all_questions[year].append((q, cleaned))

    matched = []
    used = set()
    years = list(all_questions.keys())

    for i in range(len(years)):
        year_i = years[i]
        for q_raw_i, q_clean_i in all_questions[year_i]:
            key_i = (year_i, q_clean_i)
            if key_i in used:
                continue

            freq = 1
            appeared = [year_i]

            for j in range(i + 1, len(years)):
                year_j = years[j]
                for q_raw_j, q_clean_j in all_questions[year_j]:
                    if similarity(q_clean_i, q_clean_j) >= threshold:
                        freq += 1
                        appeared.append(year_j)
                        used.add((year_j, q_clean_j))
                        break

            if freq > 1:
                matched.append({
                    "question": q_raw_i,
                    "frequency": freq,
                    "years": appeared
                })
                used.add(key_i)

    return matched