import os
import pdfplumber
from analyzer import find_repeated_questions

def extract_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text

print("\n=== EXAM QUESTION PAPER ANALYZER (CLI MODE) ===\n")

pdf_files = [f for f in os.listdir() if f.endswith(".pdf")]

if len(pdf_files) < 2:
    print("❌ Need at least 2 PDF files in this folder")
    exit()

texts = {}
for pdf in pdf_files:
    print(f"Reading: {pdf}")
    texts[pdf.replace(".pdf", "")] = extract_text(pdf)

print("\nAnalyzing repeated questions...\n")

results = find_repeated_questions(texts)

if not results:
    print("❌ No repeated questions found.")
else:
    print(f"✅ Found {len(results)} repeated questions\n")
    for i, r in enumerate(results, 1):
        print("="*60)
        print(f"{i}. FREQUENCY: {r['frequency']}")
        print(f"   YEARS: {', '.join(r['years'])}")
        print(f"   QUESTION:\n   {r['question']}\n")

print("\n=== DONE ===")
input("Press Enter to exit...")