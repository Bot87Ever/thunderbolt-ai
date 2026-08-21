import rag


def test_load_documents():
    chunks = rag.load_documents()
    assert chunks
    assert isinstance(chunks, list)


def test_document_chunks_are_strings():
    chunks = rag.load_documents()
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_ask_document(monkeypatch):
    def fake_ask_model(question, context):
        return "Test answer"

    monkeypatch.setattr(rag, "ask_model", fake_ask_model)

    result = rag.ask_document("What is Python?")

    assert isinstance(result, str)
    assert result == "Test answer"


def test_ask_document_python(monkeypatch):
    def fake_ask_model(question, context):
        return "Python is a programming language."

    monkeypatch.setattr(rag, "ask_model", fake_ask_model)

    result = rag.ask_document("What is Python?")

    assert "Python" in result