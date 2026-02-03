from app.kb import load_raw_faq, build_documents, split_documents, build_faiss_index


def main() -> None:
    raw_items = load_raw_faq()
    print(f"Loaded {len(raw_items)} raw FAQ items")

    docs = build_documents(raw_items)
    print(f"Built {len(docs)} Document objects")

    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    index = build_faiss_index(chunks)
    print("FAISS index built and saved.")


if __name__ == "__main__":
    main()
