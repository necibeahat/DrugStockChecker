"""
Embedding generation service using Amazon Titan.

This module handles text embedding generation for pharmaceutical documents,
with batch processing, retry logic, and error handling for API calls.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import json

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of an embedding generation operation."""
    text: str
    embedding: List[float]
    success: bool
    error: Optional[str] = None


class EmbeddingService:
    """
    Service for generating text embeddings using Amazon Titan.
    
    Provides batch processing capabilities with automatic retry logic
    and comprehensive error handling for production use.
    """
    
    def __init__(
        self,
        model_id: str = "amazon.titan-embed-text-v2:0",
        region_name: str = "us-east-1",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        batch_size: int = 25
    ):
        """
        Initialize the embedding service.
        
        Args:
            model_id: Amazon Titan embedding model ID
            region_name: AWS region for Bedrock service
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Initial delay between retries in seconds (uses exponential backoff)
            batch_size: Number of texts to process in each batch
        """
        self.model_id = model_id
        self.region_name = region_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.batch_size = batch_size
        
        # Initialize Bedrock client
        try:
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=region_name
            )
            logger.info(f"Initialized Bedrock client for region {region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
        
        # Statistics tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_retries = 0
    
    def generate_embedding(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            EmbeddingResult: Result containing embedding or error information
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return EmbeddingResult(
                text=text,
                embedding=[],
                success=False,
                error="Empty text provided"
            )
        
        # Truncate text if too long (Titan has a limit)
        max_length = 8000  # Conservative limit for Titan
        if len(text) > max_length:
            logger.warning(f"Text too long ({len(text)} chars), truncating to {max_length}")
            text = text[:max_length]
        
        self.total_requests += 1
        
        for attempt in range(self.max_retries):
            try:
                # Prepare request body
                request_body = {
                    "inputText": text
                }
                
                # Call Bedrock API
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body),
                    contentType='application/json',
                    accept='application/json'
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                embedding = response_body.get('embedding', [])
                
                if not embedding:
                    raise ValueError("Empty embedding returned from API")
                
                self.successful_requests += 1
                return EmbeddingResult(
                    text=text,
                    embedding=embedding,
                    success=True
                )
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                error_message = e.response.get('Error', {}).get('Message', str(e))
                
                logger.warning(
                    f"Bedrock API error (attempt {attempt + 1}/{self.max_retries}): "
                    f"{error_code} - {error_message}"
                )
                
                # Check if error is retryable
                if error_code in ['ThrottlingException', 'ServiceUnavailable', 'InternalServerError']:
                    if attempt < self.max_retries - 1:
                        self.total_retries += 1
                        delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Retrying after {delay} seconds...")
                        time.sleep(delay)
                        continue
                
                # Non-retryable error or max retries reached
                self.failed_requests += 1
                return EmbeddingResult(
                    text=text,
                    embedding=[],
                    success=False,
                    error=f"{error_code}: {error_message}"
                )
                
            except Exception as e:
                logger.error(f"Unexpected error generating embedding (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    self.total_retries += 1
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                
                self.failed_requests += 1
                return EmbeddingResult(
                    text=text,
                    embedding=[],
                    success=False,
                    error=str(e)
                )
        
        # Should not reach here, but just in case
        self.failed_requests += 1
        return EmbeddingResult(
            text=text,
            embedding=[],
            success=False,
            error="Max retries exceeded"
        )
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        show_progress: bool = True
    ) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts with batch processing.
        
        Args:
            texts: List of texts to generate embeddings for
            show_progress: Whether to log progress information
            
        Returns:
            List[EmbeddingResult]: Results for all texts
        """
        if not texts:
            logger.warning("Empty text list provided for batch embedding generation")
            return []
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        results = []
        
        # Process in batches to avoid overwhelming the API
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
            
            if show_progress:
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")
            
            for text in batch:
                result = self.generate_embedding(text)
                results.append(result)
            
            # Small delay between batches to avoid rate limiting
            if i + self.batch_size < len(texts):
                time.sleep(0.1)
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(
            f"Batch embedding generation complete: "
            f"{successful} successful, {failed} failed"
        )
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about embedding generation operations.
        
        Returns:
            Dict containing operation statistics
        """
        success_rate = (
            self.successful_requests / self.total_requests
            if self.total_requests > 0 else 0
        )
        
        avg_retries = (
            self.total_retries / self.total_requests
            if self.total_requests > 0 else 0
        )
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'total_retries': self.total_retries,
            'success_rate': success_rate,
            'average_retries_per_request': avg_retries
        }
    
    def reset_statistics(self):
        """Reset all statistics counters."""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_retries = 0
        logger.info("Statistics reset")
    
    def test_connection(self) -> bool:
        """
        Test the connection to Bedrock service.
        
        Returns:
            bool: True if connection is successful
        """
        try:
            test_text = "This is a test."
            result = self.generate_embedding(test_text)
            
            if result.success:
                logger.info("Bedrock connection test successful")
                return True
            else:
                logger.error(f"Bedrock connection test failed: {result.error}")
                return False
                
        except Exception as e:
            logger.error(f"Bedrock connection test failed with exception: {e}")
            return False


def create_embedding_text(document: Any) -> str:
    """
    Create a comprehensive text representation of a document for embedding.
    
    Args:
        document: NewsDocument or DrugShortageDocument instance
        
    Returns:
        str: Text suitable for embedding generation
    """
    from src.models.documents import NewsDocument, DrugShortageDocument
    
    if isinstance(document, NewsDocument):
        # Combine key fields for news documents
        parts = [
            f"Title: {document.title}",
            f"Date: {document.date}",
            f"Countries: {', '.join(document.countries)}",
            f"Regions: {', '.join(document.regions)}",
            f"Therapeutic Areas: {', '.join(document.therapeutic_areas)}",
            f"Indications: {', '.join(document.indications)}",
            f"Keywords: {', '.join(document.keywords)}",
            f"Product Groups: {', '.join(document.product_groups)}",
            f"Content: {document.content_html}"
        ]
        
        # Add companies if available
        if document.companies:
            parts.insert(3, f"Companies: {', '.join(document.companies)}")
        
        # Add generic names if available
        if document.generic_names:
            parts.insert(4, f"Generic Names: {', '.join(document.generic_names)}")
        
        return "\n".join(parts)
        
    elif isinstance(document, DrugShortageDocument):
        # Combine key fields for shortage documents
        parts = [
            f"Product: {document.product_name}",
            f"Ingredient: {document.ingredient}",
            f"Manufacturer: {document.manufacturer}",
            f"Status: {document.status}",
            f"Date Reported: {document.date_reported}",
            f"Source Country: {document.source_country}",
            f"Source: {document.source}"
        ]
        
        # Add reason if available
        if document.reason:
            parts.append(f"Reason: {document.reason}")
        
        # Add expected resolution if available
        if document.expected_resolution:
            parts.append(f"Expected Resolution: {document.expected_resolution}")
        
        return "\n".join(parts)
    
    else:
        raise ValueError(f"Unsupported document type: {type(document)}")