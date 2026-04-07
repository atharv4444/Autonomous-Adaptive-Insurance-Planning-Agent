# AGENTS.md

## Implemented Agents

### User Profiling Agent

- Converts validated raw inputs into a structured user profile
- Derives net worth, liability ratio, affordability band, and life stage

### Risk Analysis Agent

- Calculates a transparent rule-based risk score
- Assigns a simple risk label: `low`, `moderate`, or `high`

### Policy Evaluation Agent

- Loads policies from a local dataset
- Scores them using suitability, coverage fit, and affordability
- Produces ranked policy candidates with explanation points

### Recommendation Agent

- Orchestrates the full flow
- Returns the best policy, top 3 policies, risk score, and explanation

## Reserved Extension Points

The following are intentionally not implemented yet, but the current structure supports adding them later:

- Scenario Simulation Agent
- Critic Agent
- Memory System
- LLM orchestration
- External API connectors
- Advanced ML models
- Regulatory/compliance module
