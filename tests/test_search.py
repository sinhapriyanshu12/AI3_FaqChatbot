# tests/test_search.py
import sys
sys.path.append(".")
from agents.vector_store import load_store

store = load_store()

test_queries = [
    "What is the tuition fee for Class 9?",
    "What documents are needed for admission?",
    "What is the last date to pay Term 1 fees?",
    "Can I bring a mobile phone to school?",
    "What is the minimum attendance required?",
    "How many Q&As are in the admissions FAQ?",
    "What is the late fee penalty?",
    "When do board exams start?",
    "Is there a hostel?",
    "What is the RTE seat percentage?",
]

for query in test_queries:
    results = store.similarity_search(query, k=3)
    print(f"\nQuery: {query}")
    for r in results:
        print(f"  → [{r.metadata['source_file']} p{r.metadata['page_number']}] {r.page_content[:100]}...")