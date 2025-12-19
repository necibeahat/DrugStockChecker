"""
Drug shortage JSON data parser.

This module handles parsing of drug shortage JSON files from multiple sources,
extracting all required fields, normalizing ingredient names and manufacturer information,
and handling different source formats (Canada, Australia, etc.).
"""

import json
import re
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging
from datetime import datetime

from src.models.documents import DrugShortageDocument

logger = logging.getLogger(__name__)


class DrugShortageParser:
    """
    Parser for drug shortage JSON data files from multiple sources.
    
    Handles extraction of pharmaceutical shortage data with normalization
    of ingredient names and manufacturer information across different formats.
    """
    
    def __init__(self):
        """Initialize the parser with normalization mappings."""
        self.processed_count = 0
        self.error_count = 0
        self.errors = []
        
        # Ingredient name normalization mappings
        self.ingredient_normalizations = {
            # Common variations and synonyms
            'acetaminophen': 'paracetamol',
            'ibuprofen': 'ibuprofen',
            'aspirin': 'acetylsalicylic acid',
            # Add more as needed based on data analysis
        }
        
        # Manufacturer name normalizations
        self.manufacturer_normalizations = {
            # Common variations in manufacturer names
            'pfizer inc': 'pfizer',
            'pfizer canada inc': 'pfizer',
            'johnson & johnson': 'j&j',
            'janssen pharmaceuticals': 'janssen',
            # Add more as needed
        }
    
    def parse_file(self, file_path: str) -> List[DrugShortageDocument]:
        """
        Parse a single drug shortage JSON file.
        
        Args:
            file_path: Path to the JSON file to parse
            
        Returns:
            List[DrugShortageDocument]: List of parsed and validated shortage documents
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Parsing drug shortage file: {file_path}")
        
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
                doc = self._parse_shortage_item(item)
                if doc:
                    documents.append(doc)
                    self.processed_count += 1
            except Exception as e:
                self.error_count += 1
                error_msg = f"Error parsing shortage item: {str(e)}"
                self.errors.append(error_msg)
                logger.warning(error_msg)
                continue
        
        logger.info(f"Parsed {self.processed_count} shortage documents, {self.error_count} errors")
        return documents
    
    def parse_directory(self, directory_path: str) -> List[DrugShortageDocument]:
        """
        Parse all drug shortage JSON files in a directory.
        
        Args:
            directory_path: Path to directory containing JSON files
            
        Returns:
            List[DrugShortageDocument]: Combined list of all parsed documents
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_documents = []
        json_files = list(directory.glob("*shortage*.json"))
        
        if not json_files:
            logger.warning(f"No shortage JSON files found in {directory}")
            return all_documents
        
        logger.info(f"Found {len(json_files)} shortage JSON files to parse")
        
        for json_file in json_files:
            try:
                documents = self.parse_file(str(json_file))
                all_documents.extend(documents)
                logger.info(f"Parsed {len(documents)} shortage documents from {json_file.name}")
            except Exception as e:
                logger.error(f"Failed to parse file {json_file}: {e}")
                continue
        
        logger.info(f"Total shortage documents parsed: {len(all_documents)}")
        return all_documents
    
    def _parse_shortage_item(self, item: Dict[str, Any]) -> Optional[DrugShortageDocument]:
        """
        Parse a single shortage item from JSON data.
        
        Args:
            item: Dictionary containing shortage item data
            
        Returns:
            DrugShortageDocument: Parsed and validated shortage document, or None if parsing fails
        """
        try:
            # Extract and validate required fields
            product_name = item.get('product_name') or ''
            if isinstance(product_name, str):
                product_name = product_name.strip()
            else:
                product_name = str(product_name) if product_name is not None else ''
            
            if not product_name:
                logger.warning("Skipping shortage item without product name")
                return None
            
            ingredient = item.get('ingredient') or ''
            if isinstance(ingredient, str):
                ingredient = ingredient.strip()
            else:
                ingredient = str(ingredient) if ingredient is not None else ''
            
            if not ingredient:
                logger.warning(f"Product {product_name} has no ingredient information")
                ingredient = "Unknown"
            
            # Normalize ingredient name
            normalized_ingredient = self._normalize_ingredient(ingredient)
            
            status = item.get('status') or ''
            if isinstance(status, str):
                status = status.strip()
            else:
                status = str(status) if status is not None else ''
            
            if not status:
                logger.warning(f"Product {product_name} has no status information")
                status = "Unknown"
            
            # Handle date fields
            date_reported = item.get('date_reported', '')
            if not date_reported:
                logger.warning(f"Product {product_name} has no reported date")
                date_reported = "Unknown"
            else:
                # Normalize date format
                date_reported = self._normalize_date(date_reported)
            
            # Extract other fields with defaults
            reason = item.get('reason') or ''
            if isinstance(reason, str):
                reason = reason.strip()
            else:
                reason = str(reason) if reason is not None else ''
            
            source_url = item.get('source_url') or ''
            if isinstance(source_url, str):
                source_url = source_url.strip()
            else:
                source_url = str(source_url) if source_url is not None else ''
            
            # Normalize manufacturer name
            manufacturer = item.get('manufacturer') or ''
            if isinstance(manufacturer, str):
                manufacturer = manufacturer.strip()
            else:
                manufacturer = str(manufacturer) if manufacturer is not None else ''
            normalized_manufacturer = self._normalize_manufacturer(manufacturer)
            
            expected_resolution = item.get('expected_resolution') or ''
            if isinstance(expected_resolution, str):
                expected_resolution = expected_resolution.strip()
            else:
                expected_resolution = str(expected_resolution) if expected_resolution is not None else ''
            
            source = item.get('source') or 'Unknown'
            if isinstance(source, str):
                source = source.strip()
            else:
                source = str(source) if source is not None else 'Unknown'
            
            source_country = item.get('source_country') or 'Unknown'
            if isinstance(source_country, str):
                source_country = source_country.strip()
            else:
                source_country = str(source_country) if source_country is not None else 'Unknown'
            
            # Handle scraped_at timestamp
            scraped_at = item.get('scraped_at', '')
            if scraped_at:
                scraped_at = self._normalize_timestamp(scraped_at)
            
            # Create the document
            doc = DrugShortageDocument(
                product_name=product_name,
                ingredient=ingredient,
                matched_ingredient=normalized_ingredient,
                status=status,
                date_reported=date_reported,
                reason=reason,
                source_url=source_url,
                manufacturer=normalized_manufacturer,
                expected_resolution=expected_resolution,
                source=source,
                source_country=source_country.upper(),  # Standardize country codes
                scraped_at=scraped_at
            )
            
            # Validate the document
            doc.validate_data_integrity()
            return doc
            
        except Exception as e:
            logger.error(f"Error parsing shortage item: {e}")
            raise
    
    def _normalize_ingredient(self, ingredient: str) -> str:
        """
        Normalize ingredient names for consistency.
        
        Args:
            ingredient: Raw ingredient name
            
        Returns:
            str: Normalized ingredient name
        """
        if not ingredient:
            return ingredient
        
        # Convert to lowercase for comparison
        ingredient_lower = ingredient.lower().strip()
        
        # Check for known normalizations
        normalized = self.ingredient_normalizations.get(ingredient_lower)
        if normalized:
            return normalized
        
        # Clean up common formatting issues
        # Remove extra whitespace
        ingredient = re.sub(r'\s+', ' ', ingredient).strip()
        
        # Remove common suffixes that don't affect the active ingredient
        suffixes_to_remove = [
            r'\s+hydrochloride$',
            r'\s+hcl$',
            r'\s+sodium$',
            r'\s+sulfate$',
            r'\s+sulphate$',
            r'\s+phosphate$',
            r'\s+citrate$',
            r'\s+tartrate$',
            r'\s+maleate$',
            r'\s+fumarate$',
            r'\s+succinate$'
        ]
        
        for suffix in suffixes_to_remove:
            ingredient = re.sub(suffix, '', ingredient, flags=re.IGNORECASE)
        
        return ingredient.strip()
    
    def _normalize_manufacturer(self, manufacturer: str) -> str:
        """
        Normalize manufacturer names for consistency.
        
        Args:
            manufacturer: Raw manufacturer name
            
        Returns:
            str: Normalized manufacturer name
        """
        if not manufacturer:
            return manufacturer
        
        # Convert to lowercase for comparison
        manufacturer_lower = manufacturer.lower().strip()
        
        # Check for known normalizations
        normalized = self.manufacturer_normalizations.get(manufacturer_lower)
        if normalized:
            return normalized
        
        # Clean up common formatting issues
        manufacturer = re.sub(r'\s+', ' ', manufacturer).strip()
        
        # Remove common corporate suffixes for normalization
        suffixes_to_clean = [
            r'\s+inc\.?$',
            r'\s+incorporated$',
            r'\s+corp\.?$',
            r'\s+corporation$',
            r'\s+ltd\.?$',
            r'\s+limited$',
            r'\s+llc$',
            r'\s+co\.?$',
            r'\s+company$'
        ]
        
        cleaned = manufacturer
        for suffix in suffixes_to_clean:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip() or manufacturer  # Return original if cleaning resulted in empty string
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize date strings to a consistent format.
        
        Args:
            date_str: Raw date string
            
        Returns:
            str: Normalized date string in YYYY-MM-DD format
        """
        if not date_str:
            return date_str
        
        # Try to parse common date formats
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%d-%m-%Y',
            '%m-%d-%Y',
            '%d %b %Y',  # 30 Dec 2024
            '%d.%m.%Y',  # 12.11.2025
            '%d %B %Y',  # 30 December 2024
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format worked, return original
        logger.warning(f"Could not normalize date format: {date_str}")
        return date_str
    
    def _normalize_timestamp(self, timestamp_str: str) -> str:
        """
        Normalize timestamp strings to ISO format.
        
        Args:
            timestamp_str: Raw timestamp string
            
        Returns:
            str: Normalized timestamp in ISO format
        """
        if not timestamp_str:
            return timestamp_str
        
        # Try to parse and normalize to ISO format
        timestamp_formats = [
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S'
        ]
        
        for fmt in timestamp_formats:
            try:
                parsed_ts = datetime.strptime(timestamp_str, fmt)
                return parsed_ts.isoformat()
            except ValueError:
                continue
        
        # If no format worked, return original
        return timestamp_str
    
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
    
    def get_ingredient_stats(self, documents: List[DrugShortageDocument]) -> Dict[str, Any]:
        """
        Get statistics about ingredients in the parsed documents.
        
        Args:
            documents: List of parsed shortage documents
            
        Returns:
            Dict containing ingredient statistics
        """
        if not documents:
            return {'total_ingredients': 0, 'unique_ingredients': 0, 'top_ingredients': []}
        
        ingredient_counts = {}
        for doc in documents:
            ingredient = doc.matched_ingredient.lower()
            ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1
        
        sorted_ingredients = sorted(ingredient_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_ingredients': len(documents),
            'unique_ingredients': len(ingredient_counts),
            'top_ingredients': sorted_ingredients[:10],
            'ingredient_distribution': ingredient_counts
        }
    
    def get_manufacturer_stats(self, documents: List[DrugShortageDocument]) -> Dict[str, Any]:
        """
        Get statistics about manufacturers in the parsed documents.
        
        Args:
            documents: List of parsed shortage documents
            
        Returns:
            Dict containing manufacturer statistics
        """
        if not documents:
            return {'total_products': 0, 'unique_manufacturers': 0, 'top_manufacturers': []}
        
        manufacturer_counts = {}
        for doc in documents:
            manufacturer = doc.manufacturer.lower()
            if manufacturer:  # Skip empty manufacturers
                manufacturer_counts[manufacturer] = manufacturer_counts.get(manufacturer, 0) + 1
        
        sorted_manufacturers = sorted(manufacturer_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_products': len(documents),
            'unique_manufacturers': len(manufacturer_counts),
            'top_manufacturers': sorted_manufacturers[:10],
            'manufacturer_distribution': manufacturer_counts
        }