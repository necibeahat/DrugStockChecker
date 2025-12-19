#!/usr/bin/env python3
"""
Advanced Healthcare Agent with Custom Pharmaceutical Data Tools

This agent combines Strands SDK with your custom pharmaceutical data tools
to provide intelligent analysis of drug shortages and pharma news.
"""

from strands import Agent
from strands_tools import calculator, python_repl, http_request
from pharma_data_tool import search_pharma_news, get_drug_shortage_info, analyze_pharma_trends
import os

def create_advanced_healthcare_agent():
    """Create an advanced healthcare agent with custom pharmaceutical data tools."""
    
    system_prompt = """You are an advanced healthcare intelligence assistant with access to:

🔍 SPECIALIZED DATA TOOLS:
- search_pharma_news(): Search pharmaceutical news and regulatory updates
- get_drug_shortage_info(): Access current drug shortage information  
- analyze_pharma_trends(): Analyze patterns in pharmaceutical data

🧮 GENERAL TOOLS:
- calculator: Perform calculations and statistical analysis
- python_repl: Execute Python code for data processing
- http_request: Fetch additional web-based information

🎯 YOUR EXPERTISE:
- Pharmaceutical regulatory decisions and their implications
- Drug shortage analysis and supply chain insights
- ALS/neurology treatment developments and clinical updates
- Cross-referencing news events with supply chain impacts
- Geographic and temporal trend analysis
- Risk assessment for pharmaceutical supply chains

📋 ANALYSIS APPROACH:
1. Always start with your specialized data tools to gather relevant information
2. Cross-reference findings across news and shortage data
3. Identify patterns, correlations, and potential impacts
4. Provide actionable insights with supporting evidence
5. Highlight critical healthcare implications

Be thorough, evidence-based, and focus on actionable healthcare intelligence.
"""

    # Create agent with both community tools and custom pharmaceutical tools
    agent = Agent(
        tools=[
            # Custom pharmaceutical data tools
            search_pharma_news,
            get_drug_shortage_info, 
            analyze_pharma_trends,
            # Community tools for general analysis
            calculator,
            python_repl,
            http_request
        ],
        system_prompt=system_prompt
    )
    
    return agent

def run_healthcare_scenarios():
    """Run example healthcare analysis scenarios."""
    
    print("🏥 Creating Advanced Healthcare Intelligence Agent...")
    
    # Check for credentials
    if not (os.getenv('AWS_BEDROCK_API_KEY') or 
            (os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'))):
        print("⚠️  AWS credentials not found!")
        print("\nTo use this agent, set up AWS Bedrock credentials:")
        print("1. Get Bedrock API key: https://console.aws.amazon.com/bedrock")
        print("2. Enable model access in Bedrock console") 
        print("3. Set environment variable:")
        print("   export AWS_BEDROCK_API_KEY=your_key_here")
        return
    
    try:
        agent = create_advanced_healthcare_agent()
        print("✅ Advanced agent created successfully!")
        
        # Scenario 1: General pharmaceutical landscape analysis
        print("\n" + "="*60)
        print("📊 SCENARIO 1: Pharmaceutical Landscape Overview")
        print("="*60)
        response = agent("Give me an overview of the current pharmaceutical landscape based on our data. What are the key trends in both news and drug shortages?")
        print(f"\n🤖 Agent Analysis:\n{response}")
        
        # Scenario 2: Specific drug shortage investigation
        print("\n" + "="*60)
        print("💊 SCENARIO 2: Drug Shortage Analysis")
        print("="*60)
        response = agent("I'm concerned about potential drug shortages. Can you analyze our shortage data and identify any critical patterns or high-risk areas?")
        print(f"\n🤖 Agent Analysis:\n{response}")
        
        # Scenario 3: ALS/Neurology focus
        print("\n" + "="*60)
        print("🧠 SCENARIO 3: ALS/Neurology Treatment Updates")
        print("="*60)
        response = agent("What are the latest developments in ALS and neurology treatments based on our news data? Are there any related supply chain concerns?")
        print(f"\n🤖 Agent Analysis:\n{response}")
        
        print("\n" + "="*60)
        print("✅ Healthcare analysis scenarios completed!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error running scenarios: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure AWS Bedrock model access is enabled")
        print("2. Check your AWS credentials are valid")
        print("3. Verify your data files are accessible")

def interactive_mode():
    """Run the agent in interactive mode for custom queries."""
    
    print("🏥 Starting Interactive Healthcare Agent...")
    
    if not (os.getenv('AWS_BEDROCK_API_KEY') or 
            (os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'))):
        print("⚠️  AWS credentials required for interactive mode")
        return
    
    try:
        agent = create_advanced_healthcare_agent()
        print("✅ Agent ready for interactive queries!")
        print("\n💡 Try asking about:")
        print("   - Drug shortage trends")
        print("   - Pharmaceutical news analysis")
        print("   - ALS treatment developments")
        print("   - Supply chain risk assessment")
        print("\nType 'quit' to exit\n")
        
        while True:
            query = input("🔍 Your healthcare query: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if query:
                print(f"\n🤖 Analyzing: {query}")
                response = agent(query)
                print(f"\n📋 Analysis Result:\n{response}\n")
                print("-" * 60)
        
        print("👋 Healthcare analysis session ended.")
        
    except Exception as e:
        print(f"❌ Error in interactive mode: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_healthcare_scenarios()