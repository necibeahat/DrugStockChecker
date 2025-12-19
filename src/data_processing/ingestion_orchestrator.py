"""
Data ingestion orchestrator.

This module coordinates parsing, embedding generation, and database insertion
for pharmaceutical data, providing progress tracking, completion statistics,
and duplicate detection and handling.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import hashlib

from src.data_processing.navlin_parser import NavlinNewsParser
from src.data_processing.shortage_parser import DrugShortageParser
from src.data_processing.embedding_service import EmbeddingService, create_embedding_text
from src.data_processing.chromadb_client import ChromaDBClient
from src.models.documents import NewsDocument, DrugShortageDocument, DocumentType

logger = logging.getLogger(__name__)


@dataclass
class IngestionStats:
    """Statistics for a data ingestion operation."""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_documents: int = 0
    processed_documents: int = 0
    failed_documents: int = 0
    duplicates_found: int = 0
    duplicates_updated: int = 0
    embedding_failures: int = 0
    database_failures: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the ingestion process in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Get the success rate for document processing."""
        if self.total_documents == 0:
            return 0.0
        return self.processed_documents / self.total_documents


class DataIngestionOrchestrator:
    """
    Orchestrates the complete data ingestion pipeline.
    
    Coordinates parsing of JSON files, embedding generation, and database insertion
    with comprehensive progress tracking and error handling.
    """
    
    def __init__(
        self,
        chromadb_client: ChromaDBClient,
        embedding_service: EmbeddingService,
        duplicate_threshold: float = 0.95
    ):
        """
        Initialize the ingestion orchestrator.
        
        Args:
            chromadb_client: ChromaDB client for database operations
            embedding_service: Service for generating embeddings
            duplicate_threshold: Similarity threshold for duplicate detection (0.0-1.0)
        """
        self.chromadb_client = chromadb_client
        self.embedding_service = embedding_service
        self.duplicate_threshold = duplicate_threshold
        
        # Initialize parsers
        self.navlin_parser = NavlinNewsParser()
        self.shortage_parser = DrugShortageParser()
        
        # Track processed document hashes for duplicate detection
        self.processed_hashes: Set[str] = set()
        
        # Statistics
        self.stats = IngestionStats()
    
    def ingest_data_directory(
        self,
        data_directory: str,
        show_progress: bool = True
    ) -> IngestionStats:
        """
        Ingest all pharmaceutical data from a directory.
        
        Args:
            data_directory: Path to directory containing data files
            show_progress: Whether to show progress information
            
        Returns:
            IngestionStats: Complete statistics for the ingestion process
        """
        data_path = Path(data_directory)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_directory}")
        
        logger.info(f"Starting data ingestion from {data_directory}")
        self.stats = IngestionStats()
        self.stats.start_time = datetime.now()
        
        try:
            # Load existing document hashes for duplicate detection
            self._load_existing_hashes()
            
            # Process Navlin News data
            navlin_dir = data_path / "Navlin News"
            if navlin_dir.exists():
                logger.info("Processing Navlin News data...")
                self._ingest_navlin_news(str(navlin_dir), show_progress)
            else:
                logger.warning("Navlin News directory not found")
            
            # Process drug shortage data
            shortage_files = list(data_path.glob("*shortage*.json"))
            if shortage_files:
                logger.info(f"Processing {len(shortage_files)} drug shortage files...")
                for shortage_file in shortage_files:
                    self._ingest_shortage_file(str(shortage_file), show_progress)
            else:
                logger.warning("No drug shortage files found")
            
            self.stats.end_time = datetime.now()
            
            # Log final statistics
            self._log_final_stats()
            
            return self.stats
            
        except Exception as e:
            self.stats.end_time = datetime.now()
            logger.error(f"Data ingestion failed: {e}")
            raise
    
    def ingest_navlin_news_file(
        self,
        file_path: str,
        show_progress: bool = True
    ) -> IngestionStats:
        """
        Ingest a single Navlin News file.
        
        Args:
            file_path: Path to the Navlin News JSON file
            show_progress: Whether to show progress information
            
        Returns:
            IngestionStats: Statistics for the ingestion process
        """
        logger.info(f"Ingesting Navlin News file: {file_path}")
        self.stats = IngestionStats()
        self.stats.start_time = datetime.now()
        
        try:
            self._load_existing_hashes()
            self._ingest_navlin_news_file(file_path, show_progress)
            self.stats.end_time = datetime.now()
            self._log_final_stats()
            return self.stats
            
        except Exception as e:
            self.stats.end_time = datetime.now()
            logger.error(f"Navlin News file ingestion failed: {e}")
            raise
    
    def ingest_shortage_file(
        self,
        file_path: str,
        show_progress: bool = True
    ) -> IngestionStats:
        """
        Ingest a single drug shortage file.
        
        Args:
            file_path: Path to the drug shortage JSON file
            show_progress: Whether to show progress information
            
        Returns:
            IngestionStats: Statistics for the ingestion process
        """
        logger.info(f"Ingesting drug shortage file: {file_path}")
        self.stats = IngestionStats()
        self.stats.start_time = datetime.now()
        
        try:
            self._load_existing_hashes()
            self._ingest_shortage_file(file_path, show_progress)
            self.stats.end_time = datetime.now()
            self._log_final_stats()
            return self.stats
            
        except Exception as e:
            self.stats.end_time = datetime.now()
            logger.error(f"Drug shortage file ingestion failed: {e}")
            raise
    
    def _ingest_navlin_news(self, directory_path: str, show_progress: bool):
        """Ingest all Navlin News files from a directory."""
        try:
            documents = self.navlin_parser.parse_directory(directory_path)
            self.stats.total_documents += len(documents)
            
            if documents:
                self._process_documents(documents, "news", show_progress)
                
            # Update file statistics
            parser_stats = self.navlin_parser.get_parsing_stats()
            if parser_stats['processed_count'] > 0:
                self.stats.processed_files += 1
            if parser_stats['error_count'] > 0:
                self.stats.failed_files += 1
                
        except Exception as e:
            self.stats.failed_files += 1
            logger.error(f"Failed to process Navlin News directory: {e}")
            raise
    
    def _ingest_navlin_news_file(self, file_path: str, show_progress: bool):
        """Ingest a single Navlin News file."""
        try:
            documents = self.navlin_parser.parse_file(file_path)
            self.stats.total_files += 1
            self.stats.total_documents += len(documents)
            
            if documents:
                self._process_documents(documents, "news", show_progress)
                self.stats.processed_files += 1
            else:
                self.stats.failed_files += 1
                
        except Exception as e:
            self.stats.failed_files += 1
            logger.error(f"Failed to process Navlin News file {file_path}: {e}")
            raise
    
    def _ingest_shortage_file(self, file_path: str, show_progress: bool):
        """Ingest a single drug shortage file."""
        try:
            documents = self.shortage_parser.parse_file(file_path)
            self.stats.total_files += 1
            self.stats.total_documents += len(documents)
            
            if documents:
                self._process_documents(documents, "shortages", show_progress)
                self.stats.processed_files += 1
            else:
                self.stats.failed_files += 1
                
        except Exception as e:
            self.stats.failed_files += 1
            logger.error(f"Failed to process shortage file {file_path}: {e}")
            raise
    
    def _process_documents(
        self,
        documents: List[DocumentType],
        collection_name: str,
        show_progress: bool
    ):
        """Process a batch of documents through the complete pipeline."""
        if not documents:
            return
        
        logger.info(f"Processing {len(documents)} documents for {collection_name} collection")
        
        # Filter out duplicates
        unique_documents = []
        for doc in documents:
            doc_hash = self._calculate_document_hash(doc)
            
            if doc_hash in self.processed_hashes:
                self.stats.duplicates_found += 1
                if show_progress and self.stats.duplicates_found % 10 == 0:
                    logger.info(f"Found {self.stats.duplicates_found} duplicates so far")
                continue
            
            unique_documents.append(doc)
            self.processed_hashes.add(doc_hash)
        
        if not unique_documents:
            logger.info("No new documents to process (all duplicates)")
            return
        
        logger.info(f"Processing {len(unique_documents)} unique documents")
        
        # Generate embeddings
        embedding_texts = [create_embedding_text(doc) for doc in unique_documents]
        embedding_results = self.embedding_service.generate_embeddings_batch(
            embedding_texts, show_progress
        )
        
        # Prepare documents for database insertion
        documents_to_insert = []
        metadatas = []
        embeddings = []
        ids = []
        
        for i, (doc, embedding_result) in enumerate(zip(unique_documents, embedding_results)):
            if not embedding_result.success:
                self.stats.embedding_failures += 1
                self.stats.failed_documents += 1
                logger.warning(f"Failed to generate embedding for document: {embedding_result.error}")
                continue
            
            # Create document ID
            doc_id = self._create_document_id(doc, collection_name)
            
            # Create metadata
            metadata = self._create_document_metadata(doc)
            
            documents_to_insert.append(embedding_result.text)
            metadatas.append(metadata)
            embeddings.append(embedding_result.embedding)
            ids.append(doc_id)
        
        # Insert into database
        if documents_to_insert:
            try:
                self.chromadb_client.add_documents(
                    collection_name=collection_name,
                    documents=documents_to_insert,
                    metadatas=metadatas,
                    embeddings=embeddings,
                    ids=ids
                )
                
                self.stats.processed_documents += len(documents_to_insert)
                logger.info(f"Successfully inserted {len(documents_to_insert)} documents")
                
            except Exception as e:
                self.stats.database_failures += len(documents_to_insert)
                self.stats.failed_documents += len(documents_to_insert)
                logger.error(f"Failed to insert documents into database: {e}")
                raise
    
    def _calculate_document_hash(self, document: DocumentType) -> str:
        """Calculate a hash for duplicate detection."""
        if isinstance(document, NewsDocument):
            # Use ID and title for news documents
            content = f"{document.id}:{document.title}:{document.date}"
        elif isinstance(document, DrugShortageDocument):
            # Use product name, ingredient, and date for shortage documents
            content = f"{document.product_name}:{document.ingredient}:{document.date_reported}"
        else:
            raise ValueError(f"Unsupported document type: {type(document)}")
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _create_document_id(self, document: DocumentType, collection_name: str) -> str:
        """Create a unique document ID."""
        if isinstance(document, NewsDocument):
            return f"{collection_name}_{document.id}"
        elif isinstance(document, DrugShortageDocument):
            # Create ID from hash since shortage documents don't have unique IDs
            doc_hash = self._calculate_document_hash(document)
            return f"{collection_name}_{doc_hash[:12]}"
        else:
            raise ValueError(f"Unsupported document type: {type(document)}")
    
    def _create_document_metadata(self, document: DocumentType) -> Dict[str, Any]:
        """Create metadata dictionary for a document."""
        if isinstance(document, NewsDocument):
            return {
                'document_type': 'news',
                'source': document.source,
                'id': document.id,
                'title': document.title,
                'date': document.date,
                'countries': document.countries,
                'regions': document.regions,
                'therapeutic_areas': document.therapeutic_areas,
                'indications': document.indications,
                'keywords': document.keywords,
                'product_groups': document.product_groups
            }
        elif isinstance(document, DrugShortageDocument):
            return {
                'document_type': 'shortage',
                'source': document.source,
                'product_name': document.product_name,
                'ingredient': document.ingredient,
                'matched_ingredient': document.matched_ingredient,
                'status': document.status,
                'date_reported': document.date_reported,
                'manufacturer': document.manufacturer,
                'source_country': document.source_country
            }
        else:
            raise ValueError(f"Unsupported document type: {type(document)}")
    
    def _load_existing_hashes(self):
        """Load existing document hashes from the database for duplicate detection."""
        try:
            # Get existing documents from both collections
            existing_hashes = set()
            
            # Check news collection
            try:
                news_results = self.chromadb_client.query_collection(
                    collection_name="news",
                    query_texts=[""],
                    n_results=10000,  # Large number to get all documents
                    include=['metadatas']
                )
                
                for metadata in news_results.get('metadatas', []):
                    if metadata:
                        for meta in metadata:
                            if 'id' in meta and 'title' in meta and 'date' in meta:
                                content = f"{meta['id']}:{meta['title']}:{meta['date']}"
                                doc_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                                existing_hashes.add(doc_hash)
                                
            except Exception as e:
                logger.warning(f"Could not load existing news hashes: {e}")
            
            # Check shortages collection
            try:
                shortage_results = self.chromadb_client.query_collection(
                    collection_name="shortages",
                    query_texts=[""],
                    n_results=10000,  # Large number to get all documents
                    include=['metadatas']
                )
                
                for metadata in shortage_results.get('metadatas', []):
                    if metadata:
                        for meta in metadata:
                            if 'product_name' in meta and 'ingredient' in meta and 'date_reported' in meta:
                                content = f"{meta['product_name']}:{meta['ingredient']}:{meta['date_reported']}"
                                doc_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                                existing_hashes.add(doc_hash)
                                
            except Exception as e:
                logger.warning(f"Could not load existing shortage hashes: {e}")
            
            self.processed_hashes = existing_hashes
            logger.info(f"Loaded {len(existing_hashes)} existing document hashes for duplicate detection")
            
        except Exception as e:
            logger.warning(f"Could not load existing hashes: {e}")
            self.processed_hashes = set()
    
    def _log_final_stats(self):
        """Log final ingestion statistics."""
        duration = self.stats.duration
        duration_str = f"{duration:.2f} seconds" if duration else "unknown"
        
        logger.info("=" * 60)
        logger.info("DATA INGESTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration_str}")
        logger.info(f"Files processed: {self.stats.processed_files}/{self.stats.total_files}")
        logger.info(f"Documents processed: {self.stats.processed_documents}/{self.stats.total_documents}")
        logger.info(f"Success rate: {self.stats.success_rate:.2%}")
        logger.info(f"Duplicates found: {self.stats.duplicates_found}")
        logger.info(f"Embedding failures: {self.stats.embedding_failures}")
        logger.info(f"Database failures: {self.stats.database_failures}")
        
        if self.stats.failed_documents > 0:
            logger.warning(f"Failed to process {self.stats.failed_documents} documents")
        
        logger.info("=" * 60)
    
    def get_statistics(self) -> IngestionStats:
        """Get the current ingestion statistics."""
        return self.stats