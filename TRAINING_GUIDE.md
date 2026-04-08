# Training Guide — Autonomous Adaptive Insurance Planning Agent

This guide explains how to evolve the current rule-based agentic system into a data-driven, trainable AI — and which datasets to use.

---

## How the Current System Works (Phase 0)

Right now, all agents use **handcrafted rules**:

| Agent | Logic Type |
|---|---|
| User Profiling | Deterministic thresholds (age bands, income bands) |
| Risk Analysis | Weighted rule-based score (0–100) |
| Scenario Simulation | Profile-scaled probabilities and costs |
| Policy Evaluation | Utility formula + multi-factor scoring |
| Critic | Heuristic issue detection + penalty-based confidence |

This is valid for a prototype, but here's how to train each layer.

---

## Phase 1: Supervised Risk Scoring (Easiest Win)

### What to Train
Replace `RiskAnalysisAgent.calculate_risk()` with a trained ML model.

### How
1. **Dataset**: Use a labeled insurance claims dataset (see below)
2. **Features**: `age`, `income`, `dependents`, `assets`, `liabilities`, `liability_ratio`, `net_worth`
3. **Target**: Risk class (low / moderate / high) — or a continuous risk score
4. **Model**: Start with **XGBoost** or **Random Forest** (sklearn)
5. **Integration**:
   ```python
   import joblib
   
   class RiskAnalysisAgent:
       def __init__(self):
           self.model = joblib.load("models/risk_model.pkl")
       
       def calculate_risk(self, profile):
           features = [profile.age, profile.income, profile.dependents, ...]
           risk_score = self.model.predict_proba([features])[0]
           # Map to label
   ```

### Training Script Outline
```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

df = pd.read_csv("data/insurance_claims.csv")

# Feature engineering
X = df[["age", "income", "dependents", "bmi", "smoker", "region"]]
y = df["risk_label"]  # You may need to create this from claim amounts

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

print(f"Accuracy: {model.score(X_test, y_test):.2%}")
joblib.dump(model, "models/risk_model.pkl")
```

---

## Phase 2: Scenario Calibration with Real Data

### What to Train
Calibrate the `ScenarioSimulationAgent` probabilities using real-world claim frequency data.

### How
1. Use claim datasets to compute actual probabilities: `P(medical_claim | age, smoker, region)`
2. Fit a **logistic regression** or **Bayesian model** per scenario type
3. Replace the hardcoded probability functions with model predictions

### Example
```python
from sklearn.linear_model import LogisticRegression

# Train: "did this person file a medical claim?"
model = LogisticRegression()
model.fit(X_train, y_medical_claim)

# In ScenarioSimulationAgent:
med_prob = model.predict_proba([[age, income, bmi, smoker]])[0][1]
```

---

## Phase 3: Policy Ranking with Learning-to-Rank

### What to Train
Replace the utility formula in `PolicyEvaluationAgent` with a learned ranking model.

### How
1. Collect user feedback: "Did the user accept this policy?" (click-through data)
2. Use **LambdaMART** or **LightGBM ranker** to learn which policies users prefer
3. Features: `coverage_ratio`, `premium_ratio`, `suitability_match`, `risk_label`, `utility_score`

### Framework
```python
import lightgbm as lgb

train_data = lgb.Dataset(X_train, label=y_relevance, group=query_groups)
params = {"objective": "lambdarank", "metric": "ndcg"}
model = lgb.train(params, train_data, num_boost_round=100)
```

---

## Phase 4: LLM-Powered Explanations

### What to Do
Use a language model (GPT-4, Gemini, or a local LLM like Llama) to generate natural language explanations.

### How
1. Replace `_build_explanation()` in `RecommendationAgent` with an LLM call
2. Pass structured data (risk score, policy details, critic issues) as context
3. The LLM produces a human-readable explanation

