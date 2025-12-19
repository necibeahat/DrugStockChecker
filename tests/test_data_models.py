"""
Tests for pharmaceutical data models.
"""

import pytest
from src.models.documents import NewsDocument, DrugShortageDocument


class TestNewsDocument:
    """Test cases for NewsDocument data model."""
    
    def test_create_valid_news_document(self):
        """Test creating a valid news document."""
        doc = NewsDocument(
            id=12345,
            title="Test News Article",
            date="2025-12-19",
            countries=["DENMARK"],
            regions=["EUROPE"],
            therapeutic_areas=["NEUROLOGY"]
        )
        
        assert doc.id == 12345
        assert doc.title == "Test News Article"
        assert doc.countries == ["DENMARK"]
        assert doc.source == "Navlin News"
        
    def test_news_document_validation_success(self):
        """Test successful validation of news document."""
        doc = NewsDocument(
            id=12345,
            title="Test News Article",
            date="2025-12-19",
            countries=["DENMARK"]
        )
        
        assert doc.validate_data_integrity() is True
        
    def test_news_document_validation_missing_id(self):
        """Test validation failure for missing ID."""
        doc = NewsDocument(
            id=0,  # Invalid ID
            title="Test News Article",
            date="2025-12-19",
            countries=["DENMARK"]
        )
        
        with pytest.raises(ValueError, match="must have a valid positive ID"):
            doc.validate_data_integrity()
            
    def test_news_document_validation_empty_title(self):
        """Test validation failure for empty title."""
        doc = NewsDocument(
            id=12345,
            title="",  # Empty title
            date="2025-12-19",
            countries=["DENMARK"]
        )
        
        with pytest.raises(ValueError, match="must have a non-empty title"):
            doc.validate_data_integrity()
            
    def test_news_document_validation_no_countries(self):
        """Test validation failure for missing countries."""
        doc = NewsDocument(
            id=12345,
            title="Test News Article",
            date="2025-12-19",
            countries=[]  # No countries
        )
        
        with pytest.raises(ValueError, match="must specify at least one country"):
            doc.validate_data_integrity()
            
    def test_news_document_from_dict(self):
        """Test creating NewsDocument from dictionary."""
        data = {
            'id': 29036,
            'title': "Danish Medicines Council Rejects Leqembi",
            'createTime': "2025-12-18",
            'countries': ["DENMARK"],
            'regions': ["EUROPE"],
            'keywords': ["lecanemab"],
            'product_groups': ["LEQEMBI"],
            'therapeutic_areas': ["NEUROLOGY"],
            'indications': ["ALZHEIMER'S DISEASE"],
            'content': "<p>Test content</p>",
            'topic': "Pricing & Reimbursement"
        }
        
        doc = NewsDocument.from_dict(data)
        
        assert doc.id == 29036
        assert doc.title == "Danish Medicines Council Rejects Leqembi"
        assert doc.countries == ["DENMARK"]
        assert doc.regions == ["EUROPE"]
        assert doc.therapeutic_areas == ["NEUROLOGY"]
        
    def test_news_document_to_dict(self):
        """Test converting NewsDocument to dictionary."""
        doc = NewsDocument(
            id=12345,
            title="Test News Article",
            date="2025-12-19",
            countries=["DENMARK"],
            regions=["EUROPE"]
        )
        
        result = doc.to_dict()
        
        assert result['id'] == 12345
        assert result['title'] == "Test News Article"
        assert result['countries'] == ["DENMARK"]
        assert result['source'] == "Navlin News"


