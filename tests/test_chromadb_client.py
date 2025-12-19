"""
Tests for ChromaDB client functionality.
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from src.data_processing.chromadb_client import ChromaDBClient, create_chromadb_client
from src.models.documents import NewsDocument, DrugShortageDocument


class TestChromaDBClient:
    """Test cases for ChromaDBClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.client = ChromaDBClient(persist_directory=self.temp_dir)
        
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test ChromaDBClient initialization."""
        client = ChromaDBClient(host="test_host", port=9000)
        
        assert client.host == "test_host"
        assert client.port == 9000
        assert client.client is None
        assert client.collections == {}
        assert client.NEWS_COLLECTION == "pharmaceutical_news"
        assert client.SHORTAGE_COLLECTION == "drug_shortages"
    
    @patch('chromadb.PersistentClient')
    def test_connect_persistent_mode(self, mock_persistent_client):
        """Test connection in persistent mode."""
        mock_client = Mock()
        mock_persistent_client.return_value = mock_client
        
        result = self.client.connect()
        
        assert result is True
        assert self.client.client == mock_client
        mock_persistent_client.assert_called_once()
    
    def test_disconnect(self):
        """Test disconnection."""
        self.client.client = Mock()
        self.client.collections = {"test": Mock()}
        
        self.client.disconnect()
        
        assert self.client.client is None
        assert self.client.collections == {}
    
    def test_health_check_no_client(self):
        """Test health check with no client connection."""
        result = self.client.health_check()
        
        assert result["connected"] is False
        assert "No client connection" in result["errors"]
        assert result["total_documents"] == 0
    
    @patch('chromadb.PersistentClient')
    def test_health_check_with_client(self, mock_persistent_client):
        """Test health check with connected client."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.name = "test_collection"
        mock_collection.count.return_value = 5
        
        mock_client.list_collections.return_value = [mock_collection]
        mock_persistent_client.return_value = mock_client
        
        self.client.connect()
        result = self.client.health_check()
        
        assert result["connected"] is True
        assert result["total_documents"] == 5
        assert "test_collection" in result["collections"]
        assert result["collections"]["test_collection"]["document_count"] == 5
    
    @patch('chromadb.PersistentClient')
    def test_setup_collections(self, mock_persistent_client):
        """Test collection setup."""
        mock_client = Mock()
        mock_news_collection = Mock()
        mock_shortage_collection = Mock()
        
        # Mock creating new collections
        mock_client.get_collection.side_effect = Exception("Collection not found")
        mock_client.create_collection.side_effect = [mock_news_collection, mock_shortage_collection]
        mock_persistent_client.return_value = mock_client
        
        self.client.connect()
        result = self.client.setup_collections()
        
        assert result is True
        assert self.client.collections[self.client.NEWS_COLLECTION] == mock_news_collection
        assert self.client.collections[self.client.SHORTAGE_COLLECTION] == mock_shortage_collection
        assert mock_client.create_collection.call_count == 2
    
    @patch('chromadb.PersistentClient')
    def test_get_collection_stats(self, mock_persistent_client):
        """Test getting collection statistics."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 10
        mock_collection.metadata = {"test": "metadata"}
        
        mock_client.get_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client
        
        self.client.connect()
        result = self.client.get_collection_stats("test_collection")
        
        assert result["exists"] is True
        assert result["document_count"] == 10
        assert result["metadata"] == {"test": "metadata"}
        assert result["error"] is None
    
    @patch('chromadb.PersistentClient')
    def test_add_documents_news(self, mock_persistent_client):
        """Test adding news documents."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client
        
        # Create test news document
        news_doc = NewsDocument(
            id=12345,
            title="Test News",
            date="2025-12-19",
            countries=["DENMARK"],
            content_html="<p>Test content</p>"
        )
        
        embeddings = [[0.1, 0.2, 0.3]]
        
        self.client.connect()
        result = self.client.add_documents("test_collection", [news_doc], embeddings)
        
        assert result is True
        mock_collection.add.assert_called_once()
        
        # Check the call arguments
        call_args = mock_collection.add.call_args
        assert len(call_args.kwargs['ids']) == 1
        assert call_args.kwargs['ids'][0] == "news_12345"
        assert call_args.kwargs['metadatas'][0]['type'] == "news"
        assert call_args.kwargs['metadatas'][0]['title'] == "Test News"
    
    @patch('chromadb.PersistentClient')
    def test_add_documents_shortage(self, mock_persistent_client):
        """Test adding drug shortage documents."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client
        
        # Create test shortage document
        shortage_doc = DrugShortageDocument(
            product_name="Test Product",
            ingredient="Test Ingredient",
            matched_ingredient="Test Ingredient",
            status="Shortage",
            date_reported="2025-12-11",
            reason="Test reason",
            source_url="https://example.com",
            manufacturer="Test Manufacturer",
            expected_resolution="",
            source="Test Source",
            source_country="CA",
            scraped_at="2025-12-16T21:37:47.403152"
        )
        
        embeddings = [[0.1, 0.2, 0.3]]
        
        self.client.connect()
        result = self.client.add_documents("test_collection", [shortage_doc], embeddings)
        
        assert result is True
        mock_collection.add.assert_called_once()
        
        # Check the call arguments
        call_args = mock_collection.add.call_args
        assert len(call_args.kwargs['ids']) == 1
        assert call_args.kwargs['metadatas'][0]['type'] == "shortage"
        assert call_args.kwargs['metadatas'][0]['product_name'] == "Test Product"
    
    @patch('chromadb.PersistentClient')
    def test_query_collection(self, mock_persistent_client):
        """Test querying a collection."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_results = {"ids": [["test_id"]], "distances": [[0.5]]}
        mock_collection.query.return_value = mock_results
        mock_client.get_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client
        
        self.client.connect()
        result = self.client.query_collection(
            "test_collection", 
            [[0.1, 0.2, 0.3]], 
            n_results=5
        )
        
        assert result == mock_results
        mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]],
            n_results=5,
            where=None,
            include=["metadatas", "documents", "distances"]
        )


class TestCreateChromaDBClient:
    """Test cases for create_chromadb_client factory function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.data_processing.chromadb_client.ChromaDBClient')
    def test_create_chromadb_client(self, mock_chromadb_client):
        """Test factory function for creating ChromaDB client."""
        mock_client_instance = Mock()
        mock_client_instance.connect.return_value = True
        mock_client_instance.setup_collections.return_value = True
        mock_chromadb_client.return_value = mock_client_instance
        
        result = create_chromadb_client(host="test_host", port=9000)
        
        assert result == mock_client_instance
        mock_chromadb_client.assert_called_once_with(
            host="test_host", 
            port=9000, 
            persist_directory=None
        )
        mock_client_instance.connect.assert_called_once()
        mock_client_instance.setup_collections.assert_called_once()
    
    @patch('src.data_processing.chromadb_client.ChromaDBClient')
    def test_create_chromadb_client_connection_failure(self, mock_chromadb_client):
        """Test factory function when connection fails."""
        mock_client_instance = Mock()
        mock_client_instance.connect.return_value = False
        mock_chromadb_client.return_value = mock_client_instance
        
        result = create_chromadb_client()
        
        assert result == mock_client_instance  # Should still return client for error handling
        mock_client_instance.connect.assert_called_once()
        mock_client_instance.setup_collections.assert_not_called()  # Should not be called if connection fails