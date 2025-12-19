# AWS Bedrock Setup for Strands Healthcare Agent

## Quick Setup Guide

### Option 1: Bedrock API Key (Recommended for Development)

1. **Get Bedrock API Key:**
   - Open [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
   - Navigate to "API keys" in the left sidebar
   - Click "Generate long-term API key"
   - Set expiration (max 30 days for development)
   - Copy and save the key securely (shown only once!)

2. **Enable Model Access:**
   - In Bedrock Console, go to "Model access" → "Manage model access"
   - Enable "Claude 4 Sonnet" or your preferred model
   - Wait a few minutes for access to propagate

3. **Set Environment Variable:**
   ```bash
   export AWS_BEDROCK_API_KEY=your_bedrock_api_key_here
   ```

4. **Test Your Setup:**
   ```bash
   source .venv/bin/activate
   python healthcare_strands_agent.py
   ```

### Option 2: AWS Credentials (Production)

1. **Configure AWS CLI:**
   ```bash
   aws configure
   ```
   Or set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-west-2
   ```

2. **Enable Model Access** (same as Option 1, step 2)

3. **Test Your Setup** (same as Option 1, step 4)

## Running Your Healthcare Agents

### Basic Agent
```bash
python healthcare_strands_agent.py
```

### Advanced Agent with Custom Tools
```bash
# Run predefined scenarios
python advanced_healthcare_agent.py

# Interactive mode
python advanced_healthcare_agent.py --interactive
```

## Troubleshooting

- **"Access denied to model"**: Enable model access in Bedrock console
- **"Invalid API key"**: Check key hasn't expired (30-day limit)
- **"Module not found"**: Ensure you're in the virtual environment
- **"No AWS credentials"**: Set AWS_BEDROCK_API_KEY or AWS credentials

## Next Steps

Once credentials are set up, you can:
1. Run the basic healthcare agent
2. Try the advanced agent with pharmaceutical data tools
3. Customize the system prompts for your specific use cases
4. Add more custom tools for your data sources