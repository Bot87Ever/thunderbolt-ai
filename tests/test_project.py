import os


def test_documents_folder_exists():
    assert os.path.exists("documents")
    assert os.path.isdir("documents")


def test_requirements_exists():
    assert os.path.exists("requirements.txt")


def test_readme_exists():
    assert os.path.exists("README.md")


def test_main_exists():
    assert os.path.exists("main.py")


def test_rag_exists():
    assert os.path.exists("rag.py")