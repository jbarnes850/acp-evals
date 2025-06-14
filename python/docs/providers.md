# LLM Provider Configuration Guide

ACP Evals supports multiple LLM providers for evaluation. This guide covers detailed setup and configuration for each provider.

## Overview

The framework uses a provider abstraction layer that allows you to:
- Switch between providers without changing code
- Automatically detect configured providers
- Fall back to mock mode for testing
- Track costs across different providers

## Supported Providers (June 2025)

### OpenAI

**Latest Models:**
- `gpt-4.1` - Latest GPT-4.1 with improved coding and reasoning
- `gpt-4.1-nano` - Smaller, faster variant 
- `o3` - Advanced reasoning model (200K context)
- `o3-mini` - Fast reasoning (200K context)
- `o4-mini` - Cost-efficient reasoning

**Setup:**

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

2. Add to `.env`:
```bash
OPENAI_API_KEY=sk-proj-...your-key...
OPENAI_MODEL=gpt-4.1
```

3. Optional settings:
```bash
# For Azure OpenAI or custom endpoints
OPENAI_API_BASE=https://your-endpoint.openai.azure.com/

# For specific deployments
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

**Pricing (per 1K tokens):**
- `gpt-4.1`: $0.01/$0.03 (input/output)
- `o3`: $0.015/$0.075
- `o4-mini`: $0.002/$0.010

### Anthropic  

**Latest Models:**
- `claude-4-opus` - Best for complex, long-running tasks (32K output)
- `claude-4-sonnet` - Excellent coding performance (64K output)

**Setup:**

1. Get your API key from [Anthropic Console](https://console.anthropic.com/)

2. Add to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...your-key...
ANTHROPIC_MODEL=claude-4-sonnet
```

**Pricing (per 1K tokens):**
- `claude-4-opus`: $0.015/$0.075 (input/output)
- `claude-4-sonnet`: $0.003/$0.015

**Special Features:**
- Both models support extended thinking mode
- Tool use during reasoning
- Excellent instruction following

### Ollama (Local LLMs)

**Recommended Models:**
- `qwen3:235b-a22b` - Flagship model, competes with GPT-4
- `qwen3:30b-a3b` - Best balance for local inference
- `qwen3:4b` - Lightweight but powerful
- `llama3.3:70b` - Meta's latest, excellent performance
- `phi-4` - Microsoft's reasoning model

**Setup:**

1. Install Ollama:
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

2. Pull models:
```bash
ollama pull qwen3:30b-a3b
ollama pull llama3.3:70b
```

3. Add to `.env`:
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:30b-a3b
```

**Benefits:**
- No API costs
- Complete privacy
- No rate limits
- Offline capability

## Provider Selection

### Automatic Detection

The framework automatically detects available providers:

```python
# Uses EVALUATION_PROVIDER from .env
eval = AccuracyEval(agent=my_agent)

# Auto-detects first available provider
# Priority: OpenAI → Anthropic → Ollama → Mock
```

### Explicit Selection

```python
# Use specific provider
eval = AccuracyEval(
    agent=my_agent,
    judge_model="gpt-4.1"  # Forces OpenAI
)

eval = AccuracyEval(
    agent=my_agent,
    judge_model="claude-4-sonnet"  # Forces Anthropic
)
```

### Provider Configuration

```python
# With custom configuration
from acp_evals.providers import ProviderFactory

provider = ProviderFactory.create(
    "openai",
    model="o3",
    temperature=0.0,
    max_tokens=2000
)
```

## Mock Provider

For testing without API calls:

```python
# Enable mock mode
eval = AccuracyEval(
    agent=my_agent,
    mock_mode=True
)

# Or via environment
MOCK_MODE=true
```

Mock mode provides:
- Consistent test results
- No API costs
- Fast execution
- Offline testing

## Cost Management

### Tracking Costs

All evaluations track token usage and costs:

```python
result = await eval.run(input="...", expected="...")
print(f"Evaluation cost: ${result.details.get('cost', 0):.4f}")
```

### Cost Alerts

Set up cost alerts in `.env`:

```bash
ENABLE_COST_TRACKING=true
COST_ALERT_THRESHOLD=1.00  # Alert when cost exceeds $1.00
```

### Provider Comparison

| Provider | Model | Input $/1K | Output $/1K | Context | Best For |
|----------|-------|------------|-------------|---------|----------|
| OpenAI | gpt-4.1 | $0.01 | $0.03 | 128K | General evaluation |
| OpenAI | o3 | $0.015 | $0.075 | 200K | Complex reasoning |
| Anthropic | claude-4-sonnet | $0.003 | $0.015 | 200K | Code evaluation |
| Ollama | qwen3:30b | $0 | $0 | 32K | Local testing |

## Advanced Configuration

### Timeout Settings

```bash
# Evaluation timeout (seconds)
EVALUATION_TIMEOUT=30

# Batch timeout
BATCH_TIMEOUT_SECONDS=300
```

### Rate Limiting

The framework handles rate limits automatically:
- Exponential backoff
- Retry with jitter
- Provider-specific handling

### Custom Endpoints

For enterprise or custom deployments:

```python
# Custom OpenAI-compatible endpoint
OPENAI_API_BASE=https://your-endpoint.com/v1

# Ollama on different host
OLLAMA_BASE_URL=http://gpu-server:11434
```

## Troubleshooting

### Provider Not Found

```
Error: No LLM provider configured
```

**Solution:**
1. Check API keys in `.env`
2. Verify environment variables are loaded
3. Use `acp-evals check` to diagnose

### Invalid Model Error

```
Warning: Model 'gpt-5' may not be valid
```

**Solution:**
- Check model name spelling
- Ensure model is available in your region
- Update to latest model names

### Connection Errors

```
Error: Cannot connect to Ollama
```

**Solution:**
1. Ensure Ollama is running: `ollama serve`
2. Check firewall settings
3. Verify base URL configuration

### Rate Limit Errors

```
Error: Rate limit exceeded
```

**Solution:**
1. Framework auto-retries with backoff
2. Consider using multiple API keys
3. Reduce parallel batch size

## Best Practices

1. **Development**: Use Ollama or mock mode
2. **Testing**: Use smaller models (o4-mini, qwen3:4b)
3. **Production**: Use GPT-4.1 or Claude-4 for quality
4. **Cost Optimization**: 
   - Cache results when possible
   - Use appropriate model for task complexity
   - Monitor token usage regularly

## Provider Roadmap

Coming soon:
- Google Gemini support
- Cohere Command R
- Custom model endpoints
- Multi-provider evaluation (compare models)