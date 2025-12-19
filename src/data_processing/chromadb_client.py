"""
ChromaDB client and collection management for pharmaceutical data.

This module provides the interface for connecting to ChromaDB, managing collections,
and performing health checks for the pharmaceutical intelligence system.
"""

import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import json
import os
from pathlib import Path

from src.models.documents import NewsDocument, DrugShortageDocument, DocumentType


logger = logging.getLogger(__name__)


class ChromaDBClient:
    """
    ChromaDB client for managing pharmaceutical data collections.
    
    Handles connection management, collection setup, and health monitoring
    for news and drug shortage data storage and retrieval.
    """
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 8000,
        persist_directory: Optional[str] = None
    ):
        """
        Initialize ChromaDB client.
        
        Args:
            host: ChromaDB server host
            port: ChromaDB server port
            persist_directory: Directory for persistent storage (if using local mode)
        """
        self.host = host
        self.port = port
        self.persist_directory = persist_directory or "./chroma_db"
        self.client: Optional[chromadb.Client] = None
        self.collections: Dict[str, Collection] = {}
        
        # Collection names
        self.NEWS_COLLECTION = "pharmaceutical_news"
        self.SHORTAGE_COLLECTION = "drug_shortages"
        
    def connect(self) -> bool:
        """
        Establish connection to ChromaDB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Try to connect to ChromaDB server first
            try:
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=Settings(
                        chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                        chroma_client_auth_credentials="test-token"
                    )
                )
                # Test the connection
                self.client.heartbeat()
                logger.info(f"Connected to ChromaDB server at {self.host}:{self.port}")
                
            except Exception as server_error:
                logger.warning(f"Failed to connect to ChromaDB server: {server_error}")
                logger.info("Falling back to persistent client mode")
                
                # Fall back to persistent client
                Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                logger.info(f"Connected to ChromaDB in persistent mode at {self.persist_directory}")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from ChromaDB."""
        if self.client:
            self.client = None
            self.collections.clear()
            logger.info("Disconnected from ChromaDB")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on ChromaDB connection and collections.
        
        Returns:
            Dict containing health status information
        """
        health_status = {
            "connected": False,
            "collections": {},
            "total_documents": 0,
            "last_check": datetime.now().isoformat(),
            "errors": []
        }
        
        try:
            if not self.client:
                health_status["errors"].append("No client connection")
                return health_status
                
            # Test basic connection
            try:
                if hasattr(self.client, 'heartbeat'):
                    self.client.heartbeat()
                health_status["connected"] = True
            except Exception as e:
                health_status["errors"].append(f"Heartbeat failed: {e}")
                return health_status
                
            # Check collections
            try:
                collections = self.client.list_collections()
                for collection in collections:
                    collection_name = collection.name
                    try:
                        count = collection.count()
                        health_status["collections"][collection_name] = {
                            "document_count": count,
                            "status": "healthy"
                        }
                        health_status["total_documents"] += count
                    except Exception as e:
                        health_status["collections"][collection_name] = {
                            "document_count": 0,
                            "status": "error",
                            "error": str(e)
                        }
                        health_status["errors"].append(f"Collection {collection_name} error: {e}")
                        
            except Exception as e:
                health_status["errors"].append(f"Failed to list collections: {e}")
                
        except Exception as e:
            health_status["errors"].append(f"Health check failed: {e}")
            
        return health_status
    
    def setup_collections(self) -> bool:
        """
        Set up collections for news and drug shortage data.
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        if not self.client:
            logger.error("No ChromaDB client connection")
            return False
            
        try:
            # Setup news collection
            news_metadata = {
                "hnsw:space": "cosine",
                "description": "Pharmaceutical news and regulatory information",
                "data_type": "news",
                "created_at": datetime.now().isoformat()
            }
            
            try:
                news_collection = self.client.get_collection(
                    name=self.NEWS_COLLECTION
                )
                logger.info(f"Found existing news collection: {self.NEWS_COLLECTION}")
            except Exception:
                news_collection = self.client.create_collection(
                    name=self.NEWS_COLLECTION,
                    metadata=news_metadata
                )
                logger.info(f"Created news collection: {self.NEWS_COLLECTION}")
                
            self.collections[self.NEWS_COLLECTION] = news_collection
            
            # Setup drug shortage collection
            shortage_metadata = {
                "hnsw:space": "cosine",
                "description": "Drug shortage and supply chain information",
                "data_type": "shortage",
                "created_at": datetime.now().isoformat()
            }
            
            try:
                shortage_collection = self.client.get_collection(
                    name=self.SHORTAGE_COLLECTION
                )
                logger.info(f"Found existing shortage collection: {self.SHORTAGE_COLLECTION}")
            except Exception:
                shortage_collection = self.client.create_collection(
                    name=self.SHORTAGE_COLLECTION,
                    metadata=shortage_metadata
                )
                logger.info(f"Created shortage collection: {self.SHORTAGE_COLLECTION}")
                
            self.collections[self.SHORTAGE_COLLECTION] = shortage_collection
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup collections: {e}")
            return False
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        Get a collection by name.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection object or None if not found
        """
        if collection_name in self.collections:
            return self.collections[collection_name]
            
        if not self.client:
            logger.error("No ChromaDB client connection")
            return None
            
        try:
            collection = self.client.get_collection(name=collection_name)
            self.collections[collection_name] = collection
            return collection
        except Exception as e:
            logger.error(f"Failed to get collection {collection_name}: {e}")
            return None
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary containing collection statistics
        """
        stats = {
            "name": collection_name,
            "exists": False,
            "document_count": 0,
            "metadata": {},
            "error": None
        }
        
        try:
            collection = self.get_collection(collection_name)
            if collection:
                stats["exists"] = True
                stats["document_count"] = collection.count()
                stats["metadata"] = collection.metadata or {}
            else:
                stats["error"] = "Collection not found"
                
        except Exception as e:
            stats["error"] = str(e)
            logger.error(f"Failed to get stats for collection {collection_name}: {e}")
            
        return stats
    
    def reset_collections(self) -> bool:
        """
        Reset all collections (delete and recreate).
        
        WARNING: This will delete all data!
        
        Returns:
            bool: True if reset successful, False otherwise
        """
        if not self.client:
            logger.error("No ChromaDB client connection")
            return False
            
        try:
            # Delete existing collections
            for collection_name in [self.NEWS_COLLECTION, self.SHORTAGE_COLLECTION]:
                try:
                    self.client.delete_collection(name=collection_name)
                    logger.info(f"Deleted collection: {collection_name}")
                except Exception as e:
                    logger.warning(f"Failed to delete collection {collection_name}: {e}")
                    
            # Clear local collection cache
            self.collections.clear()
            
            # Recreate collections
            return self.setup_collections()
            
        except Exception as e:
            logger.error(f"Failed to reset collections: {e}")
            return False
    
    def add_documents(
        self, 
        collection_name: str, 
        documents: List[DocumentType],
        embeddings: List[List[float]],
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to a collection with embeddings.
        
        Args:
            collection_name: Name of the target collection
            documents: List of document objects
            embeddings: List of embedding vectors
            batch_size: Number of documents to process in each batch
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not documents or not embeddings:
            logger.warning("No documents or embeddings provided")
            return True
            
        if len(documents) != len(embeddings):
            logger.error("Number of documents must match number of embeddings")
            return False
            
        collection = self.get_collection(collection_name)
        if not collection:
            logger.error(f"Collection {collection_name} not found")
            return False
            
        try:
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                
                # Prepare data for ChromaDB
                ids = []
                metadatas = []
                documents_text = []
                
                for doc in batch_docs:
                    if isinstance(doc, NewsDocument):
                        doc_id = f"news_{doc.id}"
                        # Create searchable text from title and content
                        text_content = f"{doc.title} {doc.content_html}"
                        metadata = {
                            "type": "news",
                            "id": doc.id,
                            "title": doc.title,
                            "date": doc.date,
                            "countries": json.dumps(doc.countries),
                            "regions": json.dumps(doc.regions),
                            "therapeutic_areas": json.dumps(doc.therapeutic_areas),
                            "keywords": json.dumps(doc.keywords),
                            "topic": doc.topic,
                            "source": doc.source
                        }
                    elif isinstance(doc, DrugShortageDocument):
                        doc_id = f"shortage_{hash(doc.product_name + doc.ingredient + doc.date_reported)}"
                        # Create searchable text from product name and ingredient
                        text_content = f"{doc.product_name} {doc.ingredient} {doc.manufacturer} {doc.reason}"
                        metadata = {
                            "type": "shortage",
                            "product_name": doc.product_name,
                            "ingredient": doc.ingredient,
                            "status": doc.status,
                            "date_reported": doc.date_reported,
                            "manufacturer": doc.manufacturer,
                            "source": doc.source,
                            "source_country": doc.source_country
                        }
                    else:
                        logger.error(f"Unknown document type: {type(doc)}")
                        continue
                        
                    ids.append(doc_id)
                    metadatas.append(metadata)
                    documents_text.append(text_content)
                
                # Add batch to collection
                if ids:  # Only add if we have valid documents
                    collection.add(
                        ids=ids,
                        embeddings=batch_embeddings[:len(ids)],  # Match the number of valid documents
                        metadatas=metadatas,
                        documents=documents_text
                    )
                    
                logger.info(f"Added batch of {len(ids)} documents to {collection_name}")
                
            logger.info(f"Successfully added {len(documents)} documents to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to {collection_name}: {e}")
            return False
    
    def query_collection(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        include: List[str] = ["metadatas", "documents", "distances"]
    ) -> Optional[Dict[str, Any]]:
        """
        Query a collection with embedding vectors.
        
        Args:
            collection_name: Name of the collection to query
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            where: Metadata filter conditions
            include: What to include in results
            
        Returns:
            Query results or None if failed
        """
        collection = self.get_collection(collection_name)
        if not collection:
            logger.error(f"Collection {collection_name} not found")
            return None
            
        try:
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=include
            )
            return results
            
        except Exception as e:
            logger.error(f"Failed to query collection {collection_name}: {e}")
            return None


def create_chromadb_client(
    host: str = "localhost",
    port: int = 8000,
    persist_directory: Optional[str] = None
) -> ChromaDBClient:
    """
    Factory function to create and initialize a ChromaDB client.
    
    Args:
        host: ChromaDB server host
        port: ChromaDB server port
        persist_directory: Directory for persistent storage
        
    Returns:
        Initialized ChromaDBClient instance
    """
    client = ChromaDBClient(host=host, port=port, persist_directory=persist_directory)
    
    if client.connect():
        if client.setup_collections():
            logger.info("ChromaDB client initialized successfully")
            return client
        else:
            logger.error("Failed to setup collections")
    else:
        logger.error("Failed to connect to ChromaDB")
        
    return client  # Return client even if setup failed, for error handling