class TestDrugShortageDocument:
    """Test cases for DrugShortageDocument data model."""
    
    def test_create_valid_shortage_document(self):
        """Test creating a valid drug shortage document."""
        doc = DrugShortageDocument(
            product_name="JAMP VORICONAZOLE 50MG",
            ingredient="Voriconazole",
            matched_ingredient="Voriconazole",
            status="Actual shortage",
            date_reported="2025-12-11",
            reason="",
            source_url="https://www.drugshortagescanada.ca/shortage/271035",
            manufacturer="JAMP PHARMA CORPORATION",
            expected_resolution="",
            source="Drug Shortages Canada",
            source_country="CA",
            scraped_at="2025-12-16T21:37:47.403152"
        )
        
        assert doc.product_name == "JAMP VORICONAZOLE 50MG"
        assert doc.ingredient == "Voriconazole"
        assert doc.status == "Actual shortage"
        assert doc.source_country == "CA"
        
    def test_shortage_document_validation_success(self):
        """Test successful validation of shortage document."""
        doc = DrugShortageDocument(
            product_name="Test Product",
            ingredient="Test Ingredient",
            matched_ingredient="Test Ingredient",
            status="Shortage",
            date_reported="2025-12-11",
            reason="",
            source_url="https://example.com",
            manufacturer="Test Manufacturer",
            expected_resolution="",
            source="Test Source",
            source_country="CA",
            scraped_at="2025-12-16T21:37:47.403152"
        )
        
        assert doc.validate_data_integrity() is True
        
    def test_shortage_document_validation_empty_product_name(self):
        """Test validation failure for empty product name."""
        doc = DrugShortageDocument(
            product_name="",  # Empty product name
            ingredient="Test Ingredient",
            matched_ingredient="Test Ingredient",
            status="Shortage",
            date_reported="2025-12-11",
            reason="",
            source_url="https://example.com",
            manufacturer="Test Manufacturer",
            expected_resolution="",
            source="Test Source",
            source_country="CA",
            scraped_at="2025-12-16T21:37:47.403152"
        )
        
        with pytest.raises(ValueError, match="must have a non-empty product name"):
            doc.validate_data_integrity()
            
    def test_shortage_document_validation_empty_ingredient(self):
        """Test validation failure for empty ingredient."""
        doc = DrugShortageDocument(
            product_name="Test Product",
            ingredient="",  # Empty ingredient
            matched_ingredient="Test Ingredient",
            status="Shortage",
            date_reported="2025-12-11",
            reason="",
            source_url="https://example.com",
            manufacturer="Test Manufacturer",
            expected_resolution="",
            source="Test Source",
            source_country="CA",
            scraped_at="2025-12-16T21:37:47.403152"
        )
        
        with pytest.raises(ValueError, match="must have a non-empty ingredient"):
            doc.validate_data_integrity()
            
    def test_shortage_document_from_dict(self):
        """Test creating DrugShortageDocument from dictionary."""
        data = {
            "product_name": "JAMP VORICONAZOLE 50MG",
            "ingredient": "Voriconazole",
            "matched_ingredient": "Voriconazole",
            "status": "Actual shortage",
            "date_reported": "2025-12-11",
            "reason": "",
            "source_url": "https://www.drugshortagescanada.ca/shortage/271035",
            "manufacturer": "JAMP PHARMA CORPORATION",
            "expected_resolution": "",
            "source": "Drug Shortages Canada",
            "source_country": "CA",
            "scraped_at": "2025-12-16T21:37:47.403152"
        }
        
        doc = DrugShortageDocument.from_dict(data)
        
        assert doc.product_name == "JAMP VORICONAZOLE 50MG"
        assert doc.ingredient == "Voriconazole"
        assert doc.status == "Actual shortage"
        assert doc.source == "Drug Shortages Canada"
        
    def test_shortage_document_to_dict(self):
        """Test converting DrugShortageDocument to dictionary."""
        doc = DrugShortageDocument(
            product_name="Test Product",
            ingredient="Test Ingredient",
            matched_ingredient="Test Ingredient",
            status="Shortage",
            date_reported="2025-12-11",
            reason="",
            source_url="https://example.com",
            manufacturer="Test Manufacturer",
            expected_resolution="",
            source="Test Source",
            source_country="CA",
            scraped_at="2025-12-16T21:37:47.403152"
        )
        
        result = doc.to_dict()
        
        assert result['product_name'] == "Test Product"
        assert result['ingredient'] == "Test Ingredient"
        assert result['status'] == "Shortage"
        assert result['source_country'] == "CA"