# LLM Provider Guide

ACP Evals provides a unified interface for multiple LLM providers with automatic detection and simple configuration.

## Overview

The provider system offers:
- **Auto-detection**: Automatically detects configured providers based on environment variables
- **Unified interface**: Same API across all providers
- **Built-in cost tracking**: Automatic token usage and cost calculation
- **Zero configuration**: Works out of the box once API keys are set

## Supported Providers

### OpenAI

**Supported Models:**
- `gpt-4.1` - Latest model (default)
- `gpt-4.1-nano` - Cost-efficient variant
- `o3` - Advanced reasoning model
- `o3-mini` - Smaller reasoning model
- `o4-mini` - Fastest model

**Setup:**
```bash
# Add to .env file
OPENAI_API_KEY=sk-proj-...your-key...
```

**Optional Configuration:**
```bash
OPENAI_MODEL=gpt-4.1          # Default model
OPENAI_API_BASE=...           # Custom endpoint
```

**Pricing (per 1K tokens):**
- `gpt-4.1`: $0.01 input / $0.03 output
- `gpt-4.1-nano`: $0.005 input / $0.015 output
- `o3`: $0.015 input / $0.075 output
- `o3-mini`: $0.003 input / $0.015 output
- `o4-mini`: $0.002 input / $0.010 output

### Anthropic

**Supported Models:**
- `claude-3-opus-20240229` - Most capable model for complex reasoning (default)
- `claude-3-sonnet-20240229` - Balanced intelligence and speed
- `claude-3-haiku-20240307` - Fastest model for quick responses

**Setup:**
```bash
# Add to .env file
ANTHROPIC_API_KEY=sk-ant-api03-...your-key...
```

**Optional Configuration:**
```bash
ANTHROPIC_MODEL=claude-3-opus-20240229    # Default model
```

**Pricing (per 1K tokens):**
- `claude-3-opus-20240229`: $0.015 input / $0.075 output
- `claude-3-sonnet-20240229`: $0.003 input / $0.015 output
- `claude-3-haiku-20240307`: $0.0008 input / $0.004 output

### Ollama (Local)

**Recommended Models:**
- `qwen3:8b` - Good balance for local inference (default)
- `qwen3:4b` - Faster inference option
- `devstral:latest` - Development-focused model
- `gemma3:12b` - Google's model

**Setup:**
```bash
# Install Ollama
brew install ollama               # macOS
curl -fsSL https://ollama.ai/install.sh | sh  # Linux

# Pull models
ollama pull qwen3:8b

# Start server
ollama serve
```

**Optional Configuration:**
```bash
OLLAMA_BASE_URL=http://localhost:11434    # Default URL
OLLAMA_MODEL=qwen3:8b                    # Default model
```

**Benefits:**
- No API costs
- Complete privacy
- No rate limits
- Offline capability

## Usage

### Automatic Provider Selection

The framework automatically detects and uses the first available provider:

```python
from acp_evals import AccuracyEval

# Uses auto-detected provider (OpenAI → Anthropic → Ollama)
eval = AccuracyEval(agent=my_agent)
result = await eval.run(input="What is 2+2?", expected="4")
```

### Explicit Provider Selection

```python
# Force specific provider via judge_model
eval = AccuracyEval(
    agent=my_agent,
    judge_model="claude-4-sonnet"  # Uses Anthropic
)

eval = AccuracyEval(
    agent=my_agent, 
    judge_model="gpt-4.1"          # Uses OpenAI
)
```

### Direct Provider Usage

```python
from acp_evals.providers import ProviderFactory

# Create provider directly
provider = ProviderFactory.create("openai", model="gpt-4.1")
response = await provider.complete("Hello world")

print(f"Response: {response.content}")
print(f"Cost: ${response.cost:.4f}")
print(f"Tokens: {response.usage}")
```

### Environment-Based Configuration

```bash
# Set default provider
EVALUATION_PROVIDER=anthropic

# Set evaluation parameters
EVALUATION_TEMPERATURE=0.0
EVALUATION_MAX_TOKENS=1000
EVALUATION_TIMEOUT=30
```

## Provider Detection

Check which providers are configured:

```python
from acp_evals.providers import ProviderFactory

# Check available providers
available = ProviderFactory.detect_available_providers()
print(available)
# {'openai': True, 'anthropic': False, 'ollama': True}

# Get default provider
default = ProviderFactory.get_default_provider()
print(default)  # 'openai'
```

## Error Handling

The framework provides helpful error messages:

```python
from acp_evals.core.exceptions import ProviderNotConfiguredError

try:
    provider = ProviderFactory.create("openai")
except ProviderNotConfiguredError as e:
    print(e)  # Shows setup instructions
```

## Cost Tracking

All providers automatically track token usage and costs:

```python
eval = AccuracyEval(agent=my_agent, judge_model="gpt-4.1")
result = await eval.run(input="Test", expected="Answer")

# Access cost information
if hasattr(result, 'metadata') and result.metadata:
    cost = result.metadata.get('cost', 0)
    print(f"Evaluation cost: ${cost:.4f}")
```

## Implementation Details

### Base Provider Interface

All providers implement the same interface:

```python
from acp_evals.providers.base import LLMProvider, LLMResponse

class MyProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "my_provider"
    
    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        # Implementation
        return LLMResponse(
            content="response",
            model=self.model,
            usage={"total_tokens": 100},
            cost=0.001
        )
    
    @classmethod
    def get_required_env_vars(cls) -> list[str]:
        return ["MY_API_KEY"]
```

### Provider Factory

The factory handles provider creation and auto-detection:

```python
from acp_evals.providers import ProviderFactory

# Registry of available providers
ProviderFactory.PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider, 
    "ollama": OllamaProvider,
}

# Auto-detection priority
priority = ["openai", "anthropic", "ollama"]
```

### Configuration Loading

Configuration is loaded from environment variables:

```python
from acp_evals.core.config import get_provider_config

config = get_provider_config()
# Returns provider settings from environment
```

## Troubleshooting

### Common Issues

1. **Provider not found**: Check API key environment variables
2. **Connection errors**: Verify API endpoints and network connectivity
3. **Rate limits**: Framework handles retries automatically
4. **Ollama connection**: Ensure `ollama serve` is running

### Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Shows detailed provider communication
eval = AccuracyEval(agent=my_agent)
```

### Health Checks

```python
# Check provider connectivity
provider = ProviderFactory.create("ollama")
if hasattr(provider, 'check_connection'):
    connected = await provider.check_connection()
    print(f"Ollama connected: {connected}")
```

## Best Practices

1. **Use environment variables** for API keys instead of hardcoding
2. **Set EVALUATION_PROVIDER** to avoid auto-detection overhead
3. **Monitor costs** with built-in tracking
4. **Use Ollama for development** to avoid API costs
5. **Handle provider errors** gracefully in production

## Migration Notes

- **Mock mode removed**: No longer supported, use real providers or local Ollama
- **Simplified interface**: Provider creation is now automatic
- **Environment-first**: Configuration primarily through environment variables
- **Built-in validation**: Providers validate configuration on initialization