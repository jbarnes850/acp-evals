# ACP Evals CLI Enhancement TODO List

## Priority 1 - Today (for PyPI release)

### 1. Implement `test` command ⬜
- [ ] Create `cli/commands/test.py`
- [ ] Add quick test suite (3-5 tests)
- [ ] Add comprehensive test suite 
- [ ] Add adversarial test suite
- [ ] Implement export functionality
- [ ] Add progress bars and rich output
- [ ] Write tests for command

### 2. Implement `run` command ⬜
- [ ] Create `cli/commands/run.py`
- [ ] Support all evaluator types (accuracy, performance, safety, reliability)
- [ ] Add multi-agent handoff support
- [ ] Implement direct CLI evaluation
- [ ] Add result formatting
- [ ] Write tests for command

### 3. Implement `discover` command ⬜
- [ ] Create `cli/commands/discover.py`
- [ ] Integrate with ACPEvaluationClient
- [ ] List available agents from ACP server
- [ ] Add --test-all functionality
- [ ] Format output as table
- [ ] Write tests for command

### 4. Enhanced Templates ⬜
- [ ] Add `acp-agent` template showing real ACP integration
- [ ] Add `multi-agent` template for coordination patterns
- [ ] Update existing templates with better examples
- [ ] Add inline documentation

### 5. Update Help Text ⬜
- [ ] Update main CLI description
- [ ] Add usage examples to each command
- [ ] Improve command descriptions
- [ ] Add "Getting Started" section

### 6. Integration & Testing ⬜
- [ ] Update `cli/main.py` to register new commands
- [ ] Run all commands to verify functionality
- [ ] Update documentation
- [ ] Add CLI tests

## Priority 2 - Next Release (Week 1)

### 7. Implement `dataset` commands ✅
- [x] Create `cli/commands/dataset.py`
- [x] Implement list subcommand
- [x] Implement load subcommand
- [x] Implement create-suite subcommand
- [x] Implement analyze subcommand

### 8. Implement `traces` commands ✅
- [x] Create `cli/commands/traces.py`
- [x] Implement ingest subcommand
- [x] Implement recycle subcommand
- [x] Implement patterns subcommand
- [x] Implement regression subcommand

### 9. Implement `generate` command ✅
- [x] Create `cli/commands/generate.py`
- [x] Implement test generation
- [x] Implement adversarial generation
- [x] Implement scenarios generation (multi-turn conversations)

### 10. Implement `workflow` command ✅
- [x] Create `cli/commands/workflow.py`
- [x] Implement test subcommand
- [x] Implement compare subcommand
- [x] Implement handoff subcommand

## Priority 3 - Future Releases

### 11. Implement `monitor` command ⬜
- [ ] Create `cli/commands/monitor.py`
- [ ] Implement continuous monitoring
- [ ] Add status viewing
- [ ] Add alert configuration

### 12. Implement `benchmark` command ⬜
- [ ] Create `cli/commands/benchmark.py`
- [ ] Implement suite running
- [ ] Add agent comparison
- [ ] Add pattern benchmarking

### 13. Implement `ci` command ⬜
- [ ] Create `cli/commands/ci.py`
- [ ] Add CI/CD integration
- [ ] Add GitHub Actions support
- [ ] Add regression detection

### 14. Implement `analyze` command ⬜
- [ ] Create `cli/commands/analyze.py`
- [ ] Add cost analysis
- [ ] Add performance analysis
- [ ] Add token efficiency analysis

## Code Quality & Documentation

### Testing ⬜
- [ ] Write unit tests for each command
- [ ] Add integration tests
- [ ] Test with real ACP agents
- [ ] Verify all examples work

### Documentation ⬜
- [ ] Update README with new commands
- [ ] Create CLI usage guide
- [ ] Add command examples
- [ ] Update API documentation

### Code Quality ⬜
- [ ] Run ruff linter
- [ ] Run pyright type checker
- [ ] Ensure consistent error handling
- [ ] Add proper logging

## Notes

- Each command should follow the established patterns in `check.py`
- Use Rich for beautiful console output
- Support both sync and async operations
- Provide clear, actionable error messages
- Include progress indicators for long operations