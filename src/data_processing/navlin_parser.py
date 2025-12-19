"""
Navlin News JSON data parser.

This module handles parsing of Navlin News JSON files, extracting all required fields,
handling missing or malformed data gracefully, and converting HTML content to searchable text.
"""

import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from html import unescape
from bs4 import BeautifulSoup

from src.models.documents import NewsDocument

logger = logging.getLogger(__name__)


class NavlinNewsParser:
    """
    Parser for Navlin News JSON data files.
    
    Handles extraction of pharmaceutical news data with robust error handling
    and HTML content conversion to searchable text.
    """
    
    def __init__(self):
        """Initialize the parser with default configuration."""
        self.processed_count = 0
        self.error_count = 0
        self.errors = []
    
    def parse_file(self, file_path: str) -> List[NewsDocument]:
        """
        Parse a single Navlin News JSON file.
        
        Args:
            file_path: Path to the JSON file to parse
            
        Returns:
            List[NewsDocument]: List of parsed and validated news documents
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Parsing Navlin News file: {file_path}")
        
        try:
            # Try utf-8-sig first to handle BOM
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            raise
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error in file {file_path}: {e}")
            # Try with different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        data = json.load(f)
                    break
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            else:
                raise
        
        # Handle both single objects and arrays
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError(f"Expected JSON array or object, got {type(data)}")
        
        documents = []
        self.processed_count = 0
        self.error_count = 0
        self.errors = []
        
        for item in data:
            try:
                doc = self._parse_news_item(item)
                if doc:
                    documents.append(doc)
                    self.processed_count += 1
            except Exception as e:
                self.error_count += 1
                error_msg = f"Error parsing item {item.get('id', 'unknown')}: {str(e)}"
                self.errors.append(error_msg)
                logger.warning(error_msg)
                continue
        
        logger.info(f"Parsed {self.processed_count} documents, {self.error_count} errors")
        return documents
    
    def parse_directory(self, directory_path: str) -> List[NewsDocument]:
        """
        Parse all Navlin News JSON files in a directory.
        
        Args:
            directory_path: Path to directory containing JSON files
            
        Returns:
            List[NewsDocument]: Combined list of all parsed documents
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_documents = []
        json_files = list(directory.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return all_documents
        
        logger.info(f"Found {len(json_files)} JSON files to parse")
        
        for json_file in json_files:
            try:
                documents = self.parse_file(str(json_file))
                all_documents.extend(documents)
                logger.info(f"Parsed {len(documents)} documents from {json_file.name}")
            except Exception as e:
                logger.error(f"Failed to parse file {json_file}: {e}")
                continue
        
        logger.info(f"Total documents parsed: {len(all_documents)}")
        return all_documents
    
    def _parse_news_item(self, item: Dict[str, Any]) -> Optional[NewsDocument]:
        """
        Parse a single news item from JSON data.
        
        Args:
            item: Dictionary containing news item data
            
        Returns:
            NewsDocument: Parsed and validated news document, or None if parsing fails
        """
        try:
            # Extract and validate required fields
            doc_id = item.get('id')
            if not doc_id:
                logger.warning("Skipping item without ID")
                return None
            
            title = item.get('title', '').strip()
            if not title:
                logger.warning(f"Item {doc_id} has empty title")
                title = f"Untitled News Item {doc_id}"
            
            # Handle date fields - try multiple possible field names
            date = (item.get('date') or 
                   item.get('publishDateStr') or 
                   item.get('createTime') or 
                   item.get('publishDate'))
            
            if not date:
                logger.warning(f"Item {doc_id} has no date information")
                date = "Unknown"
            
            # Convert publishDate timestamp to string if needed
            if isinstance(date, int):
                from datetime import datetime
                try:
                    date = datetime.fromtimestamp(date / 1000).strftime('%Y-%m-%d')
                except (ValueError, OSError):
                    date = "Unknown"
            
            # Extract countries with fallback
            countries = item.get('countries', [])
            if not countries:
                logger.warning(f"Item {doc_id} has no country information")
                countries = ["Unknown"]
            
            # Extract and clean HTML content
            content_html = item.get('content_html', item.get('content', ''))
            
            # Convert HTML to searchable text
            searchable_content = self._html_to_text(content_html)
            
            # Create the document with all available fields
            doc = NewsDocument(
                id=doc_id,
                title=title,
                date=str(date),
                countries=countries,
                country_codes=item.get('country_codes', item.get('countryCodes', [])),
                regions=item.get('regions', []),
                keywords=item.get('keywords', []),
                product_groups=item.get('product_groups', item.get('productGroups', [])),
                therapeutic_areas=item.get('therapeutic_areas', item.get('therapeuticAreas', [])),
                indications=item.get('indications', []),
                content_html=searchable_content,  # Store cleaned text instead of HTML
                types=item.get('types', []),
                topic=item.get('topic', ''),
                source="Navlin News",
                # Additional fields
                daily_id=item.get('dailyId'),
                daily_brief=item.get('dailyBrief'),
                daily_content=item.get('dailyContent'),
                companies=item.get('companies'),
                generic_names=item.get('genericNames'),
                notes=item.get('notes'),
                active=item.get('active', True),
                publish_date=item.get('publishDate'),
                create_time=item.get('createTime'),
                update_time=item.get('updateTime'),
                create_by=item.get('createBy'),
                update_by=item.get('updateBy'),
                author=item.get('author'),
                publish_date_str=item.get('publishDateStr'),
                certain_order=item.get('certainOrder'),
                janssen_order=item.get('janssenOrder'),
                priority=item.get('priority'),
                send_time=item.get('sendTime'),
                verification=item.get('verification', False),
                image=item.get('image'),
                seconds=item.get('seconds')
            )
            
            # Validate the document
            doc.validate_data_integrity()
            return doc
            
        except Exception as e:
            logger.error(f"Error parsing news item {item.get('id', 'unknown')}: {e}")
            raise
    
    def _html_to_text(self, html_content: str) -> str:
        """
        Convert HTML content to clean, searchable text.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            str: Clean text suitable for search and embedding
        """
        if not html_content:
            return ""
        
        try:
            # First, unescape HTML entities
            text = unescape(html_content)
            
            # Use BeautifulSoup to parse and extract text
            soup = BeautifulSoup(text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            logger.warning(f"Error converting HTML to text: {e}")
            # Fallback: simple regex-based HTML tag removal
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = unescape(text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the last parsing operation.
        
        Returns:
            Dict containing processing statistics
        """
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'errors': self.errors.copy(),
            'success_rate': (self.processed_count / (self.processed_count + self.error_count) 
                           if (self.processed_count + self.error_count) > 0 else 0)
        }