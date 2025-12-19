"""Configuration settings for the Pharmaceutical Intelligence Chatbot."""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    
    # ChromaDB settings
    CHROMADB_HOST: str = Field(default="localhost", env="CHROMADB_HOST")
    CHROMADB_PORT: int = Field(default=8000, env="CHROMADB_PORT")
    CHROMADB_COLLECTION_NEWS: str = Field(default="pharma_news", env="CHROMADB_COLLECTION_NEWS")
    CHROMADB_COLLECTION_SHORTAGES: str = Field(default="drug_shortages", env="CHROMADB_COLLECTION_SHORTAGES")
    
    # AWS Bedrock settings
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    BEDROCK_MODEL_ID: str = Field(default="anthropic.claude-3-5-sonnet-20241022-v2:0", env="BEDROCK_MODEL_ID")
    TITAN_EMBEDDING_MODEL_ID: str = Field(default="amazon.titan-embed-text-v1", env="TITAN_EMBEDDING_MODEL_ID")
    
    # Streamlit settings
    STREAMLIT_PORT: int = Field(default=8501, env="STREAMLIT_PORT")
    STREAMLIT_HOST: str = Field(default="localhost", env="STREAMLIT_HOST")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Data processing
    BATCH_SIZE: int = Field(default=100, env="BATCH_SIZE")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()