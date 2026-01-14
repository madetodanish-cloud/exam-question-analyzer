import streamlit as st
import pdfplumber
import re
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Exam Question Paper Analyzer", layout="wide")

# ---------------- DARK UI ----------------
st.markdown("""
<style>
body, .stApp { background-color: #0b0f19; color: #e6edf3; }
h1, h2, h3 { color: #e6edf3; }
.stButton>button {
    background-color: #1f6feb; color: white;
    border-radius: 10px; height: 3em; font-size: 16px;
}
.card {
    background-color: #161b22;
    padding: 14px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.badge-high { color: #ff7b72; font-weight: bold; }
.badge-medium { color: #f2cc60; font-weight: bold; }
.topic { color: #7ee787; }
</style>
""", unsafe_allow_html=True)

# ---------------- TOPIC KEYWORDS ----------------
TOPICS = {
    "Equivalence / Relations": ["equivalence", "relation", "reflexive", "symmetric", "transitive"],
    "Graph Theory": ["graph", "bfs", "dfs", "spanning", "tree", "euler", "hamilton"],
    "Recurrence": ["recurrence", "generating"],
    "Functions": ["function", "injective", "surjective", "bijective"],
    "Combinatorics": ["combination", "permutation", "pigeon", "multinomial"]
}

# ---------------- FUNCTIONS ----------------
def extract_year(name):
    m = re.search(r"(20\d{2})", name)
    return m.group(1) if m else "Unknown"

def extract_questions(pdf_file):
    qs = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split("\n"):
                line = line.strip()
                if len(line) > 25:
                    qs.append(line)
    return qs

def detect_topic(question):
    q = question.lower()
    for topic, keys in TOPICS.items():
        for k in keys:
            if k in q:
                return topic
    return "General"

# ---------------- UI ----------------
st.title("📘 Exam Question Paper Analyzer (MVP)")
st.write("Upload **2 or more PDFs**. Get **high-frequency repeated questions** with topics.")

uploaded = st.file_uploader(
    "Upload Question Papers (PDFs)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded and len(uploaded) >= 2:
    if st.button("Analyze"):
        with st.spinner("Analyzing papers..."):
            questions = []
            years = []

            for pdf in uploaded:
                year = extract_year(pdf.name)
                qs = extract_questions(pdf)
                for q in qs:
                    questions.append(q)
                    years.append(year)

            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf = vectorizer.fit_transform(questions)
            sim = cosine_similarity(tfidf)

            groups = []
            used = set()

            for i in range(len(questions)):
                if i in used:
                    continue
                group = [(questions[i], years[i])]
                for j in range(i + 1, len(questions)):
                    if sim[i][j] > 0.68:
                        group.append((questions[j], years[j]))
                        used.add(j)
                if len(group) > 1:
                    groups.append(group)
                    used.add(i)

        st.subheader("🔥 High-Value Repeated Questions")

        report = []

        if not groups:
            st.warning("No repeated questions found.")
        else:
            for g in groups:
                year_list = [y for _, y in g]
                freq = len(set(year_list))
                label = (
                    "<span class='badge-high'>🔥 HIGH</span>" if freq >= 3
                    else "<span class='badge-medium'>🟡 MEDIUM</span>"
                )
                topic = detect_topic(g[0][0])

                st.markdown(f"### {label} — Appeared in {freq} year(s)")
                st.markdown(f"<span class='topic'>Topic: {topic}</span>", unsafe_allow_html=True)

                for q, y in g:
                    st.markdown(
                        f"<div class='card'><b>{y}</b><br>{q}</div>",
                        unsafe_allow_html=True
                    )
                    report.append({
                        "Question": q,
                        "Year": y,
                        "Frequency": freq,
                        "Topic": topic
                    })

            df = pd.DataFrame(report)

            st.download_button(
                "⬇ Download CSV",
                df.to_csv(index=False),
                file_name="mvp_repeated_questions.csv",
                mime="text/csv"
            )

            st.download_button(
                "⬇ Download TXT",
                "\n\n".join(
                    f"[{r['Year']}] {r['Question']} | {r['Topic']} | freq={r['Frequency']}"
                    for r in report
                ),
                file_name="mvp_repeated_questions.txt",
                mime="text/plain"
            )

elif uploaded:
    st.info("Upload at least **2 PDFs**.")