#!/usr/bin/env python3
"""
Healthcare Intelligence Agent using Strands SDK

This agent specializes in pharmaceutical news analysis and drug shortage tracking.
It can help analyze your healthcare data and provide insights.
"""

from strands import Agent
from strands_tools import calculator, python_repl, http_request
import os

def create_healthcare_agent():
    """Create a healthcare-focused agent with relevant tools."""
    
    # System prompt tailored for healthcare/pharmaceutical domain
    system_prompt = """You are a healthcare intelligence assistant specializing in:

1. Pharmaceutical news analysis and regulatory decisions
2. Drug shortage tracking and supply chain insights  
3. ALS/neurology treatment developments
4. Cross-referencing news events with supply impacts
5. Data analysis of healthcare trends

You have access to tools for calculations, web requests, and Python code execution.
When analyzing data, focus on:
- Regulatory implications
- Supply chain impacts
- Treatment availability
- Geographic patterns
- Temporal trends

Be precise, evidence-based, and highlight critical healthcare insights.
"""

    # Create agent with community tools
    agent = Agent(
        tools=[calculator, python_repl, http_request],
        system_prompt=system_prompt
    )
    
    return agent

def main():
    """Test the healthcare agent."""
    print("🏥 Creating Healthcare Intelligence Agent...")
    
    # Check for credentials
    if not (os.getenv('AWS_BEDROCK_API_KEY') or 
            (os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'))):
        print("⚠️  AWS credentials not found!")
        print("\nTo use this agent, set up AWS Bedrock credentials:")
        print("1. Get Bedrock API key: https://console.aws.amazon.com/bedrock")
        print("2. Enable model access in Bedrock console")
        print("3. Set environment variable:")
        print("   export AWS_BEDROCK_API_KEY=your_key_here")
        print("\nOr use AWS credentials:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        return
    
    try:
        agent = create_healthcare_agent()
        print("✅ Agent created successfully!")
        
        # Test with a healthcare-related question
        print("\n🧪 Testing agent with healthcare question...")
        response = agent("What are the key factors that typically cause drug shortages in the pharmaceutical industry?")
        print(f"\n🤖 Agent Response:\n{response}")
        
        # Test conversation memory
        print("\n🧠 Testing conversation memory...")
        response2 = agent("Can you give me 3 specific examples related to my previous question?")
        print(f"\n🤖 Agent Response:\n{response2}")
        
    except Exception as e:
        print(f"❌ Error creating or testing agent: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure AWS Bedrock model access is enabled")
        print("2. Check your AWS credentials are valid")
        print("3. Verify you have internet connectivity")

if __name__ == "__main__":
    main()