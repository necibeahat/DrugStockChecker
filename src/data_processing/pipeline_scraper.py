"""
AstraZeneca Pipeline Web Scraper.

This module handles scraping pharmaceutical pipeline data from the AstraZeneca
pipeline page, extracting drug names, therapy areas, development phases, 
indications and other relevant pipeline information.
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from html import unescape

import requests
from bs4 import BeautifulSoup

from src.models.documents import PipelineDrugDocument

logger = logging.getLogger(__name__)

# Default URL for AstraZeneca pipeline
DEFAULT_PIPELINE_URL = "https://www.astrazeneca.com/our-therapy-areas/pipeline.html"

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# Common user agent to avoid blocking
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class PipelineScraperError(Exception):
    """Base exception for pipeline scraper errors."""
    pass


class NetworkError(PipelineScraperError):
    """Exception raised for network-related errors."""
    pass


class ParsingError(PipelineScraperError):
    """Exception raised for HTML parsing errors."""
    pass


class AstraZenecaPipelineScraper:
    """
    Scraper for AstraZeneca pharmaceutical pipeline data.
    
    Extracts drug candidate information including names, therapy areas,
    development phases, and indications from the AstraZeneca pipeline page.
    """
    
    def __init__(
        self,
        url: str = DEFAULT_PIPELINE_URL,
        timeout: int = REQUEST_TIMEOUT,
        user_agent: str = DEFAULT_USER_AGENT
    ):
        """
        Initialize the pipeline scraper.
        
        Args:
            url: URL of the AstraZeneca pipeline page
            timeout: Request timeout in seconds
            user_agent: User agent string for HTTP requests
        """
        self.url = url
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.processed_count = 0
        self.error_count = 0
        self.errors = []
    
    def fetch_page(self) -> str:
        """
        Fetch the pipeline page HTML content.
        
        Returns:
            str: Raw HTML content of the page
            
        Raises:
            NetworkError: If the request fails due to network issues
        """
        logger.info(f"Fetching pipeline page from: {self.url}")
        
        try:
            response = self.session.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched page (status: {response.status_code})")
            return response.text
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timed out after {self.timeout} seconds: {e}"
            logger.error(error_msg)
            raise NetworkError(error_msg) from e
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error while fetching pipeline page: {e}"
            logger.error(error_msg)
            raise NetworkError(error_msg) from e
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error {response.status_code}: {e}"
            logger.error(error_msg)
            raise NetworkError(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            logger.error(error_msg)
            raise NetworkError(error_msg) from e
    
    def parse_html(self, html_content: str) -> List[PipelineDrugDocument]:
        """
        Parse the HTML content and extract pipeline drug information.
        
        Args:
            html_content: Raw HTML content of the pipeline page
            
        Returns:
            List[PipelineDrugDocument]: List of parsed pipeline drug documents
            
        Raises:
            ParsingError: If parsing fails due to unexpected page structure
        """
        logger.info("Parsing pipeline HTML content")
        
        if not html_content or not html_content.strip():
            raise ParsingError("Empty HTML content provided")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            error_msg = f"Failed to parse HTML: {e}"
            logger.error(error_msg)
            raise ParsingError(error_msg) from e
        
        documents = []
        self.processed_count = 0
        self.error_count = 0
        self.errors = []
        scraped_at = datetime.utcnow().isoformat()
        
        # Try multiple parsing strategies for robustness
        parsing_methods = [
            self._parse_table_structure,
            self._parse_card_structure,
            self._parse_list_structure,
            self._parse_generic_structure,
        ]
        
        for parse_method in parsing_methods:
            try:
                extracted_data = parse_method(soup)
                if extracted_data:
                    logger.info(f"Successfully extracted {len(extracted_data)} items using {parse_method.__name__}")
                    
                    for item in extracted_data:
                        try:
                            doc = self._create_document(item, scraped_at)
                            if doc:
                                documents.append(doc)
                                self.processed_count += 1
                        except Exception as e:
                            self.error_count += 1
                            error_msg = f"Error creating document for {item.get('drug_name', 'unknown')}: {e}"
                            self.errors.append(error_msg)
                            logger.warning(error_msg)
                    
                    if documents:
                        break
                        
            except Exception as e:
                logger.debug(f"Parsing method {parse_method.__name__} failed: {e}")
                continue
        
        if not documents:
            logger.warning("No pipeline data could be extracted from the page")
        else:
            logger.info(f"Parsed {self.processed_count} documents, {self.error_count} errors")
        
        return documents
    
    def _parse_table_structure(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse pipeline data from table structures.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of dictionaries with extracted drug data
        """
        data = []
        
        # Look for tables that might contain pipeline data
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            headers = []
            
            # Extract headers from the first row or thead
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            elif rows:
                first_row = rows[0]
                if first_row.find_all('th'):
                    headers = [th.get_text(strip=True).lower() for th in first_row.find_all('th')]
                    rows = rows[1:]
            
            # Map common header variations
            header_mapping = self._get_header_mapping(headers)
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue
                
                row_data = {}
                for idx, cell in enumerate(cells):
                    if idx < len(headers):
                        header = headers[idx]
                        value = self._clean_text(cell.get_text())
                        
                        if header in header_mapping:
                            row_data[header_mapping[header]] = value
                
                # Only add if we have at least drug name and some other info
                if row_data.get('drug_name') and (row_data.get('therapy_area') or row_data.get('development_phase')):
                    data.append(row_data)
        
        return data
    
    def _parse_card_structure(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse pipeline data from card/div-based structures.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of dictionaries with extracted drug data
        """
        data = []
        
        # Common CSS class patterns for pipeline cards
        card_patterns = [
            {'class': re.compile(r'pipeline.*card|card.*pipeline', re.I)},
            {'class': re.compile(r'drug.*item|item.*drug', re.I)},
            {'class': re.compile(r'molecule|compound', re.I)},
            {'class': re.compile(r'product.*card', re.I)},
        ]
        
        cards = []
        for pattern in card_patterns:
            cards.extend(soup.find_all('div', pattern))
            cards.extend(soup.find_all('article', pattern))
            cards.extend(soup.find_all('li', pattern))
        
        for card in cards:
            drug_data = self._extract_drug_from_element(card)
            if drug_data and drug_data.get('drug_name'):
                data.append(drug_data)
        
        return data
    
    def _parse_list_structure(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse pipeline data from list structures (ul/ol).
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of dictionaries with extracted drug data
        """
        data = []
        
        # Find lists that might contain pipeline data
        lists = soup.find_all(['ul', 'ol'])
        
        for lst in lists:
            items = lst.find_all('li', recursive=False)
            
            for item in items:
                drug_data = self._extract_drug_from_element(item)
                if drug_data and drug_data.get('drug_name'):
                    data.append(drug_data)
        
        return data
    
    def _parse_generic_structure(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Generic parsing approach for unstructured page layouts.
        
        Searches for content patterns that indicate pipeline drug information.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of dictionaries with extracted drug data
        """
        data = []
        
        # Look for sections that might contain pipeline info
        section_patterns = [
            {'class': re.compile(r'pipeline|therapy|phase', re.I)},
            {'id': re.compile(r'pipeline|therapy|phase', re.I)},
        ]
        
        sections = []
        for pattern in section_patterns:
            sections.extend(soup.find_all(['section', 'div', 'article'], pattern))
        
        # Also look for headings followed by content
        therapy_headings = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=re.compile(
            r'oncology|cardiovascular|respiratory|immunology|rare disease|vaccine|neuroscience',
            re.I
        ))
        
        for heading in therapy_headings:
            therapy_area = self._clean_text(heading.get_text())
            
            # Find sibling or nested content after the heading
            next_siblings = heading.find_next_siblings()
            for sibling in next_siblings[:5]:  # Limit search depth
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                    
                # Look for drug names in the content
                drugs = self._extract_drugs_from_section(sibling, therapy_area)
                data.extend(drugs)
        
        return data
    
    def _extract_drug_from_element(self, element: Any) -> Dict[str, Any]:
        """
        Extract drug information from a single HTML element.
        
        Args:
            element: BeautifulSoup element to extract from
            
        Returns:
            Dictionary with extracted drug data
        """
        drug_data = {}
        
        # Common patterns for drug names
        name_patterns = [
            {'class': re.compile(r'name|title|drug|molecule|compound', re.I)},
            {'data-field': re.compile(r'name|title', re.I)},
        ]
        
        for pattern in name_patterns:
            name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'span', 'div', 'strong'], pattern)
            if name_elem:
                drug_data['drug_name'] = self._clean_text(name_elem.get_text())
                break
        
        # If no specific element found, try first heading or strong element
        if not drug_data.get('drug_name'):
            heading = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong'])
            if heading:
                drug_data['drug_name'] = self._clean_text(heading.get_text())
        
        # Extract therapy area
        therapy_patterns = [
            {'class': re.compile(r'therapy|area|category', re.I)},
            {'data-field': re.compile(r'therapy|area', re.I)},
        ]
        
        for pattern in therapy_patterns:
            therapy_elem = element.find(['span', 'div', 'p'], pattern)
            if therapy_elem:
                drug_data['therapy_area'] = self._clean_text(therapy_elem.get_text())
                break
        
        # Extract phase
        phase_patterns = [
            {'class': re.compile(r'phase|stage|status', re.I)},
            {'data-field': re.compile(r'phase|stage', re.I)},
        ]
        
        for pattern in phase_patterns:
            phase_elem = element.find(['span', 'div', 'p'], pattern)
            if phase_elem:
                drug_data['development_phase'] = self._clean_text(phase_elem.get_text())
                break
        
        # Look for phase in text content
        if not drug_data.get('development_phase'):
            text = element.get_text()
            phase_match = re.search(r'phase\s*([IVi1-4]+|[1-4])', text, re.I)
            if phase_match:
                drug_data['development_phase'] = f"Phase {phase_match.group(1).upper()}"
        
        # Extract indications
        indication_patterns = [
            {'class': re.compile(r'indication|disease|condition', re.I)},
            {'data-field': re.compile(r'indication', re.I)},
        ]
        
        for pattern in indication_patterns:
            indication_elems = element.find_all(['span', 'div', 'p', 'li'], pattern)
            if indication_elems:
                drug_data['indications'] = [
                    self._clean_text(elem.get_text()) for elem in indication_elems
                    if self._clean_text(elem.get_text())
                ]
                break
        
        # Extract mechanism of action
        moa_patterns = [
            {'class': re.compile(r'mechanism|moa|action', re.I)},
            {'data-field': re.compile(r'mechanism', re.I)},
        ]
        
        for pattern in moa_patterns:
            moa_elem = element.find(['span', 'div', 'p'], pattern)
            if moa_elem:
                drug_data['mechanism_of_action'] = self._clean_text(moa_elem.get_text())
                break
        
        # Extract partner information
        partner_patterns = [
            {'class': re.compile(r'partner|collaborat', re.I)},
            {'data-field': re.compile(r'partner', re.I)},
        ]
        
        for pattern in partner_patterns:
            partner_elem = element.find(['span', 'div', 'p'], pattern)
            if partner_elem:
                drug_data['partner'] = self._clean_text(partner_elem.get_text())
                break
        
        return drug_data
    
    def _extract_drugs_from_section(self, section: Any, therapy_area: str) -> List[Dict[str, Any]]:
        """
        Extract multiple drugs from a section element.
        
        Args:
            section: BeautifulSoup section element
            therapy_area: Therapy area for drugs in this section
            
        Returns:
            List of drug data dictionaries
        """
        drugs = []
        
        # Look for individual drug items
        items = section.find_all(['li', 'div', 'p'])
        
        for item in items:
            text = self._clean_text(item.get_text())
            if not text or len(text) < 3:
                continue
            
            # Check if this looks like a drug name (often capitalized or contains numbers)
            if re.match(r'^[A-Z][A-Z0-9-]+', text) or re.match(r'^\w+-\d+', text):
                drug_data = {
                    'drug_name': text.split()[0] if text else '',
                    'therapy_area': therapy_area,
                    'development_phase': '',
                    'indications': [],
                }
                
                # Try to extract phase from the text
                phase_match = re.search(r'phase\s*([IVi1-4]+|[1-4])', text, re.I)
                if phase_match:
                    drug_data['development_phase'] = f"Phase {phase_match.group(1).upper()}"
                
                if drug_data['drug_name']:
                    drugs.append(drug_data)
        
        return drugs
    
    def _get_header_mapping(self, headers: List[str]) -> Dict[str, str]:
        """
        Map table headers to standardized field names.
        
        Args:
            headers: List of header strings
            
        Returns:
            Dictionary mapping original headers to standardized names
        """
        mapping = {}
        
        header_variants = {
            'drug_name': ['drug', 'name', 'compound', 'molecule', 'product', 'drug name', 'candidate'],
            'therapy_area': ['therapy', 'area', 'therapeutic area', 'therapy area', 'category'],
            'development_phase': ['phase', 'stage', 'status', 'development stage', 'clinical phase'],
            'indications': ['indication', 'indications', 'disease', 'condition', 'target indication'],
            'mechanism_of_action': ['mechanism', 'moa', 'mechanism of action', 'mode of action'],
            'molecule_type': ['type', 'molecule type', 'modality', 'drug type'],
            'partner': ['partner', 'collaboration', 'partners', 'collaborator'],
        }
        
        for header in headers:
            header_lower = header.lower().strip()
            for field, variants in header_variants.items():
                if header_lower in variants or any(v in header_lower for v in variants):
                    mapping[header_lower] = field
                    break
        
        return mapping
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _create_document(
        self,
        data: Dict[str, Any],
        scraped_at: str
    ) -> Optional[PipelineDrugDocument]:
        """
        Create a PipelineDrugDocument from extracted data.
        
        Args:
            data: Dictionary of extracted drug data
            scraped_at: Timestamp when the data was scraped
            
        Returns:
            PipelineDrugDocument or None if creation fails
        """
        try:
            doc = PipelineDrugDocument(
                drug_name=data.get('drug_name', ''),
                therapy_area=data.get('therapy_area', 'Unknown'),
                development_phase=data.get('development_phase', 'Unknown'),
                indications=data.get('indications', []),
                molecule_type=data.get('molecule_type', ''),
                mechanism_of_action=data.get('mechanism_of_action', ''),
                partner=data.get('partner', ''),
                additional_info={k: v for k, v in data.items() 
                               if k not in ['drug_name', 'therapy_area', 'development_phase', 
                                          'indications', 'molecule_type', 'mechanism_of_action', 
                                          'partner']},
                source_url=self.url,
                source="AstraZeneca Pipeline",
                scraped_at=scraped_at
            )
            
            doc.validate_data_integrity()
            return doc
            
        except ValueError as e:
            logger.warning(f"Validation failed for drug {data.get('drug_name')}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    def scrape(self) -> List[PipelineDrugDocument]:
        """
        Scrape the AstraZeneca pipeline page and extract drug information.
        
        This is the main entry point for scraping. It fetches the page,
        parses the HTML, and returns structured drug documents.
        
        Returns:
            List[PipelineDrugDocument]: List of extracted pipeline drug documents
            
        Raises:
            NetworkError: If page fetching fails
            ParsingError: If HTML parsing fails completely
        """
        logger.info("Starting AstraZeneca pipeline scrape")
        
        html_content = self.fetch_page()
        documents = self.parse_html(html_content)
        
        logger.info(f"Scrape complete. Extracted {len(documents)} drug documents")
        return documents
    
    def scrape_to_json(self, output_path: Optional[str] = None) -> str:
        """
        Scrape pipeline data and return/save as JSON.
        
        Args:
            output_path: Optional path to save the JSON file
            
        Returns:
            str: JSON string of the extracted data
        """
        documents = self.scrape()
        
        data = {
            'source': 'AstraZeneca Pipeline',
            'source_url': self.url,
            'scraped_at': datetime.utcnow().isoformat(),
            'total_count': len(documents),
            'pipeline_drugs': [doc.to_dict() for doc in documents]
        }
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"Saved pipeline data to: {output_path}")
        
        return json_str
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the last scraping operation.
        
        Returns:
            Dict containing scraping statistics
        """
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'errors': self.errors.copy(),
            'success_rate': (self.processed_count / (self.processed_count + self.error_count) 
                           if (self.processed_count + self.error_count) > 0 else 0),
            'source_url': self.url
        }


def scrape_astrazeneca_pipeline(
    url: str = DEFAULT_PIPELINE_URL,
    output_path: Optional[str] = None,
    timeout: int = REQUEST_TIMEOUT
) -> List[PipelineDrugDocument]:
    """
    Convenience function to scrape AstraZeneca pipeline data.
    
    Args:
        url: URL of the pipeline page
        output_path: Optional path to save results as JSON
        timeout: Request timeout in seconds
        
    Returns:
        List[PipelineDrugDocument]: List of extracted pipeline drugs
        
    Example:
        >>> drugs = scrape_astrazeneca_pipeline()
        >>> for drug in drugs:
        ...     print(f"{drug.drug_name}: {drug.development_phase}")
    """
    scraper = AstraZenecaPipelineScraper(url=url, timeout=timeout)
    
    if output_path:
        scraper.scrape_to_json(output_path)
    
    return scraper.scrape()
