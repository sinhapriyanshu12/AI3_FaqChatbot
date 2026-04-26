from pathlib import Path
import shutil

import pytest

from agents.vector_store import build_store, load_store


@pytest.fixture(scope="session")
def built_store():
    docs_folder = Path("data/raw")
    index_path = Path("data/processed/test_index")
    if index_path.exists():
        shutil.rmtree(index_path)
    build_store(str(docs_folder), str(index_path))
    store = load_store(str(index_path))
    yield store
    if index_path.exists():
        shutil.rmtree(index_path)
