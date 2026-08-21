import pytest
import rag


def test_load_documents():
    chunks = rag.load_documents()

    assert chunks is not None
    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_document_chunks_are_strings():
    chunks = rag.load_documents()

    assert len(chunks) > 0

    for chunk in chunks:
        assert isinstance(chunk, str)
        assert len(chunk.strip()) > 0


def test_ask_document():
    question = "What GPU was used in the benchmark?"

    answer = rag.ask_document(question)

    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer.strip()) > 0


def test_ask_document_python():
    question = "What is Python?"

    answer = rag.ask_document(question)

    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer.strip()) > 0