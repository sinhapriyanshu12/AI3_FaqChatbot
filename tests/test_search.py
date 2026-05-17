import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.vector_store import load_store

def test_search():
    try:
        store = load_store()
    except Exception as e:
        print(f"ERROR: Could not load FAISS store: {e}")
        print("Please run: python data/pipeline/build_kb.py first")
        return

    test_queries = [
        "What is the tuition fee for Class 9?",
        "What documents are needed for admission?",
        "What is the last date to pay Term 1 fees?",
        "Can I bring a mobile phone to school?",
        "What is the minimum attendance required?",
        "What is the late fee penalty?",
        "Is there a hostel facility?",
        "What is the RTE seat percentage?",
        "What sports facilities are available?",
        "How are parents informed about progress?",
    ]

    print("=" * 60)
    print("FAISS SEARCH TEST — 10 queries")
    print("=" * 60)

    for i, query in enumerate(test_queries, 1):
        results = store.similarity_search(query, k=3)
        print(f"\n[{i}] Query: {query}")
        for r in results:
            print(f"  → [{r.metadata.get('source_file','?')} p{r.metadata.get('page_number','?')}] {r.page_content[:100]}...")

    print("\n" + "=" * 60)
    print("TEST COMPLETE — Check results above match correct documents")
    print("=" * 60)

if __name__ == "__main__":
    test_search()
