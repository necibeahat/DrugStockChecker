# Design Document

## Overview

The Pharmaceutical Competitive Intelligence Chatbot is a sophisticated AI-powered system that enables business analysts to query and analyze pharmaceutical news and drug shortage data through natural language conversations. The system leverages ChromaDB for semantic search, Strands SDK for agent orchestration, and Streamlit for the user interface, creating a comprehensive solution for competitive intelligence in the pharmaceutical industry.

The system serves two primary user personas: business analysts who need quick access to competitive intelligence insights, and system engineers who manage data ingestion and system maintenance. The architecture emphasizes semantic search capabilities, real-time data access, and intuitive natural language querying.

## Architecture

The system follows a layered architecture with clear separation of concerns:

### Frontend Layer
- **Streamlit Interface**: Web-based chat interface providing conversational access to pharmaceutical data
- **User Session Management**: Maintains conversation history and user context
- **Query Interface**: Natural language input processing and response formatting

### Agent Layer
- **Strands Agent**: Core AI agent built using Strands SDK with Claude 4 on AWS Bedrock
- **Query Processing**: Natural language understanding and intent classification
- **Response Generation**: Contextual response synthesis with source attribution

### Tool Layer
- **ChromaDB Query Tool**: Semantic search and retrieval from vector database
- **Data Analysis Tool**: Statistical analysis and trend identification
- **Export Tool**: Data export and report generation capabilities

### Data Layer
- **ChromaDB Vector Database**: Stores pharmaceutical news and shortage data as embeddings
- **JSON Data Sources**: Raw data files from Navlin News and Drug Shortages Canada
- **Embedding Service**: Amazon Titan for text embedding generation

### Infrastructure Layer
- **AWS Bedrock**: Model hosting and inference
- **Local ChromaDB Instance**: Vector database deployment
- **Python Virtual Environment**: Isolated runtime environment

## Components and Interfaces

### Streamlit Frontend Component
```python
class ChatInterface:
    - display_chat_history()
    - process_user_input()
    - render_response()
    - show_sample_questions()
```

### Strands Agent Component
```python
class PharmaIntelligenceAgent:
    - process_query(query: str) -> str
    - classify_intent(query: str) -> QueryIntent
    - generate_response(results: List[Document]) -> str
```

### ChromaDB Integration Tool
```python
class ChromaDBTool:
    - semantic_search(query: str, filters: Dict) -> List[Document]
    - get_similar_documents(doc_id: str) -> List[Document]
    - get_collection_stats() -> Dict
```

### Data Ingestion Component
```python
class DataIngestionService:
    - ingest_navlin_news(file_path: str) -> int
    - ingest_drug_shortages(file_path: str) -> int
    - create_embeddings(text: str) -> List[float]
    - update_collection(documents: List[Document]) -> bool
```

## Data Models

### News Document Model
```python
@dataclass
class NewsDocument:
    id: int
    title: str
    date: str
    countries: List[str]
    country_codes: List[Dict[str, str]]
    regions: List[str]
    keywords: List[str]
    product_groups: List[str]
    therapeutic_areas: List[str]
    indications: List[str]
    content_html: str
    types: List[Dict]
    topic: str
    source: str = "Navlin News"
```

### Drug Shortage Document Model
```python
@dataclass
class DrugShortageDocument:
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
```

### Query Intent Model
```python
@dataclass
class QueryIntent:
    intent_type: str  # regulatory, pricing, supply_chain, competitive
    geographic_filter: List[str]
    therapeutic_filter: List[str]
    time_filter: Dict[str, str]
    entity_filter: List[str]  # companies, products
```

