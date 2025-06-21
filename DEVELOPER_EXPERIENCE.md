# ACP-Evals: 10/10 Developer Experience

## What We Built

A professional agent testing framework that **feels simple but scales with your needs**. Built specifically for the BeeAI/ACP ecosystem.

## Core Philosophy

**"Powerful tools that feel simple"** - We achieve this by:
1. **Smart defaults** - Everything works with minimal configuration
2. **Progressive disclosure** - Complexity is there when you need it
3. **Native integration** - First-class support for ACP/BeeAI patterns
4. **Real evaluations** - No mocks, only actual LLM-powered testing

## The Developer Journey

### Day 1: First Test (30 seconds)
```python
from acp_evals import test

# That's it. Test your agent.
result = test("http://localhost:8000/agents/my-agent", "What's 2+2?", "4")
print(f"✓ Your agent works! Score: {result.score:.0%}")
```

### Day 2: Testing Rich Messages (2 minutes)
```python
from acp_sdk.models import Message, MessagePart
from acp_evals import test

# Native ACP Message support
message = Message(parts=[
    MessagePart(content="Analyze this chart", content_type="text/plain"),
    MessagePart(content=chart_image, content_type="image/png")
])

result = test(agent, message, "Identifies upward trend and key data points")
```

### Day 3: Professional Testing (5 minutes)
```python
from acp_evals import test, TestOptions

# Add control when you need it
result = test(
    agent,
    "Handle customer refund request",
    "Polite response following company policy",
    TestOptions(
        check="semantic",      # Not just exact match
        threshold=0.85,        # High quality bar
        rubric="customer_service",  # Domain-specific criteria
        track_latency=True     # Performance matters
    )
)

# Get actionable feedback
print(f"Score: {result.score:.0%}")
print(f"Latency: {result.details['latency_ms']}ms")
print(f"Feedback: {result.details['feedback']}")
```

### Day 7: Advanced Patterns (Coming Soon)
```python
from acp_evals import evaluate

# Test tool usage
result = evaluate.tool_usage(
    agent,
    "Find weather in Tokyo",
    expected_tools=["weather_api", "location_lookup"]
)

# Test multi-step reasoning
result = evaluate.reasoning(
    agent,
    "Plan a trip to Paris",
    expected_steps=["research", "budgeting", "booking"]
)

# Test conversation state
conv = evaluate.conversation(agent)
conv.add_turn("Remember my name is John")
conv.add_turn("What's my name?")  # Tests memory
result = conv.evaluate()
```

## Key Design Decisions

### 1. **Two-Parameter Minimum**
```python
test(agent, input, expected)  # Everything else is optional
```
- No configuration files required
- No setup ceremonies
- Just test your agent

### 2. **Smart Input Handling**
The `test()` function accepts:
- Plain strings: `"What's 2+2?"`
- ACP Messages: `Message(parts=[...])`
- Dict representations: `{"parts": [...]}`
- BeeAI agent instances (future)

### 3. **Progressive Complexity**
```python
# Level 1: Dead simple
test(agent, "Hi", "Hello")

# Level 2: Some control
test(agent, "Hi", "Hello", TestOptions(check="exact"))

# Level 3: Professional depth
test(agent, prompt, expected, TestOptions(
    check="reasoning",
    expected_steps=[...],
    track_tokens=True,
    judge_model="gpt-4"
))
```

### 4. **Real LLM Evaluations**
- No mock mode in production
- All evaluations use actual LLMs
- Accurate, meaningful feedback
- Cost tracking included

### 5. **BeeAI/ACP Native**
- Works with `bee agent:dev` workflow
- Understands ACP Message format
- Tool usage evaluation (coming)
- Workflow testing (coming)

## What Makes This 10/10

### ✅ **Instant Value**
- Test in 2 lines of code
- No configuration required
- Works with existing agents

### ✅ **Professional Depth**
- Semantic evaluation beyond keyword matching
- Performance metrics (latency, tokens)
- Domain-specific rubrics
- Detailed feedback

### ✅ **Developer-Friendly Output**
```
EVALUATION RESULT
├─ Score        ████████████████░░░░ 82%
├─ Status       PASS
├─ Latency      145ms
└─ Feedback     Response is accurate but could be more detailed...

Suggestions:
• Add more examples for edge cases
• Consider implementing streaming for long responses
• Response time is excellent (<200ms)
```

### ✅ **Smart Error Messages**
```
Could not connect to agent at http://localhost:8000/agents/my-agent

Troubleshooting Steps:

1. Check if your agent is running:
   • For BeeAI agents: bee agent:dev
   • For ACP agents: curl http://localhost:8000/agents

2. Verify the agent URL format:
   • ACP format: http://localhost:8000/agents/my-agent
   
3. Check agent configuration:
   • For BeeAI: Check bee.yaml
   • For ACP: Check @server.agent() decorator

4. View agent logs:
   • BeeAI: bee agent:logs
   • ACP: Check server output
```

## Implementation Status

### ✅ Completed
- Simple `test()` function with 2-parameter minimum
- Native ACP Message support
- Progressive disclosure via TestOptions
- Real LLM evaluations (no mocks)
- Professional output formatting
- Smart error messages

### 🚧 In Progress (TODOs)
- Agent discovery mechanism
- Tool usage evaluation (API implemented, needs ACP client streaming support)
- Multi-step reasoning evaluation
- Conversation state testing
- Streaming evaluation support
- BeeAI recipe library
- Comprehensive test suites

### ✅ Recently Added
- Performance evaluation with latency/memory tracking
- Tool usage evaluation API (pending ACP enhancements)
- Compatibility aliases (PerfEval, ReliabilityEval)

## Why This Architecture

1. **Simplicity First**: The basic `test()` function handles 80% of use cases
2. **Power When Needed**: TestOptions and evaluate namespace for advanced usage
3. **Ecosystem Integration**: Native support for ACP/BeeAI patterns
4. **Professional Tools**: Real evaluations with meaningful metrics
5. **Developer Empathy**: Clear errors, actionable feedback, minimal friction

## Next Steps

1. **Complete TODO features** marked as NotImplementedError
2. **Add agent discovery** to reduce configuration
3. **Create recipe library** for common agent types
4. **Build streaming support** for real-time evaluation
5. **Enhance error messages** with more context

The goal: Make agent testing so easy that developers actually enjoy it.