# Pharmaceutical Intelligence Chatbot

An AI-powered competitive intelligence system for pharmaceutical companies, enabling business analysts to query and analyze pharmaceutical news and drug shortage data through natural language conversations.

## Features

- **Natural Language Querying**: Ask questions about pharmaceutical news and drug shortages in plain English
- **Semantic Search**: Powered by ChromaDB and Amazon Titan embeddings for intelligent information retrieval
- **Multi-Source Data**: Integrates Navlin News and Drug Shortages Canada data
- **Interactive Interface**: Streamlit-based chat interface with sample questions and filtering
- **Export Capabilities**: Save and export findings in multiple formats

## Architecture

- **Frontend**: Streamlit web interface
- **AI Agent**: Strands SDK with Claude 4 on AWS Bedrock
- **Vector Database**: ChromaDB for semantic search
- **Data Sources**: JSON files from pharmaceutical news and shortage databases

## Quick Start

1. **Setup Environment**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your AWS credentials and preferences
   ```

3. **Start ChromaDB**
   ```bash
   chroma run --host localhost --port 8000
   ```

4. **Ingest Data**
   ```bash
   python -m src.data_processing.ingest
   ```

5. **Run Chatbot**
   ```bash
   streamlit run src/frontend/app.py
   ```

## Project Structure

```
├── src/
│   ├── agents/          # Strands AI agents
│   ├── tools/           # Custom agent tools
│   ├── data_processing/ # Data ingestion and processing
│   ├── frontend/        # Streamlit interface
│   ├── models/          # Data models and schemas
│   └── config/          # Configuration management
├── data/                # Raw data files
├── tests/               # Test suite
└── requirements.txt     # Python dependencies
```

## Development

- **Testing**: `pytest tests/`
- **Code Formatting**: `black src/ tests/`
- **Type Checking**: `mypy src/`

## Requirements

- Python 3.9+
- AWS Account with Bedrock access
- ChromaDB local installation