### Example with OpenAI
```python
import openai

def generate_explanation(policy, risk, critic_issues):
    prompt = f"""
    You are an insurance advisor. Explain why {policy.policy_name} is recommended
    for a user with risk score {risk} and these issues: {critic_issues}.
    Keep it under 3 sentences.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

---

## Phase 5: Reinforcement Learning (Advanced)

### What to Train
Train the `CriticAgent` using RL to learn when to rerank vs accept.

### How
1. Define reward: +1 if the recommended policy is accepted by the user, -1 if rejected
2. State: top-3 policies + user profile features
3. Action: accept top policy or swap with candidate 2/3
4. Use **PPO** or **DQN** (via stable-baselines3)

This is advanced and requires user interaction data to train effectively.

---

## Recommended Datasets

### 1. Medical Cost Personal Dataset
- **Source**: [Kaggle — Insurance](https://www.kaggle.com/datasets/mirichoi0218/insurance)
- **Size**: 1,338 records
- **Features**: age, sex, bmi, children, smoker, region, charges
- **Use**: Train risk scoring model, calibrate medical scenario costs
- **Why**: Clean, small, perfect for a student project

### 2. Prudential Life Insurance Assessment
- **Source**: [Kaggle — Prudential](https://www.kaggle.com/c/prudential-life-insurance-assessment)
- **Size**: 59,381 records
- **Features**: 128 anonymized features + 8-level risk response
- **Use**: Train ordinal risk classification
- **Why**: Real insurance company data, 8 risk levels for nuanced scoring

### 3. Insurance Claim Analysis
- **Source**: [Kaggle — Insurance Claims](https://www.kaggle.com/datasets/thedevastator/insurance-claim-analysis)
- **Size**: 1,000 records
- **Features**: age, gender, bmi, blood_pressure, diabetic, smoker, claim amount
- **Use**: Predict claim probability and amount for scenario simulation
- **Why**: Directly maps to your scenario simulation agent

### 4. Health Insurance Cross-Sell Prediction
- **Source**: [Kaggle — Cross Sell](https://www.kaggle.com/datasets/anmolkumar/health-insurance-cross-sell-prediction)
- **Size**: 381,109 records
- **Features**: age, gender, driving_license, region, previously_insured, vehicle_age, premium, channel
- **Use**: Train policy recommendation likelihood model
- **Why**: Large dataset, great for learning which policies users accept

### 5. Porto Seguro Safe Driver Prediction
- **Source**: [Kaggle — Porto Seguro](https://www.kaggle.com/c/porto-seguro-safe-driver-prediction)
- **Size**: 595,212 records
- **Features**: 57 anonymized features
- **Use**: Claim probability prediction
- **Why**: Massive dataset for robust model training

### 6. IRDAI Annual Reports (India-specific)
- **Source**: [IRDAI Official](https://www.irdai.gov.in)
- **Type**: PDF reports with industry statistics
- **Use**: Calibrate scenario probabilities for the Indian insurance market
- **Why**: Real regulatory data from the Insurance Regulatory and Development Authority of India

---

## Quick Start: Train Your First Model

The easiest path to get a trained model into your project:

```bash
# 1. Download the Medical Cost dataset from Kaggle
# 2. Place it in app/data/insurance.csv
# 3. Run the training script:
python app/training/train_risk_model.py

# 4. The model will be saved to app/models/risk_model.pkl
# 5. Update RiskAnalysisAgent to load and use the model
```

---

## Summary

| Phase | Difficulty | Impact | Time Estimate |
|---|---|---|---|
| Phase 1: Supervised Risk Scoring | ⭐⭐ Easy | High | 2-3 days |
| Phase 2: Scenario Calibration | ⭐⭐ Easy | High | 2-3 days |
| Phase 3: Learning-to-Rank Policies | ⭐⭐⭐ Medium | Medium | 1 week |
| Phase 4: LLM Explanations | ⭐⭐ Easy | High | 1-2 days |
| Phase 5: RL Critic Agent | ⭐⭐⭐⭐⭐ Hard | Medium | 2-3 weeks |

**Recommended order**: Phase 1 → Phase 4 → Phase 2 → Phase 3 → Phase 5
