---
title: Healthcare OpenEnv
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
app_file: inference.py
pinned: false
---

# Healthcare Assistant RL Environment 🩺

This is an **OpenEnv-compliant Reinforcement Learning environment** designed to simulate a clinical decision assistant. The agent's goal is to accurately diagnose a patient based on their symptoms, medical history, and medications by ordering medical tests. The objective is to maximize diagnostic accuracy while minimizing the number of tests requested (cost) and the time taken.

## Observation Space

The environment returns an Observation object containing:
- symptoms (List[str])
- medical_history (List[str])
- current_medication (List[str])
- tests_done (List[str])
- test_results (Dict[str, str])
- step_count (int)

## Action Space

The agent can perform two types of actions:
1. recommend_test(test_name)
2. diagnose(disease_name)

Action format:
```json
{
  "action_type": "test" | "diagnose",
  "value": "<test_name or disease_name>"
}
```

## Reward Settings

- *The reward function is designed such that the maximum achievable reward corresponds to correct diagnosis with minimal tests and steps.*
- **+10** → correct diagnosis
- **-10** → wrong diagnosis
- **-2** → each test
- **-1** → each step
- **+2** → useful test (yields abnormal specific result)
- **-5** → repeated test
- Implicit **+2/+1** bonuses for correct diagnosis in harder ambiguous cases for utilizing context.
- Explicit penalties (-3, -5) for invalid actions or diagnoses.

## Tasks

The environment defines three tasks:
- Easy: Clear symptoms, minimal ambiguity.
- Medium: Overlapping symptoms requiring 1–2 tests.
- Hard: Ambiguous cases with medical history and medication influence.

## Baseline Results

Example performance using the baseline model (`gpt-4.1-mini` via native inference format):
- Easy: 0.9
- Medium: 0.7
- Hard: 0.5

## Setup and Run

1. `pip install -r requirements.txt`
2. Run validation sweeps:
```bash
python validate_env.py
openenv validate
```
3. Set environment variables:
```bash
export HF_TOKEN="your_token"
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="gpt-4.1-mini"
```
*(Windows → use set instead of export)*
4. Run inference locally: `python inference.py`

## Docker & HF Space Compatibility

This environment natively supports Hugging Face spaces:
```bash
docker build -t health-env .
docker run -e HF_TOKEN="your_token" health-env
```
