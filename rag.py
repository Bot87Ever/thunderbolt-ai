import os

import numpy as np
import ollama
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

DOCUMENT_FOLDER = "documents"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

MODEL = "gemma3:4b"


print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


def load_documents():

    chunks = []

    if not os.path.exists(DOCUMENT_FOLDER):
        os.makedirs(DOCUMENT_FOLDER)

        return chunks

    for filename in os.listdir(DOCUMENT_FOLDER):

        if not filename.lower().endswith(".pdf"):
            continue

        path = os.path.join(
            DOCUMENT_FOLDER,
            filename
        )

        print(
            f"Reading document: {filename}"
        )

        try:

            reader = PdfReader(path)

            text = ""

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            words = text.split()

            chunk_size = 250

            for i in range(
                0,
                len(words),
                chunk_size
            ):

                chunk = " ".join(
                    words[
                        i:i + chunk_size
                    ]
                )

                if chunk.strip():

                    chunks.append(chunk)

        except Exception as e:

            print(
                f"Error reading {filename}: {e}"
            )

    return chunks


def create_index(chunks):

    if not chunks:
        return None

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True
    )

    return embeddings


def retrieve(
    query,
    chunks,
    index,
    top_k=3
):

    if not chunks or index is None:
        return []

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )[0]

    query_norm = np.linalg.norm(
        query_embedding
    )

    index_norms = np.linalg.norm(
        index,
        axis=1
    )

    similarities = np.dot(
        index,
        query_embedding
    ) / (
        index_norms * query_norm + 1e-10
    )

    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    return [
        chunks[i]
        for i in top_indices
    ]


def ask_model(
    question,
    context
):

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question using the provided document context.

If the answer cannot be found in the context,
say that you could not find the information
in the document.

Document context:

{context}

User question:

{question}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def ask_document(question):

    chunks = load_documents()

    if not chunks:

        return "No PDF documents found."

    index = create_index(chunks)

    relevant_chunks = retrieve(
        question,
        chunks,
        index
    )

    if not relevant_chunks:

        return "I could not find that information in the document."

    context = "\n\n---\n\n".join(
        relevant_chunks
    )

    return ask_model(
        question,
        context
    )


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("              THUNDERBOLT.AI")
    print("                 DOCUMENT RAG")
    print("=" * 60)
    print()

    chunks = load_documents()

    if not chunks:

        print("No PDF documents found.")
        print()
        print("Put a PDF inside:")
        print("documents/")
        print()

    else:

        print()
        print(
            f"Document chunks: {len(chunks)}"
        )

        print(
            "Creating vector index..."
        )

        index = create_index(chunks)

        print("Index ready.")
        print()
        print(
            "Ask questions about your document."
        )
        print(
            "Type 'exit' to quit."
        )
        print()

        while True:

            question = input(
                "You: "
            ).strip()

            if question.lower() == "exit":
                break

            if not question:
                continue

            relevant_chunks = retrieve(
                question,
                chunks,
                index
            )

            context = "\n\n---\n\n".join(
                relevant_chunks
            )

            answer = ask_model(
                question,
                context
            )

            print()
            print(
                "Thunderbolt.ai:"
            )
            print(answer)
            print()