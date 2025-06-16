# Troubleshooting ACP Evals

This guide helps you quickly resolve common issues when using ACP Evals.

## Common Issues & Solutions

### 1. "No LLM provider configured"
- **Symptom:** Error when running evaluations; no provider detected.
- **Likely Cause:** `.env` file missing or API keys not set.
- **Solution:**
  1. Copy `.env.example` to `.env` and add your API keys.
  2. Set `EVALUATION_PROVIDER` to a configured provider (e.g., `openai`, `anthropic`, `ollama`).
  3. Run `acp-evals check` to verify setup.

### 2. "Model not found" errors
- **Symptom:** Error about missing or invalid model name.
- **Likely Cause:** Model name in `.env` or CLI does not match available models.
- **Solution:**
  - For OpenAI: Use `gpt-4.1`, `o3`, `o4-mini`.
  - For Anthropic: Use `claude-4-opus`, `claude-4-sonnet`.
  - For Ollama: Pull the model first (e.g., `ollama pull qwen3:30b-a3b`).

### 3. Timeout errors with Ollama
- **Symptom:** Evaluation hangs or fails with timeout.
- **Likely Cause:** Model not loaded or first run is slow.
- **Solution:**
  1. Pre-load the model: `ollama run qwen3:30b-a3b`.
  2. Increase timeout in `.env` or CLI options.
  3. Use a smaller model for faster startup.

### 4. High costs with cloud providers
- **Symptom:** Unexpectedly high API usage or billing.
- **Likely Cause:** Large batch jobs or expensive models.
- **Solution:**
  1. Use `mock_mode=True` during development.
  2. Use smaller models (e.g., `o4-mini`).
  3. Monitor costs with built-in tracking.
  4. Set `COST_ALERT_THRESHOLD` in `.env`.

### 5. "Agent not responding" or health check failures
- **Symptom:** Agent URL does not respond or fails health check.
- **Likely Cause:** Agent server not running or wrong URL.
- **Solution:**
  1. Start your agent server (see examples/09_real_acp_agents.py).
  2. Verify the agent URL is correct and accessible.
  3. Use `acp-evals discover` to list available agents.

## Getting Further Help
- **Discord:** [Join our Discord](https://discord.gg/NradeA6ZNF)
- **GitHub Issues:** [Open an issue](https://github.com/jbarnes850/acp-evals/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jbarnes850/acp-evals/discussions)

For more examples and advanced troubleshooting, see the `/examples` directory and the main documentation. 