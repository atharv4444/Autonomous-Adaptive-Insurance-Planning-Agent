# Autonomous Adaptive Insurance Planning Agent

A lightweight final-year project prototype that collects user financial inputs, computes a transparent risk score, compares insurance policies from a local dataset, and returns a personalized recommendation with explainability.

## Features

- Modular agent-based design
- FastAPI endpoint for recommendation requests
- CLI demo for quick presentation
- Transparent risk scoring and policy ranking
- Small local JSON policy dataset
- Basic tests for the core recommendation flow
- Clear extension points for future multi-agent and LLM upgrades

## Project Structure

```text
insurance-agent/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── agents/
│   │   ├── user_profiling.py
│   │   ├── risk_analysis.py
│   │   ├── policy_evaluation.py
│   │   └── recommendation.py
│   ├── data/
│   │   └── policies.json
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
  "risk_score": 66.67,
  "risk_label": "moderate",
  "best_policy": {
    "policy": {
      "policy_name": "SecureLife Shield"
    }
  },
  "top_policies": [
    {},
    {},
    {}
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
4. Policies are loaded from `app/data/policies.json`.
5. The Policy Evaluation Agent scores policies using:
   - suitability to goal, life stage, and risk level
   - coverage fit
   - premium affordability
6. The Recommendation Agent returns:
   - best policy
   - top 3 ranked policies
   - risk score and risk label
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

- Scenario Simulation Agent
- Critic Agent
- Memory system
- LLM-based explanation generator
- Advanced risk models
- Multi-agent orchestration

## Notes

- This is a student MVP, not a production insurance advisory system.
- The policies are dummy examples for academic demonstration only.
