#!/usr/bin/env python3
"""
Healthcare Data Analysis Agent

This agent can analyze pharmaceutical news and drug shortage data using Strands SDK.
Perfect for your healthcare data project!
"""

from strands import Agent
from strands_tools import calculator, python_repl, http_request
import json
import os

def create_healthcare_agent():
    """Create an agent specialized in healthcare data analysis."""
    
    # System prompt tailored to your healthcare data project
    system_prompt = """You are a healthcare data analysis expert specializing in:
    
    - Pharmaceutical news analysis (ALS/neurology focus)
    - Drug shortage tracking and impact assessment
    - Regulatory decision analysis
    - Cross-referencing news events with supply chain data
    
    You have access to tools for calculations, web requests, and Python code execution.
    When analyzing data, focus on:
    - Geographic patterns (countries, regions)
    - Temporal trends (dates, timelines)
    - Therapeutic areas and drug classifications
    - Supply chain impacts and shortages
    
    Always provide clear, actionable insights for healthcare professionals."""
    
    # Create agent with community tools
    agent = Agent(
        tools=[calculator, python_repl, http_request],
        system_prompt=system_prompt
    )
    
    return agent

def test_agent():
    """Test the agent with a simple healthcare query."""
    
    print("🏥 Creating Healthcare Data Analysis Agent...")
    agent = create_healthcare_agent()
    
    print("\n🤖 Testing agent with a healthcare question...")
    
    # Test with a healthcare-related question
    response = agent("""
    I have pharmaceutical data showing drug shortages in multiple countries. 
    Can you help me understand what key metrics I should track to analyze 
    the impact of these shortages on patient care?
    """)
    
    print(f"\n📊 Agent Response:\n{response}")
    
    # Test conversation memory
    print("\n🧠 Testing conversation memory...")
    follow_up = agent("What about geographic patterns? How should I analyze those?")
    print(f"\n🌍 Follow-up Response:\n{follow_up}")

def analyze_sample_data():
    """Demonstrate analyzing your actual data files."""
    
    print("\n📁 Analyzing your actual data files...")
    agent = create_healthcare_agent()
    
    # Check if data files exist
    data_files = [
        "data/drug_shortage_combined_20251216_214653.json",
        "data/Navlin News/als_news_all.json"
    ]
    
    existing_files = [f for f in data_files if os.path.exists(f)]
    
    if existing_files:
        response = agent(f"""
        I have these healthcare data files: {existing_files}
        
        Can you help me create a Python script to:
        1. Load and examine the structure of these JSON files
        2. Identify key fields for analysis
        3. Suggest initial data exploration steps
        
        Focus on pharmaceutical news and drug shortage patterns.
        """)
        
        print(f"\n📈 Data Analysis Suggestions:\n{response}")
    else:
        print("No data files found. Make sure your data files are in the correct location.")

if __name__ == "__main__":
    # Check for AWS credentials
    if not (os.getenv('AWS_BEDROCK_API_KEY') or 
            (os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'))):
        print("❌ AWS credentials not found!")
        print("\nTo use this agent, you need AWS credentials for Bedrock:")
        print("1. Get a Bedrock API key: https://console.aws.amazon.com/bedrock")
        print("2. Set it: export AWS_BEDROCK_API_KEY=your_key")
        print("3. Enable model access in Bedrock console")
        print("\nThen run this script again!")
        exit(1)
    
    print("🚀 Starting Healthcare Data Analysis Agent Demo")
    print("=" * 50)
    
    try:
        # Basic agent test
        test_agent()
        
        # Analyze your actual data
        analyze_sample_data()
        
        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("- Set up your AWS credentials if you haven't already")
        print("- Modify the system prompt for your specific use case")
        print("- Add custom tools for your data processing needs")
        print("- Integrate with your ChromaDB setup")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure AWS credentials are set")
        print("2. Enable model access in Bedrock console")
        print("3. Check your internet connection")