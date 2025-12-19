#!/usr/bin/env python3
"""
Simple Strands Agent Example

A minimal example to get started with Strands SDK.
This is the "Hello World" of Strands agents!
"""

from strands import Agent
from strands_tools import calculator

# Create a simple agent with just the calculator tool
agent = Agent(
    tools=[calculator],
    system_prompt="You are a helpful assistant that can do math calculations."
)

# Test the agent
print("🤖 Simple Agent Example")
print("=" * 50)

# Ask a math question
response = agent("What is 15% of 2,450?")
print(f"\nQuestion: What is 15% of 2,450?")
print(f"Answer: {response}")

# Test conversation memory
response2 = agent("Now multiply that result by 3")
print(f"\nQuestion: Now multiply that result by 3")
print(f"Answer: {response2}")

print("\n✅ Agent working correctly!")
