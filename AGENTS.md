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
- Scores them using suitability, coverage fit, affordability, and utility-based reasoning
- Produces ranked policy candidates with tradeoff summaries and explanation points

### Scenario Simulation Agent

- Simulates medical emergency, accident, and income loss scenarios
- Computes expected loss used in policy utility calculations

### Critic Agent

- Reviews the top-ranked policies
- Flags issues such as underinsurance, high premium pressure, and risk mismatch
- Can rerank the final recommendation if a stronger candidate exists

### Memory Store

- Saves user profiles and past recommendations to a local JSON file
- Supports lightweight recall for demo continuity and explainability

- Executes a structured plan: Profiling -> Risk Analysis -> Simulation -> Evaluation -> Critique -> Memory -> Adaptive Learning

### Adaptive Learner Agent

- Monitors the decision pipeline for 'mistakes' (e.g., Critic reranks)
- Performs real-time gradient descent updates on the Neural Network weights
- Closes the loop between advisor execution and environment feedback

### Recommendation Agent

- Acting as the high-level entry point and API interface
- Delegates all orchestration logic to the Goal Planner Agent
- Returns the best policy, final recommendation, expected loss, critic output, and explanation

## Reserved Extension Points

The following are intentionally not implemented yet, but the current structure supports adding them later:

- LLM orchestration
- External API connectors
- Advanced ML models
- Regulatory/compliance module
- Personalized memory retrieval
