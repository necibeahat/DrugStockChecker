# Technology Stack

## Core AI & Agent Technologies
- **Strands SDK** for all AI agent development and orchestration
- **AWS Bedrock Claude 4** for advanced reasoning and analysis
- **Amazon Titan** for embeddings and text processing
- **ChromaDB local installation** for ingesting JSON files

## Frontend Technologies
- **Streamlit** for front-end chat bot interface

## Environment
- **Python**: Primary language (indicated by `.venv` virtual environment)
- **Data Format**: JSON for all data storage and exchange
- **Platform**: Cross-platform development

## Data Processing
- JSON-based data pipeline for pharmaceutical news and drug shortage information
- ChromaDB for vector storage and semantic search of pharmaceutical data
- Structured data schemas with standardized fields:
  - Country codes (ISO format)
  - Regional classification
  - Therapeutic areas and indications
  - Timestamp tracking for data freshness

## Project Structure
- Virtual environment management with `.venv/`
- Data-centric architecture with organized JSON files
- Separation of different data sources (Navlin News vs Drug Shortages)
- AI agent orchestration through Strands SDK

## Common Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start ChromaDB local instance
chroma run --host localhost --port 8000

# Run Streamlit chatbot interface
streamlit run app.py

# Process and ingest JSON data into ChromaDB
python ingest_data.py

# Run Strands agent workflows
python agent_runner.py

# Deactivate environment
deactivate
```

## Data Conventions
- All timestamps in ISO format
- Consistent JSON structure across data sources
- Standardized country/region coding
- Structured keyword and classification systems