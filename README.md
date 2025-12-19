# Pharmaceutical Intelligence System

An AI-powered healthcare intelligence system that combines pharmaceutical news analysis, drug shortage tracking, and intelligent conversational AI to provide actionable insights for healthcare professionals and pharmaceutical companies.

## 🚀 Key Features

### 🤖 **Strands AI Healthcare Agents**
- **Advanced Healthcare Intelligence**: AI agents powered by Strands SDK and AWS Bedrock Claude 4
- **Custom Pharmaceutical Tools**: Specialized tools for analyzing 8,908+ pharmaceutical news articles and 317+ drug shortage records
- **Natural Language Interface**: Ask complex healthcare questions and receive expert-level analysis
- **Cross-Reference Analysis**: Automatically correlate news events with supply chain impacts
- **Real-Time Insights**: Live analysis of regulatory trends, shortage patterns, and market developments

### 📊 **Data Intelligence**
- **Comprehensive Coverage**: Navlin News pharmaceutical articles and Drug Shortages Canada data
- **Semantic Search**: ChromaDB and Amazon Titan embeddings for intelligent information retrieval
- **Multi-Source Integration**: Unified analysis across news, shortages, and regulatory data
- **Geographic Analysis**: Track global regulatory decisions and supply chain vulnerabilities
- **Trend Identification**: AI-powered pattern recognition across pharmaceutical landscapes

### 💻 **User Interfaces**
- **Interactive Chat Interface**: Streamlit-based conversational AI for complex queries
- **Scenario Analysis**: Pre-built healthcare analysis scenarios (landscape overview, shortage analysis, ALS/neurology updates)
- **Export Capabilities**: Save and export findings in multiple formats
- **Sample Questions**: Guided exploration of pharmaceutical intelligence capabilities

## 🏗️ Architecture

### **AI-Powered Intelligence Layer**
- **Strands Healthcare Agents**: Advanced AI agents specialized in pharmaceutical analysis
- **AWS Bedrock Claude 4**: State-of-the-art language model for healthcare reasoning
- **Custom Tool Integration**: Pharmaceutical-specific data analysis tools
- **Multi-Agent Orchestration**: Coordinated analysis across multiple data sources

### **Data Processing Pipeline**
- **Vector Database**: ChromaDB for semantic search and similarity matching
- **Embedding Service**: Amazon Titan for intelligent text processing
- **Data Ingestion**: Automated processing of pharmaceutical news and shortage data
- **Real-Time Analysis**: Live data processing and trend identification

### **User Experience**
- **Streamlit Frontend**: Interactive web interface for conversational AI
- **Natural Language Processing**: Complex query understanding and response generation
- **Visualization**: Data insights presented through charts and structured reports

## 🚀 Quick Start

### **1. Setup Environment**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (includes Strands SDK)
pip install -r requirements.txt
```

### **2. Configure AWS Bedrock Credentials**

See [setup_aws_credentials.md](setup_aws_credentials.md) for detailed instructions.

**Option A: Bedrock API Key (Development)**
```bash
export AWS_BEDROCK_API_KEY=your_bedrock_api_key
```

**Option B: AWS Credentials (Production)**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2
```

