#!/usr/bin/env python3
"""
Data ingestion script for pharmaceutical data.

This script provides a command-line interface for system engineers to ingest
JSON data files into ChromaDB for the pharmaceutical intelligence chatbot.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.data_processing.chromadb_client import ChromaDBClient
from src.data_processing.embedding_service import EmbeddingService
from src.data_processing.ingestion_orchestrator import DataIngestionOrchestrator


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('data_ingestion.log')
        ]
    )


def main():
    """Main entry point for the data ingestion script."""
    parser = argparse.ArgumentParser(
        description="Ingest pharmaceutical data into ChromaDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all data from the data directory
  python scripts/ingest_data.py --data-dir data/

  # Ingest a specific Navlin News file
  python scripts/ingest_data.py --navlin-file data/Navlin\ News/als_news_all.json

  # Ingest a specific drug shortage file
  python scripts/ingest_data.py --shortage-file data/drug_shortage_combined_20251216_214653.json

  # Use custom ChromaDB settings
  python scripts/ingest_data.py --data-dir data/ --chromadb-host localhost --chromadb-port 8000

  # Verbose logging
  python scripts/ingest_data.py --data-dir data/ --verbose
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--data-dir',
        type=str,
        help='Directory containing all data files to ingest'
    )
    input_group.add_argument(
        '--navlin-file',
        type=str,
        help='Specific Navlin News JSON file to ingest'
    )
    input_group.add_argument(
        '--shortage-file',
        type=str,
        help='Specific drug shortage JSON file to ingest'
    )
    
    # ChromaDB options
    parser.add_argument(
        '--chromadb-host',
        type=str,
        default='localhost',
        help='ChromaDB host (default: localhost)'
    )
    parser.add_argument(
        '--chromadb-port',
        type=int,
        default=8000,
        help='ChromaDB port (default: 8000)'
    )
    
    # Embedding service options
    parser.add_argument(
        '--aws-region',
        type=str,
        default='us-east-1',
        help='AWS region for Bedrock service (default: us-east-1)'
    )
    parser.add_argument(
        '--embedding-model',
        type=str,
        default='amazon.titan-embed-text-v2:0',
        help='Amazon Titan embedding model ID'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=25,
        help='Batch size for embedding generation (default: 25)'
    )
    
    # Other options
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress reporting'
    )
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test connections and exit'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        
        # ChromaDB client
        chromadb_client = ChromaDBClient(
            host=args.chromadb_host,
            port=args.chromadb_port
        )
        
        # Embedding service
        embedding_service = EmbeddingService(
            model_id=args.embedding_model,
            region_name=args.aws_region,
            batch_size=args.batch_size
        )
        
        # Test connections if requested
        if args.test_connection:
            logger.info("Testing connections...")
            
            # Test ChromaDB
            if chromadb_client.test_connection():
                logger.info("✓ ChromaDB connection successful")
            else:
                logger.error("✗ ChromaDB connection failed")
                return 1
            
            # Test Bedrock
            if embedding_service.test_connection():
                logger.info("✓ Bedrock connection successful")
            else:
                logger.error("✗ Bedrock connection failed")
                return 1
            
            logger.info("All connections successful!")
            return 0
        
        # Initialize orchestrator
        orchestrator = DataIngestionOrchestrator(
            chromadb_client=chromadb_client,
            embedding_service=embedding_service
        )
        
        # Perform ingestion based on arguments
        show_progress = not args.no_progress
        
        if args.data_dir:
            logger.info(f"Starting full data directory ingestion: {args.data_dir}")
            stats = orchestrator.ingest_data_directory(args.data_dir, show_progress)
            
        elif args.navlin_file:
            logger.info(f"Starting Navlin News file ingestion: {args.navlin_file}")
            stats = orchestrator.ingest_navlin_news_file(args.navlin_file, show_progress)
            
        elif args.shortage_file:
            logger.info(f"Starting drug shortage file ingestion: {args.shortage_file}")
            stats = orchestrator.ingest_shortage_file(args.shortage_file, show_progress)
        
        # Print final summary
        print("\n" + "=" * 60)
        print("INGESTION SUMMARY")
        print("=" * 60)
        print(f"Duration: {stats.duration:.2f} seconds" if stats.duration else "Duration: unknown")
        print(f"Files processed: {stats.processed_files}/{stats.total_files}")
        print(f"Documents processed: {stats.processed_documents}/{stats.total_documents}")
        print(f"Success rate: {stats.success_rate:.2%}")
        print(f"Duplicates found: {stats.duplicates_found}")
        print(f"Embedding failures: {stats.embedding_failures}")
        print(f"Database failures: {stats.database_failures}")
        
        if stats.failed_documents > 0:
            print(f"⚠️  Failed to process {stats.failed_documents} documents")
            return 1
        else:
            print("✅ All documents processed successfully!")
            return 0
            
    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())