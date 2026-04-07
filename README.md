# Autonomous Adaptive Insurance Planning Agent

A lightweight final-year project prototype that collects user financial inputs, computes a transparent risk score, simulates common financial risk scenarios, critiques candidate policies, stores basic recommendation memory, and returns a personalized recommendation with explainability.

## Features

- Multi-agent decision architecture
- FastAPI endpoint for recommendation requests
- CLI demo for quick presentation
- Transparent risk scoring and utility-based policy ranking
- Scenario simulation with expected-loss reasoning
- Critic validation layer for policy issues and confidence scoring
- File-backed memory for previous recommendations
- Small local JSON policy dataset
- Basic tests for the core recommendation flow
- Clear extension points for future multi-agent and LLM upgrades

## Versioning & Prototypes

This project uses a branched versioning strategy to preserve the evolution of the autonomous agent:

- **`main`**: The latest, most stable, and feature-complete version (currently Prototype 2).
- **`prototype-1`**: The initial baseline implementation of the agentic structure.
- **`prototype-2`**: Implementation of the multi-agent recommendation engine, including the Critic layer and Scenario Simulation.

To switch between versions, use `git checkout <branch-name>`.

## Project Structure

```text
insurance-agent/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── agents/
│   │   ├── user_profiling.py
│   │   ├── risk_analysis.py
│   │   ├── scenario_simulation.py
│   │   ├── policy_evaluation.py
│   │   ├── critic.py
│   │   └── recommendation.py
│   ├── data/
│   │   └── policies.json
│   ├── memory/
│   │   └── memory_store.py
│   ├── utils/
│   │   └── helpers.py
│   └── tests/
│       └── test_core.py
├── README.md
├── requirements.txt
└── AGENTS.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The API

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI.

### API Example

`POST /recommend`

Sample request:

```json
{
  "age": 35,
  "income": 900000,
  "dependents": 2,
  "assets": 2000000,
  "liabilities": 1500000,
  "insurance_goal": "family_protection"
}
```

Sample response shape:

```json
{
  "risk_score": 87.0,
  "risk_label": "high",
  "expected_loss": 16000.0,
  "best_policy": {
    "policy": {
      "policy_name": "SecureLife Shield"
    }
  },
  "final_recommendation": {
    "policy": {
      "policy_name": "SecureLife Shield"
    }
  },
  "top_policies": [
    {},
    {},
    {}
  ],
  "critic_issues": [
    "No major issues detected by the critic."
  ],
  "explanation": "SecureLife Shield is recommended because ..."
}
```

## Run The CLI Demo

```bash
python3 -m app.main --age 35 --income 900000 --dependents 2 --assets 2000000 --liabilities 1500000 --insurance-goal family_protection
```

This prints a JSON recommendation payload directly in the terminal.

## Run Tests

```bash
pytest app/tests -q
```

## Recommendation Flow

1. User input is validated with sensible defaults.
2. The User Profiling Agent builds a normalized profile.
3. The Risk Analysis Agent computes a transparent risk score.
4. The Scenario Simulation Agent estimates expected loss from common real-world events.
5. Policies are loaded from `app/data/policies.json`.
6. The Policy Evaluation Agent scores policies using:
   - suitability to goal, life stage, and risk level
   - coverage fit
   - premium affordability
   - utility-based reasoning with expected loss
7. The Critic Agent validates the top candidates, flags issues, and can rerank the final choice.
8. The Memory Store saves the profile and past recommendations in `app/data/memory_store.json`.
9. The Recommendation Agent returns:
   - best policy
   - final validated recommendation
   - top 3 ranked policies
   - risk score and risk label
   - expected loss and scenario breakdown
   - critic issues and confidence score
   - explanation text for demo/viva use

## Risk Score Formula

The prototype uses a simple rule-based score on a 0-100 scale:

- Age contributes a small insurance-need signal
- Dependents increase protection need
- Liabilities relative to income increase risk
- Lower income increases affordability pressure
- Lower or negative net worth increases vulnerability

This design is intentional for explainability and can later be replaced with a learned model.

## Future Extensions

The code is structured so the following can be added later without major refactoring:

- LLM-based explanation generator
- Personalized scenario simulation
- Real policy and risk APIs
- Advanced ML risk and utility models
- Regulatory/compliance checks
- Deeper multi-agent orchestration

## Notes

- This is a student MVP, not a production insurance advisory system.
- The policies are dummy examples for academic demonstration only.
