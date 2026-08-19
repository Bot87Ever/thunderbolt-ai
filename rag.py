import os
import faiss
import ollama
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


MODEL = "gemma3:4b"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

DOCUMENT_FOLDER = "documents"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 4


print("Loading embedding model...")
embedder = SentenceTransformer(EMBEDDING_MODEL)


def read_pdf(path):
    reader = PdfReader(path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def split_text(text):
    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def load_documents():

    all_chunks = []

    for filename in os.listdir(DOCUMENT_FOLDER):

        path = os.path.join(
            DOCUMENT_FOLDER,
            filename
        )

        if filename.lower().endswith(".pdf"):

            print(f"Reading: {filename}")

            text = read_pdf(path)

            chunks = split_text(text)

            all_chunks.extend(chunks)

    return all_chunks


def create_index(chunks):

    embeddings = embedder.encode(
        chunks,
        convert_to_numpy=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def retrieve(question, chunks, index):

    question_embedding = embedder.encode(
        [question],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        question_embedding,
        min(TOP_K, len(chunks))
    )

    results = []

    for i in indices[0]:

        if i < len(chunks):

            results.append(chunks[i])

    return results


def ask_model(question, context):

    prompt = f"""
You are Thunderbolt.ai.

Answer the user's question using the provided document context.

If the answer is not present in the context, clearly say:
"I could not find that information in the document."

Do not invent information.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
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


# --------------------------------------------------
# START
# --------------------------------------------------

if not os.path.exists(DOCUMENT_FOLDER):

    os.makedirs(DOCUMENT_FOLDER)

    print()
    print("Created documents folder.")
    print("Put your PDF inside:")
    print("documents/")
    print()
    exit()


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

    exit()


print()
print(f"Document chunks: {len(chunks)}")
print("Creating vector index...")

index = create_index(chunks)

print("Index ready.")
print()
print("Ask questions about your document.")
print("Type 'exit' to quit.")
print()


while True:

    question = input("You: ")

    if question.lower() == "exit":
        break

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
    print("Thunderbolt.ai:")
    print(answer)
    print()