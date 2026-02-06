"""
Data models for pharmaceutical documents.

This module defines the core data structures for pharmaceutical news and drug shortage
information, with proper validation and type hints.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
import json
from pydantic import BaseModel, validator, Field


@dataclass
class NewsDocument:
    """
    Data model for pharmaceutical news documents from Navlin News.
    
    Represents structured news data containing regulatory decisions, pricing information,
    and industry updates with geographic and therapeutic area classification.
    """
    id: int
    title: str
    date: str
    countries: List[str]
    country_codes: List[Dict[str, str]] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    product_groups: List[str] = field(default_factory=list)
    therapeutic_areas: List[str] = field(default_factory=list)
    indications: List[str] = field(default_factory=list)
    content_html: str = ""
    types: List[Dict[str, Any]] = field(default_factory=list)
    topic: str = ""
    source: str = "Navlin News"
    
    # Additional fields from the JSON structure
    daily_id: Optional[int] = None
    daily_brief: Optional[str] = None
    daily_content: Optional[str] = None
    companies: Optional[List[str]] = None
    generic_names: Optional[List[str]] = None
    notes: Optional[str] = None
    active: bool = True
    publish_date: Optional[int] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    author: Optional[str] = None
    publish_date_str: Optional[str] = None
    certain_order: Optional[int] = None
    janssen_order: Optional[int] = None
    priority: Optional[str] = None
    send_time: Optional[str] = None
    verification: bool = False
    image: Optional[str] = None
    seconds: Optional[int] = None

    def validate_data_integrity(self) -> bool:
        """
        Validate the integrity of the news document data.
        
        Returns:
            bool: True if data passes validation checks
            
        Raises:
            ValueError: If critical validation fails
        """
        # Check required fields
        if not self.id or self.id <= 0:
            raise ValueError("News document must have a valid positive ID")
            
        if not self.title or not self.title.strip():
            raise ValueError("News document must have a non-empty title")
            
        if not self.date:
            raise ValueError("News document must have a date")
            
        if not self.countries:
            raise ValueError("News document must specify at least one country")
            
        # Validate country format
        for country in self.countries:
            if not isinstance(country, str) or not country.strip():
                raise ValueError(f"Invalid country format: {country}")
                
        # Validate regions if present
        for region in self.regions:
            if not isinstance(region, str) or not region.strip():
                raise ValueError(f"Invalid region format: {region}")
                
        # Validate therapeutic areas if present
        for area in self.therapeutic_areas:
            if not isinstance(area, str) or not area.strip():
                raise ValueError(f"Invalid therapeutic area format: {area}")
                
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date,
            'countries': self.countries,
            'country_codes': self.country_codes,
            'regions': self.regions,
            'keywords': self.keywords,
            'product_groups': self.product_groups,
            'therapeutic_areas': self.therapeutic_areas,
            'indications': self.indications,
            'content_html': self.content_html,
            'types': self.types,
            'topic': self.topic,
            'source': self.source,
            'daily_id': self.daily_id,
            'daily_brief': self.daily_brief,
            'daily_content': self.daily_content,
            'companies': self.companies,
            'generic_names': self.generic_names,
            'notes': self.notes,
            'active': self.active,
            'publish_date': self.publish_date,
            'create_time': self.create_time,
            'update_time': self.update_time,
            'create_by': self.create_by,
            'update_by': self.update_by,
            'author': self.author,
            'publish_date_str': self.publish_date_str,
            'certain_order': self.certain_order,
            'janssen_order': self.janssen_order,
            'priority': self.priority,
            'send_time': self.send_time,
            'verification': self.verification,
            'image': self.image,
            'seconds': self.seconds
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewsDocument':
        """
        Create a NewsDocument from a dictionary.
        
        Args:
            data: Dictionary containing news document data
            
        Returns:
            NewsDocument: Validated news document instance
        """
        # Map JSON field names to our field names
        mapped_data = {
            'id': data.get('id'),
            'title': data.get('title', ''),
            'date': data.get('createTime', data.get('publishDateStr', '')),
            'countries': data.get('countries', []),
            'country_codes': data.get('countryCodes', []),
            'regions': data.get('regions', []),
            'keywords': data.get('keywords', []),
            'product_groups': data.get('product_groups', []),
            'therapeutic_areas': data.get('therapeutic_areas', []),
            'indications': data.get('indications', []),
            'content_html': data.get('content', ''),
            'types': data.get('types', []),
            'topic': data.get('topic', ''),
            'daily_id': data.get('dailyId'),
            'daily_brief': data.get('dailyBrief'),
            'daily_content': data.get('dailyContent'),
            'companies': data.get('companies'),
            'generic_names': data.get('genericNames'),
            'notes': data.get('notes'),
            'active': data.get('active', True),
            'publish_date': data.get('publishDate'),
            'create_time': data.get('createTime'),
            'update_time': data.get('updateTime'),
            'create_by': data.get('createBy'),
            'update_by': data.get('updateBy'),
            'author': data.get('author'),
            'publish_date_str': data.get('publishDateStr'),
            'certain_order': data.get('certainOrder'),
            'janssen_order': data.get('janssenOrder'),
            'priority': data.get('priority'),
            'send_time': data.get('sendTime'),
            'verification': data.get('verification', False),
            'image': data.get('image'),
            'seconds': data.get('seconds')
        }
        
        doc = cls(**mapped_data)
        doc.validate_data_integrity()
        return doc


@dataclass
class DrugShortageDocument:
    """
    Data model for drug shortage information from multiple sources.
    
    Represents pharmaceutical product shortages with manufacturer information,
    status tracking, and geographic context.
    """
    product_name: str
    ingredient: str
    matched_ingredient: str
    status: str
    date_reported: str
    reason: str
    source_url: str
    manufacturer: str
    expected_resolution: str
    source: str
    source_country: str
    scraped_at: str

    def validate_data_integrity(self) -> bool:
        """
        Validate the integrity of the drug shortage document data.
        
        Returns:
            bool: True if data passes validation checks
            
        Raises:
            ValueError: If critical validation fails
        """
        # Check required fields
        if not self.product_name or not self.product_name.strip():
            raise ValueError("Drug shortage document must have a non-empty product name")
            
        if not self.ingredient or not self.ingredient.strip():
            raise ValueError("Drug shortage document must have a non-empty ingredient")
            
        if not self.status or not self.status.strip():
            raise ValueError("Drug shortage document must have a status")
            
        if not self.date_reported:
            raise ValueError("Drug shortage document must have a reported date")
            
        if not self.source or not self.source.strip():
            raise ValueError("Drug shortage document must specify a source")
            
        if not self.source_country or not self.source_country.strip():
            raise ValueError("Drug shortage document must specify a source country")
            
        # Validate URL format if present
        if self.source_url and not (self.source_url.startswith('http://') or 
                                   self.source_url.startswith('https://')):
            raise ValueError(f"Invalid source URL format: {self.source_url}")
            
        # Validate date format (basic check)
        if self.date_reported:
            try:
                # Try to parse common date formats
                from datetime import datetime
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                    try:
                        datetime.strptime(self.date_reported, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format worked, it might still be valid but in a different format
                    pass
            except Exception:
                raise ValueError(f"Invalid date format: {self.date_reported}")
                
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary for serialization."""
        return {
            'product_name': self.product_name,
            'ingredient': self.ingredient,
            'matched_ingredient': self.matched_ingredient,
            'status': self.status,
            'date_reported': self.date_reported,
            'reason': self.reason,
            'source_url': self.source_url,
            'manufacturer': self.manufacturer,
            'expected_resolution': self.expected_resolution,
            'source': self.source,
            'source_country': self.source_country,
            'scraped_at': self.scraped_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DrugShortageDocument':
        """
        Create a DrugShortageDocument from a dictionary.
        
        Args:
            data: Dictionary containing drug shortage data
            
        Returns:
            DrugShortageDocument: Validated drug shortage document instance
        """
        doc = cls(
            product_name=data.get('product_name', ''),
            ingredient=data.get('ingredient', ''),
            matched_ingredient=data.get('matched_ingredient', ''),
            status=data.get('status', ''),
            date_reported=data.get('date_reported', ''),
            reason=data.get('reason', ''),
            source_url=data.get('source_url', ''),
            manufacturer=data.get('manufacturer', ''),
            expected_resolution=data.get('expected_resolution', ''),
            source=data.get('source', ''),
            source_country=data.get('source_country', ''),
            scraped_at=data.get('scraped_at', '')
        )
        
        doc.validate_data_integrity()
        return doc


@dataclass
class PipelineDrugDocument:
    """
    Data model for pharmaceutical pipeline drug information.
    
    Represents drug candidates in various stages of development with
    therapy area classification and indication details.
    """
    drug_name: str
    therapy_area: str
    development_phase: str
    indications: List[str] = field(default_factory=list)
    molecule_type: str = ""
    mechanism_of_action: str = ""
    partner: str = ""
    additional_info: Dict[str, Any] = field(default_factory=dict)
    source_url: str = ""
    source: str = "AstraZeneca Pipeline"
    scraped_at: str = ""

    def validate_data_integrity(self) -> bool:
        """
        Validate the integrity of the pipeline drug document data.
        
        Returns:
            bool: True if data passes validation checks
            
        Raises:
            ValueError: If critical validation fails
        """
        if not self.drug_name or not self.drug_name.strip():
            raise ValueError("Pipeline drug document must have a non-empty drug name")
            
        if not self.therapy_area or not self.therapy_area.strip():
            raise ValueError("Pipeline drug document must have a therapy area")
            
        if not self.development_phase or not self.development_phase.strip():
            raise ValueError("Pipeline drug document must have a development phase")
            
        if self.source_url and not (self.source_url.startswith('http://') or 
                                    self.source_url.startswith('https://')):
            raise ValueError(f"Invalid source URL format: {self.source_url}")
            
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary for serialization."""
        return {
            'drug_name': self.drug_name,
            'therapy_area': self.therapy_area,
            'development_phase': self.development_phase,
            'indications': self.indications,
            'molecule_type': self.molecule_type,
            'mechanism_of_action': self.mechanism_of_action,
            'partner': self.partner,
            'additional_info': self.additional_info,
            'source_url': self.source_url,
            'source': self.source,
            'scraped_at': self.scraped_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineDrugDocument':
        """
        Create a PipelineDrugDocument from a dictionary.
        
        Args:
            data: Dictionary containing pipeline drug data
            
        Returns:
            PipelineDrugDocument: Validated pipeline drug document instance
        """
        doc = cls(
            drug_name=data.get('drug_name', ''),
            therapy_area=data.get('therapy_area', ''),
            development_phase=data.get('development_phase', ''),
            indications=data.get('indications', []),
            molecule_type=data.get('molecule_type', ''),
            mechanism_of_action=data.get('mechanism_of_action', ''),
            partner=data.get('partner', ''),
            additional_info=data.get('additional_info', {}),
            source_url=data.get('source_url', ''),
            source=data.get('source', 'AstraZeneca Pipeline'),
            scraped_at=data.get('scraped_at', '')
        )
        
        doc.validate_data_integrity()
        return doc


# Type aliases for convenience
DocumentType = Union[NewsDocument, DrugShortageDocument, PipelineDrugDocument]