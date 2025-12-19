#!/usr/bin/env python3
"""
Strands SDK Demo - Offline Mode

This demonstrates the Strands SDK structure and your custom pharmaceutical tools
without requiring AWS credentials. Shows how the agent would work once configured.
"""

from pharma_data_tool import search_pharma_news, get_drug_shortage_info, analyze_pharma_trends

def demo_pharmaceutical_tools():
    """Demonstrate the custom pharmaceutical data tools."""
    
    print("🏥 Strands Healthcare Agent Demo")
    print("=" * 50)
    print("This demo shows your custom pharmaceutical data tools")
    print("that would be integrated with Strands AI agents.\n")
    
    # Demo 1: Search pharmaceutical news
    print("📰 DEMO 1: Pharmaceutical News Search")
    print("-" * 40)
    print("Tool: search_pharma_news('regulatory', 3)")
    result = search_pharma_news('regulatory', 3)
    print(result)
    
    # Demo 2: Drug shortage analysis
    print("\n💊 DEMO 2: Drug Shortage Information")
    print("-" * 40)
    print("Tool: get_drug_shortage_info('fentanyl')")
    result = get_drug_shortage_info('fentanyl')
    print(result)
    
    # Demo 3: Trend analysis
    print("\n📊 DEMO 3: Pharmaceutical Trends Analysis")
    print("-" * 40)
    print("Tool: analyze_pharma_trends('recent')")
    result = analyze_pharma_trends('recent')
    print(result)
    
    print("\n" + "=" * 50)
    print("🤖 How This Works with Strands Agents:")
    print("=" * 50)
    print("""
When you set up AWS Bedrock credentials, the Strands agent will:

1. 🧠 Receive your healthcare questions in natural language
2. 🔍 Automatically choose the right tools to gather information
3. 🔄 Call multiple tools and cross-reference data
4. 📋 Analyze patterns and provide intelligent insights
5. 💬 Respond in natural language with actionable recommendations

Example conversation flow:
┌─────────────────────────────────────────────────────────────┐
│ You: "What are the current drug shortage trends affecting   │
│       neurology treatments?"                                │
├─────────────────────────────────────────────────────────────┤
│ Agent: *calls analyze_pharma_trends()*                     │
│        *calls search_pharma_news('neurology')*             │
│        *calls get_drug_shortage_info()*                    │
│                                                             │
│        "Based on the data analysis, I found 317 current    │
│         drug shortages with significant impacts on..."      │
└─────────────────────────────────────────────────────────────┘

Your pharmaceutical data tools are ready to work with Strands!
Set up AWS Bedrock credentials to activate the AI agent.
""")

def show_agent_structure():
    """Show how the Strands agent would be structured."""
    
    print("\n🔧 STRANDS AGENT STRUCTURE")
    print("=" * 50)
    print("""
from strands import Agent
from strands_tools import calculator, python_repl, http_request
from pharma_data_tool import search_pharma_news, get_drug_shortage_info, analyze_pharma_trends

# Create healthcare agent with custom tools
agent = Agent(
    tools=[
        # Your custom pharmaceutical data tools
        search_pharma_news,      # Search news data
        get_drug_shortage_info,  # Access shortage data  
        analyze_pharma_trends,   # Trend analysis
        
        # Community tools for general analysis
        calculator,              # Mathematical calculations
        python_repl,            # Execute Python code
        http_request            # Web requests
    ],
    system_prompt=\"\"\"
    You are a healthcare intelligence assistant specializing in:
    - Pharmaceutical news analysis and regulatory decisions
    - Drug shortage tracking and supply chain insights  
    - ALS/neurology treatment developments
    - Cross-referencing news events with supply impacts
    \"\"\"
)

# Use the agent
response = agent("What are the latest ALS treatment developments?")
print(response)
""")

if __name__ == "__main__":
    demo_pharmaceutical_tools()
    show_agent_structure()
    
    print("\n🚀 NEXT STEPS:")
    print("1. Set up AWS Bedrock credentials (see setup_aws_credentials.md)")
    print("2. Run: python healthcare_strands_agent.py")
    print("3. Try: python advanced_healthcare_agent.py --interactive")
    print("\nYour Strands healthcare agent is ready to go! 🎉")