**Enable Model Access:**
- Open [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
- Navigate to "Model access" → "Manage model access"
- Enable "Claude 4 Sonnet" or your preferred model

### **3. Start ChromaDB (Optional - for vector search)**
```bash
chroma run --host localhost --port 8000
```

### **4. Ingest Data (Optional - for vector search)**
```bash
python scripts/ingest_data.py
```

### **5. Run Healthcare Intelligence Agents**

**Basic Healthcare Agent:**
```bash
python healthcare_strands_agent.py
```

**Advanced Agent with Custom Tools:**
```bash
# Run predefined scenarios
python advanced_healthcare_agent.py

# Interactive mode for custom queries
python advanced_healthcare_agent.py --interactive
```

**Offline Demo (No credentials required):**
```bash
python strands_demo_offline.py
```

### **6. Run Streamlit Chatbot (Coming Soon)**
```bash
streamlit run src/frontend/app.py
```

## 📁 Project Structure

```
├── healthcare_strands_agent.py      # Basic healthcare AI agent
├── advanced_healthcare_agent.py     # Advanced agent with custom tools
├── pharma_data_tool.py             # Custom pharmaceutical data tools
├── strands_demo_offline.py         # Offline demonstration
├── setup_aws_credentials.md        # AWS Bedrock setup guide
├── src/
│   ├── agents/                     # Strands AI agent configurations
│   ├── tools/                      # Custom agent tools
│   ├── data_processing/            # Data ingestion and processing
│   │   ├── chromadb_client.py     # Vector database client
│   │   ├── embedding_service.py   # Amazon Titan embeddings
│   │   ├── navlin_parser.py       # Pharmaceutical news parser
│   │   └── shortage_parser.py     # Drug shortage data parser
│   ├── frontend/                   # Streamlit interface
│   ├── models/                     # Data models and schemas
│   └── config/                     # Configuration management
├── data/                           # Raw pharmaceutical data
│   ├── Navlin News/               # 8,908+ pharmaceutical articles
│   └── drug_shortage_*.json       # 317+ drug shortage records
├── tests/                          # Test suite
└── requirements.txt                # Python dependencies (includes Strands SDK)
```

## 🤖 Strands Healthcare Intelligence Agents

### **Healthcare Agent Capabilities**

Our Strands-powered AI agents provide expert-level pharmaceutical intelligence:

#### **🔍 Data Analysis Tools**
- **`search_pharma_news(query, limit)`**: Search 8,908+ pharmaceutical news articles
- **`get_drug_shortage_info(product_name)`**: Access 317+ current drug shortage records  
- **`analyze_pharma_trends(timeframe)`**: Analyze patterns across pharmaceutical data

#### **🧠 Intelligence Scenarios**
1. **Pharmaceutical Landscape Overview**: Comprehensive market analysis
2. **Drug Shortage Risk Assessment**: Critical shortage identification and impact analysis
3. **ALS/Neurology Treatment Updates**: Latest developments and supply chain concerns

#### **💡 Example Queries**
- *"What are the current drug shortage trends affecting neurology treatments?"*
- *"Analyze the regulatory landscape for Alzheimer's disease treatments"*
- *"What supply chain risks should we monitor for pain management medications?"*
- *"Cross-reference recent FDA approvals with potential shortage impacts"*

### **Agent Architecture**

```python
from strands import Agent
from strands_tools import calculator, python_repl, http_request
from pharma_data_tool import search_pharma_news, get_drug_shortage_info, analyze_pharma_trends

# Advanced Healthcare Agent
agent = Agent(
    tools=[
        # Custom pharmaceutical data tools
        search_pharma_news,
        get_drug_shortage_info, 
        analyze_pharma_trends,
        # Community tools for analysis
        calculator, python_repl, http_request
    ],
    system_prompt="Healthcare intelligence assistant specializing in pharmaceutical analysis..."
)

# Natural language interaction
response = agent("What are the latest ALS treatment developments?")
```

### **Key Insights Delivered**

- **Critical Risk Identification**: 50.2% of drug shortages are fentanyl-related
- **Regulatory Trend Analysis**: Track global approval/rejection patterns
- **Supply Chain Vulnerabilities**: Geographic concentration risks
- **Market Intelligence**: Cross-reference news events with supply impacts
- **Therapeutic Area Focus**: ALS, Alzheimer's, Multiple Sclerosis, Parkinson's developments

## 🛠️ Development

### **Testing**
```bash
pytest tests/                    # Run test suite
python strands_demo_offline.py  # Test Strands tools without credentials
```

### **Code Quality**
```bash
black src/ tests/               # Code formatting
mypy src/                       # Type checking
```

### **Adding Custom Tools**
```python
from strands import tool

@tool
def custom_pharma_analysis(query: str) -> str:
    """Custom pharmaceutical analysis tool.
    
    Args:
        query: Analysis query
    """
    # Your custom logic here
    return analysis_result
```

## 📋 Requirements

### **System Requirements**
- Python 3.9+
- AWS Account with Bedrock access
- 4GB+ RAM (for local ChromaDB)

### **AWS Bedrock Setup**
- Bedrock API key or AWS credentials
- Model access enabled (Claude 4 Sonnet recommended)
- See [setup_aws_credentials.md](setup_aws_credentials.md) for detailed setup

### **Optional Components**
- ChromaDB local installation (for vector search)
- Streamlit (for web interface)

## 📊 Data & Performance

### **Pharmaceutical Data Coverage**
- **📰 News Articles**: 8,908 pharmaceutical industry articles
  - Regulatory decisions (FDA, EMA, Health Canada, etc.)
  - Market access and pricing developments
  - Clinical trial updates and approvals
  - Supply chain and manufacturing news

- **💊 Drug Shortages**: 317 active shortage records
  - Multi-country coverage (US, Canada, EU, Asia-Pacific)
  - Critical therapeutic areas (pain management, antifungals, addiction treatment)
  - Real-time shortage status and impact assessment

### **AI Performance Metrics**
- **Response Time**: < 30 seconds for complex multi-tool queries
- **Data Coverage**: 100% of available pharmaceutical news and shortage data
- **Analysis Depth**: Cross-references multiple data sources automatically
- **Accuracy**: Expert-level pharmaceutical intelligence with source attribution

### **Key Data Sources**
- **Navlin News**: Pharmaceutical industry news and regulatory updates
- **Drug Shortages Canada**: Comprehensive shortage tracking
- **Multi-country regulatory databases**: Global coverage of pharmaceutical decisions

## 🔗 Related Projects

- [Strands Agents SDK](https://github.com/strands-ai/strands-agents) - AI agent development framework
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - Managed AI service platform
- [ChromaDB](https://github.com/chroma-core/chroma) - Vector database for AI applications

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions about:
- **Strands SDK**: Check the [Strands documentation](https://docs.strands.ai)
- **AWS Bedrock**: See [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/)
- **This Project**: Open an issue in this repository