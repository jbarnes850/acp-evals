# Troubleshooting ACP Evals

This guide helps you quickly resolve common issues when using the simplified ACP Evals framework.

## Common Issues & Solutions

### 1. Provider Configuration Issues

#### "No LLM provider configured"
- **Symptom:** Error when running evaluations; no provider detected.
- **Likely Cause:** `.env` file missing or API keys not set.
- **Solution:**
  1. Copy `.env.example` to `.env` and add your API keys.
  2. Set `EVALUATION_PROVIDER` to a configured provider (e.g., `openai`, `anthropic`, `ollama`).
  3. Verify configuration with `python -c "from acp_evals import test_provider_config; test_provider_config()"`

#### "Model not found" errors
- **Symptom:** Error about missing or invalid model name.
- **Likely Cause:** Model name does not match available models for your provider.
- **Solution:**
  - For OpenAI: Use `gpt-4.1`, `o3`, `o4-mini`
  - For Anthropic: Use `claude-4-opus`, `claude-4-sonnet`
  - For Ollama: Pull the model first: `ollama pull qwen3:30b-a3b`

#### API Key Authentication Errors
- **Symptom:** 401/403 errors or "Invalid API key" messages.
- **Likely Cause:** Incorrect or expired API keys.
- **Solution:**
  1. Verify API keys in your provider dashboard
  2. Check `.env` file for correct key format
  3. Ensure no extra spaces or quotes around keys

### 2. Agent Connectivity Issues

#### "Agent not responding" or connection failures
- **Symptom:** Agent URL does not respond or connection timeouts.
- **Likely Cause:** Agent server not running or incorrect URL configuration.
- **Solution:**
  1. Start your agent server first
  2. Verify the agent URL is correct and accessible: `curl http://your-agent-url/health`
  3. Check firewall settings and network connectivity
  4. Ensure agent implements required ACP protocol endpoints

#### Agent Health Check Failures
- **Symptom:** Agent fails health checks during evaluation setup.
- **Likely Cause:** Agent not implementing proper health endpoint or returning incorrect format.
- **Solution:**
  1. Verify agent has `/health` endpoint returning 200 status
  2. Check agent logs for startup errors
  3. Test agent manually before running evaluations

### 3. Import and Module Errors

#### "ModuleNotFoundError: No module named 'acp_evals'"
- **Symptom:** Python cannot find the acp_evals module.
- **Likely Cause:** Package not installed or virtual environment issues.
- **Solution:**
  1. Install the package: `pip install -e .`
  2. Activate correct virtual environment
  3. Verify installation: `python -c "import acp_evals; print('OK')"`

#### Import errors for specific evaluators
- **Symptom:** Cannot import specific evaluator classes or functions.
- **Likely Cause:** Using old import paths from complex framework.
- **Solution:**
  1. Use simplified import: `from acp_evals import run_evaluation`
  2. Check available evaluators: `from acp_evals import list_evaluators; list_evaluators()`
  3. Update code to use new simplified API

### 4. CLI Command Issues

#### "Command not found: acp-evals"
- **Symptom:** CLI command not recognized by shell.
- **Likely Cause:** Package not installed or not in PATH.
- **Solution:**
  1. Install package with CLI: `pip install -e .`
  2. Verify installation: `which acp-evals`
  3. If still not found, use: `python -m acp_evals` instead

#### Invalid CLI arguments or options
- **Symptom:** CLI reports unknown arguments or invalid options.
- **Likely Cause:** Using old CLI syntax from complex framework.
- **Solution:**
  1. Check available commands: `acp-evals --help`
  2. Use simplified syntax: `acp-evals run --agent-url <url> --evaluator <name>`
  3. Remove deprecated options like `--mock-mode` or `--pipeline-config`

### 5. Runtime and Performance Issues

#### Timeout errors with Ollama
- **Symptom:** Evaluation hangs or fails with timeout.
- **Likely Cause:** Model not loaded or first run is slow.
- **Solution:**
  1. Pre-load the model: `ollama run qwen3:8b`
  2. Increase timeout in evaluation config
  3. Use a smaller model for faster startup

#### High costs with cloud providers
- **Symptom:** Unexpectedly high API usage or billing.
- **Likely Cause:** Large evaluations or expensive models without cost controls.
- **Solution:**
  1. Use smaller models during development (e.g., `gpt-4o-mini`)
  2. Monitor token usage in evaluation results
  3. Set reasonable limits on evaluation batch sizes
  4. Test with single evaluations before running large batches

#### Memory or resource issues
- **Symptom:** Out of memory errors or slow performance.
- **Likely Cause:** Large evaluation batches or resource-intensive models.
- **Solution:**
  1. Reduce batch size in evaluation configuration
  2. Use streaming evaluation mode if available
  3. Monitor system resources during evaluation

## Quick Debugging Commands

Test your setup with these commands:

```bash
# Test provider configuration
python -c "from acp_evals import test_provider_config; test_provider_config()"

# Test module imports
python -c "import acp_evals; print('ACP Evals imported successfully')"

# List available evaluators
python -c "from acp_evals import list_evaluators; print(list_evaluators())"

# Test CLI availability
acp-evals --version

# Test agent connectivity (replace with your agent URL)
curl -s http://localhost:8000/health || echo "Agent not responding"
```

## Common Configuration Patterns

### Minimal .env file
```
OPENAI_API_KEY=your_key_here
EVALUATION_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
```

### Basic evaluation script
```python
from acp_evals import run_evaluation

result = run_evaluation(
    agent_url="http://localhost:8000",
    evaluator="basic_qa",
    config={"model": "gpt-4o"}
)
print(f"Score: {result.score}")
```

For additional help, check the examples directory or file an issue on the GitHub repository.