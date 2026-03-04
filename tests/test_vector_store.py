import pytest
from unittest.mock import MagicMock, patch
from src.services.vector_store import VectorStore


@pytest.fixture
def mock_chromadb():
    with patch('src.services.vector_store.chromadb.PersistentClient') as mock:
        mock_client = MagicMock()
        mock_collection = MagicMock()
        
        mock_client.get_collection.side_effect = Exception("Collection not found")
        mock_client.create_collection.return_value = mock_collection
        mock.return_value = mock_client
        
        yield mock, mock_client, mock_collection


def test_vector_store_initialization(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    
    store = VectorStore()
    
    assert store.client is not None
    assert mock_client.create_collection.call_count == 2
    mock_client.create_collection.assert_any_call("code_files")
    mock_client.create_collection.assert_any_call("historical_issues")


def test_get_or_create_collection_existing(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    mock_client.get_collection.side_effect = None
    mock_client.get_collection.return_value = mock_collection
    
    store = VectorStore()
    collection = store._get_or_create_collection("test")
    
    assert collection == mock_collection


def test_index_code_files_with_empty_list(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    
    store = VectorStore()
    store.code_collection = mock_collection
    
    store.index_code_files([], "12345")
    
    assert not mock_collection.add.called


def test_search_relevant_code(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    
    mock_collection.query.return_value = {
        "ids": [["file1_12345", "file2_12345"]],
        "documents": [["content1", "content2"]],
        "distances": [[0.1, 0.2]],
        "metadatas": [[
            {"project_id": "12345", "path": "test.py"},
            {"project_id": "12345", "path": "main.py"}
        ]]
    }
    
    store = VectorStore()
    store.code_collection = mock_collection
    results = store.search_relevant_code("test query", "12345", n_results=5)
    
    assert len(results) == 2
    assert results[0]["path"] == "test.py"
    assert results[0]["content"] == "content1"
    assert "similarity" in results[0]


def test_search_relevant_code_filters_by_threshold(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    
    mock_collection.query.return_value = {
        "ids": [["file1_12345", "file2_12345"]],
        "documents": [["content1", "content2"]],
        "distances": [[0.1, 0.9]],  # Second one above threshold
        "metadatas": [[
            {"project_id": "12345", "path": "test.py"},
            {"project_id": "12345", "path": "main.py"}
        ]]
    }
    
    store = VectorStore()
    store.code_collection = mock_collection
    results = store.search_relevant_code("test query", "12345", n_results=5)
    
    assert len(results) == 1
    assert results[0]["path"] == "test.py"


def test_search_similar_issues(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    
    mock_collection.query.return_value = {
        "ids": [["123_12345", "456_12345"]],
        "documents": [["Issue 1", "Issue 2"]],
        "distances": [[0.15, 0.25]],
        "metadatas": [[
            {"project_id": "12345", "issue_id": "123", "title": "Bug 1"},
            {"project_id": "12345", "issue_id": "456", "title": "Bug 2"}
        ]]
    }
    
    store = VectorStore()
    store.issues_collection = mock_collection
    results = store.search_similar_issues("new issue", "12345", n_results=5)
    
    assert len(results) == 2
    assert results[0]["issue_id"] == "123"
    assert results[0]["title"] == "Bug 1"
    assert "similarity" in results[0]


def test_search_handles_empty_results(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    
    mock_collection.query.return_value = {
        "ids": [[]],
        "documents": [[]],
        "distances": [[]],
        "metadatas": [[]]
    }
    
    store = VectorStore()
    results = store.search_relevant_code("test", "12345", n_results=5)
    
    assert results == []


def test_search_handles_errors(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    
    mock_collection.query.side_effect = Exception("Search error")
    
    store = VectorStore()
    results = store.search_relevant_code("test", "12345", n_results=5)
    
    assert results == []


def test_index_handles_errors(mock_chromadb):
    mock, mock_client, mock_collection = mock_chromadb
    
    mock_collection.add.side_effect = Exception("Index error")
    
    store = VectorStore()
    store.code_collection = mock_collection
    # Should not raise, just log error
    store.index_code_files([{"path": "test.py", "content": "test"}], "12345")
