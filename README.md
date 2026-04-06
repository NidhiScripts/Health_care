---
title: Healthcare OpenEnv
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
app_file: inference.py
pinned: false
---

# 🩺 Healthcare Assistant RL Environment

## 🚨 Problem Statement

In real-world clinical settings, doctors often rely on multiple diagnostic tests, which can:
- Increase patient cost 💰
- Delay diagnosis ⏳
- Lead to redundant testing 🔁

There is a need for an intelligent system that can **recommend the optimal sequence of medical tests** while ensuring high diagnostic accuracy.

---

## 💡 Solution

We designed an **OpenEnv-compliant Reinforcement Learning environment** that simulates clinical decision-making.

The agent:
- Observes patient data (symptoms, history, medications)
- Selects diagnostic tests step-by-step
- Decides when to stop and diagnose

🎯 Goal:
> Maximize diagnostic accuracy while minimizing cost and time.

💡 **Impact:** This system can reduce unnecessary diagnostic tests, lower healthcare costs, and improve decision efficiency in real-world clinical workflows.

---

## 🧠 Why Reinforcement Learning?

Healthcare diagnosis is a **sequential decision problem**:

```text
Symptoms → Test → Result → Next Test → Diagnosis
```

RL is ideal because:
- Each action affects future decisions
- There is a trade-off between exploration (tests) and efficiency
- Rewards guide optimal strategies

### 📦 Observation Space

Observation:
- `symptoms`: List[str]
- `medical_history`: List[str]
- `current_medication`: List[str]
- `tests_done`: List[str]
- `test_results`: Dict[str, str]
- `step_count`: int

### ⚙️ Action Space

```json
{
  "action_type": "test" | "diagnose",
  "value": "<test_name or disease_name>"
}
```

Actions:
- `test` → Request a diagnostic test
- `diagnose` → Predict final disease

### 🎯 Reward Function

Designed to balance accuracy vs efficiency:

| Action | Reward |
|--------|--------|
| Correct diagnosis | +10 |
| Wrong diagnosis | -10 |
| Each test | -2 |
| Each step | -1 |
| Useful test | +2 |
| Repeated test | -5 |

👉 Encourages:
- Fewer tests
- Faster decisions
- Correct diagnosis

### 🧪 Tasks & Difficulty Levels

| Task | Description |
|------|-------------|
| Easy | Clear symptoms, direct diagnosis |
| Medium | Overlapping symptoms |
| Hard | Ambiguous + medical history influence |

### 🧮 Grading System

Each episode is scored between **0.0 – 1.0**:

| Score | Meaning |
|-------|---------|
| 1.0 | Optimal (≤2 tests + correct diagnosis) |
| 0.7 | Correct but more tests |
| 0.5 | Late diagnosis |
| 0.0 | Incorrect / timeout |

### 📊 Baseline Results

Using `gpt-4.1-mini`:

| Task | Score |
|------|-------|
| Easy | 1.0 |
| Medium | 0.7 |
| Hard | 0.5–0.7 |

### ▶️ Example Execution

```text
[START] task=medium
[STEP] step=1 → Blood test
[STEP] step=2 → ECG
[STEP] step=3 → Chest X-ray
[STEP] step=4 → Diagnose: Asthma
[END] score=0.7
```

### 🔄 How It Works

1. The agent observes the patient state (symptoms, history, medications)  
2. It selects a diagnostic test  
3. The environment returns test results  
4. The agent iteratively refines its decision  
5. It outputs a final diagnosis  

### 🏗️ System Architecture

```text
LLM (decision making)
        ↓
Rule-based validation (safety)
        ↓
OpenEnv Environment (simulation)
        ↓
Reward + Grader
```

---

## ⚙️ Setup Instructions

```bash
pip install -r requirements.txt
python validate_env.py
openenv validate
```

### 🔑 2️⃣ Environment Variables (MANDATORY ⚠️)

Make sure these variables are clearly set before execution. **Judges WILL test this:**

```bash
export HF_TOKEN="your_token"
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="gpt-4.1-mini"
```

### 🚀 Run Inference

```bash
python inference.py
```

### 🐳 Docker Support

```bash
docker build -t health-env .
docker run -e HF_TOKEN="your_token" health-env
```

### 🌍 Deployment

Deployed on Hugging Face Spaces as a containerized application.

---

## 🧠 Key Features

- OpenEnv compliant environment
- Hybrid decision system combining LLM reasoning with rule-based validation
- Sequential decision-making using RL
- Explainable step-by-step diagnosis
- Cost-aware testing strategy
- Fully containerized + reproducible

## 🚀 Future Work

- Integration with real medical datasets
- Multi-disease diagnosis expansion
- Mobile/web clinical assistant interface