### Search Result Model
```python
@dataclass
class SearchResult:
    document: Union[NewsDocument, DrugShortageDocument]
    relevance_score: float
    source_type: str
    metadata: Dict[str, Any]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, I need to perform property reflection to eliminate redundancy before writing the correctness properties:

**Property Reflection:**

After reviewing all testable properties from the prework, I identified several areas of redundancy:

1. **Citation and Attribution Properties (1.3, 7.1, 8.2)**: These all test that responses include proper source attribution. Can be combined into one comprehensive property.

2. **Filter Properties (5.1, 5.2, 5.3, 5.4)**: These test different types of filtering but can be combined into a single property about filter functionality.

3. **Data Ingestion Properties (3.1, 3.2, 3.3)**: These test different aspects of data processing but can be combined into one comprehensive ingestion property.

4. **Query Type Properties (4.1, 4.2, 4.3, 4.4, 4.5)**: These test different query types but can be combined into a single property about query classification and response relevance.

5. **Empty Result Handling (1.5, 5.5)**: Both test graceful handling of no-results scenarios and can be combined.

**Property 1: Semantic Search Relevance**
*For any* natural language query about pharmaceutical data, the system should return results that are semantically relevant to the query intent and combine information from both news and shortage data sources when applicable
**Validates: Requirements 1.1, 1.2, 1.4**

**Property 2: Source Attribution Completeness**
*For any* system response containing pharmaceutical information, the response should include complete source attribution with dates, countries, original data sources, and maintain this attribution through export processes
**Validates: Requirements 1.3, 7.1, 8.2**

**Property 3: Sample Question Coverage**
*For any* set of sample questions displayed to users, the questions should be properly categorized by analysis type and cover different therapeutic areas, geographic regions, and time periods
**Validates: Requirements 2.2, 2.4**

**Property 4: Sample Question Execution**
*For any* sample question provided by the system, selecting and executing that question should produce comprehensive results with explanations
**Validates: Requirements 2.3**

**Property 5: Data Ingestion Completeness**
*For any* JSON data file in the data directory, the ingestion process should successfully extract and index all required fields, create vector embeddings, and provide completion statistics
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

**Property 6: Duplicate Data Handling**
*For any* duplicate records detected during ingestion, the system should handle updates appropriately without creating redundant entries
**Validates: Requirements 3.5**

**Property 7: Query Classification and Response Relevance**
*For any* query classified as regulatory, pricing, supply chain, competitive, or therapeutic area focused, the system should return information specifically relevant to that classification
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

**Property 8: Filter Functionality**
*For any* combination of geographic, temporal, or therapeutic area filters applied to a query, the system should return data that matches all specified criteria using logical AND operations
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

**Property 9: Empty Result Handling**
*For any* query or filter combination that produces no results, the system should provide helpful suggestions for alternative queries, broader criteria, or related topics
**Validates: Requirements 1.5, 5.5**

**Property 10: System Status Reporting**
*For any* system status check, the system should report ChromaDB connection status, data freshness metrics, and query performance statistics
**Validates: Requirements 6.1**

**Property 11: Ingestion Process Logging**
*For any* data ingestion process execution, the system should generate logs containing processing status, error rates, and completion times
**Validates: Requirements 6.2**

**Property 12: Data Quality Alerting**
*For any* data inconsistencies detected during processing, the system should generate alerts with specific details about affected records
**Validates: Requirements 6.4**

**Property 13: Source Corroboration Indication**
*For any* finding supported by multiple sources, the system should indicate the level of corroboration and present multiple perspectives when conflicting information exists
**Validates: Requirements 7.2, 7.5**

**Property 14: Temporal Context Highlighting**
*For any* information with temporal relevance, the system should highlight data recency and currency in responses
**Validates: Requirements 7.3**

**Property 15: Confidence Indicator Provision**
*For any* response where data quality varies, the system should provide confidence indicators based on source reliability and data completeness
**Validates: Requirements 7.4**

**Property 16: Export and Save Functionality**
*For any* valuable information found by users, the system should provide export options in structured formats and allow query bookmarking for future reference
**Validates: Requirements 8.1, 8.3**

**Property 17: Shared Content Formatting**
*For any* results being shared, the system should provide formatted summaries suitable for reports and presentations
**Validates: Requirements 8.4**

**Property 18: Saved Content Organization**
*For any* saved queries and results, the system should organize them in a searchable and accessible format
**Validates: Requirements 8.5**

## Error Handling

The system implements comprehensive error handling across all layers:

### Query Processing Errors
- **Invalid Query Format**: Graceful handling of malformed natural language queries with user-friendly error messages
- **Semantic Search Failures**: Fallback to keyword search when semantic search fails
- **Empty Results**: Automatic suggestion generation for alternative queries

### Data Layer Errors
- **ChromaDB Connection Failures**: Automatic retry logic with exponential backoff
- **Embedding Generation Failures**: Error logging and graceful degradation to keyword search
- **Data Corruption**: Validation checks during ingestion with detailed error reporting

### Agent Layer Errors
- **Model Inference Failures**: Retry logic with fallback to cached responses when appropriate
- **Tool Execution Failures**: Error isolation to prevent cascade failures
- **Context Length Exceeded**: Automatic context truncation with preservation of key information

### Frontend Layer Errors
- **Session Management Failures**: Automatic session recovery with conversation history preservation
- **UI Rendering Errors**: Graceful degradation with basic text-based interface fallback
- **Export Failures**: Alternative export format options and error reporting

## Testing Strategy

The testing approach combines unit testing and property-based testing to ensure comprehensive coverage:

### Unit Testing Approach
- **Component Integration Tests**: Verify proper integration between Streamlit frontend, Strands agent, and ChromaDB
- **Data Processing Tests**: Validate JSON parsing, embedding generation, and database operations
- **Query Processing Tests**: Test specific query patterns and response formatting
- **Error Handling Tests**: Verify graceful failure handling and recovery mechanisms

### Property-Based Testing Approach
- **Testing Framework**: Hypothesis for Python property-based testing
- **Test Configuration**: Minimum 100 iterations per property test to ensure statistical significance
- **Property Test Tagging**: Each property-based test tagged with format: '**Feature: pharma-intelligence-chatbot, Property {number}: {property_text}**'
- **Generator Strategy**: Smart generators that create realistic pharmaceutical queries, data structures, and filter combinations
- **Coverage Strategy**: Property tests verify universal behaviors across all valid inputs while unit tests catch specific edge cases

### Dual Testing Benefits
- **Unit tests** catch concrete bugs in specific scenarios and integration points
- **Property tests** verify general correctness across the entire input space
- **Combined coverage** ensures both specific functionality and universal properties are validated

The property-based testing framework will generate diverse test cases including:
- Random pharmaceutical queries across different therapeutic areas
- Various filter combinations and edge cases
- Different data structures and formats
- Error conditions and boundary cases

This comprehensive testing strategy ensures the system maintains correctness properties while handling the complexity and variability inherent in pharmaceutical competitive intelligence data.