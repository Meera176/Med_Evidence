from fetcher import fetch_papers
from pdf_loader import process_pdf, chunk_text, clean_text
from embedder import embed_chunks
from vector_store import store_chunks, clear_collection
from searcher import hybrid_search
from retriever import ask


def ingest_from_pubmed(query: str) -> None:
    papers = fetch_papers(query, max_results=5)
    if not papers:
        print("No papers found.")
        return

    print(f"Chunking and embedding {len(papers)} papers...")
    all_chunks = []
    for paper in papers:
        cleaned = clean_text(paper["text"])
        chunks = chunk_text(cleaned)
        for chunk, _ in chunks:
            all_chunks.append({"text": chunk, "source": paper["source"], "page": paper["page"]})

    all_chunks = embed_chunks(all_chunks)
    store_chunks(all_chunks)
    print(f"Ingested {len(all_chunks)} chunks from PubMed.")


def ingest_from_pdf(path: str) -> None:
    print("Extracting and chunking PDF...")
    chunks = process_pdf(path)
    print(f"{len(chunks)} chunks extracted")
    chunks = embed_chunks(chunks)
    store_chunks(chunks)
    print("Ingestion complete.")


def answer(question: str):
    response = ask(question, hybrid_search(question))
    print(f"\nAnswer:\n{response}\n")


if __name__ == "__main__":
    print("MedEvidence — Medical Awareness Platform")
    print("==========================================")
    print("1. Search medical literature (PubMed)")
    print("2. Upload your own PDF")
    print("3. Ask questions (use already ingested data)")
    print("4. Clear all ingested data")
    choice = input("\nChoose (1, 2, 3 or 4): ").strip()

    if choice == "1":
        topic = input("Enter disease or medicine to search: ").strip()
        ingest_from_pubmed(topic)
    elif choice == "2":
        path = input("PDF path: ").strip()
        ingest_from_pdf(path)
    elif choice == "4":
        confirm = input("Are you sure? This deletes all ingested data (yes/no): ").strip().lower()
        if confirm == "yes":
            clear_collection()
            print("All ingested data cleared.")
        exit()
    elif choice != "3":
        print("Invalid choice.")
        exit()

    while True:
        question = input("\nAsk a question (or 'quit'): ").strip()
        if question.lower() == "quit":
            break
        answer(question)
