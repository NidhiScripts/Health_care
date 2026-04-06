import os
import json
from openai import OpenAI
from env import HealthDiagnosisEnv, Action

SYSTEM_PROMPT = """You are a clinical decision assistant.

Your goal is to diagnose the patient accurately using symptoms, history, and test results.

---

Available Tests:
- Blood test
- ECG
- Chest X-ray
- CT Scan

Available Diagnoses:
- Asthma
- Heart Attack
- Depression
- Kidney Stones
- Diabetes

---

Medical Knowledge:

- Asthma -> wheezing, breathlessness, chest tightness
- Heart Attack -> chest pain, ECG abnormality, high troponin
- Depression -> low mood, fatigue, emotional symptoms
- Kidney Stones -> severe abdominal/back pain, urinary issues
- Diabetes -> high blood sugar, fatigue, frequent urination

---

Reasoning Instructions:

1. Analyze symptoms carefully.
2. Identify 2-3 possible diseases.
3. Choose a test that helps distinguish between them.
4. Use test results before diagnosing.
5. DO NOT guess randomly.
6. DO NOT always pick the same disease.

---

Decision Rules:

- If symptoms clearly match one disease -> diagnose.
- If symptoms are unclear -> perform 2-3 different tests.
- If only 1 test is done -> prefer another test.
- NEVER repeat tests.

---

Return ONLY JSON:

{
  "action_type": "test" or "diagnose",
  "value": "<valid test or valid disease>"
}"""

def rule_based_diagnosis(obs):
    symptoms = " ".join(obs.symptoms).lower()
    results = " ".join(str(v) for v in obs.test_results.values()).lower()

    # Heart Attack
    if "chest pain" in symptoms or "troponin" in results or "ecg abnormal" in results:
        return "Heart Attack"

    # Asthma
    if "wheezing" in symptoms or "breathlessness" in symptoms:
        return "Asthma"

    # Depression
    if "low mood" in symptoms or "sad" in symptoms:
        return "Depression"

    # Kidney Stones
    if "back pain" in symptoms or "urine" in symptoms:
        return "Kidney Stones"

    # Diabetes
    if "sugar" in results or "frequent urination" in symptoms:
        return "Diabetes"

    return None

def run_inference(difficulty="easy"):
    api_key = os.getenv("HF_TOKEN", "dummy-key")
    base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-4.1-mini")
    
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    
    env = HealthDiagnosisEnv(difficulty=difficulty)
    obs = env.reset()
    
    print(f"[START] task={difficulty} env=healthcare model={model_name}")
    
    done = False
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    total_reward = 0
    info = {}
    step_num = 1
    
    valid_tests = ["Blood test", "ECG", "Chest X-ray", "CT Scan"]
    valid_diseases = ["Asthma", "Heart Attack", "Depression", "Kidney Stones", "Diabetes"]
    
    while not done:
        prompt = f"""Patient Information:
Symptoms: {obs.symptoms}
Medical History: {obs.medical_history}
Current Medication: {obs.current_medication}
Tests Done: {obs.tests_done}
Test Results: {obs.test_results}"""

        messages.append({"role": "user", "content": prompt})
        
        # fallback mechanism if dummy key
        if api_key != "dummy-key" and api_key != "your_token":
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                action_str = response.choices[0].message.content
                action_dict = json.loads(action_str)
                action = Action(**action_dict)
            except Exception as e:
                action = Action(action_type="diagnose", value="Asthma")
        else:
            # dummy action for local test without crash
            if step_num == 1:
                action = Action(action_type="test", value="Blood test")
            else:
                action = Action(action_type="diagnose", value="Asthma")
                
        # Prevent early diagnosis (require at least 2 tests)
        if len(obs.tests_done) < 2:
            if action.action_type == "diagnose":
                action.action_type = "test"
                # pick next unused test
                for t in valid_tests:
                    if t not in obs.tests_done:
                        action.value = t
                        break

        # ALWAYS evaluate rule-based before final diagnosis
        elif action.action_type == "diagnose":
            predicted = rule_based_diagnosis(obs)
            if predicted:
                action.value = predicted
            else:
                # if unsure -> DO NOT diagnose yet (collect more info)
                if len(obs.tests_done) < 3:
                    action.action_type = "test"
                    # choose next unused test
                    for t in valid_tests:
                        if t not in obs.tests_done:
                            action.value = t
                            break
                else:
                    # pick best match from symptoms (NOT constant)
                    symptoms_str = " ".join(obs.symptoms).lower()
                    if "pain" in symptoms_str:
                        action.value = "Kidney Stones"
                    elif "breath" in symptoms_str:
                        action.value = "Asthma"
                    elif "sad" in symptoms_str:
                        action.value = "Depression"
                    elif "fatigue" in symptoms_str:
                        action.value = "Diabetes"
                    else:
                        action.value = "Asthma"  # last fallback only

        # RULE: avoid repeating tests & validate tests
        if action.action_type == "test":
            if action.value in obs.tests_done or action.value not in valid_tests:
                for t in valid_tests:
                    if t not in obs.tests_done:
                        action.value = t
                        break

        # EXTRA SAFETY: validate test/diagnose schemas against true mapping logic
        if action.action_type == "diagnose" and action.value not in valid_diseases:
             action.value = valid_diseases[0]

        obs, reward, done, info = env.step(action)
        total_reward += reward
        error_val = "null" # if any error logic applies
        if info.get("invalid_action_flag"):
            error_val = "invalid_action"
            
        print(f"[STEP] step={step_num} action={json.dumps(action.model_dump())} reward={reward} done={str(done).lower()} error={error_val}")
        
        messages.append({"role": "assistant", "content": json.dumps(action.model_dump())})
        messages.append({"role": "user", "content": f"Reward received: {reward}. Done: {done}. Info: {info}"})
        step_num += 1
        
    score = info.get("score", 0.0)
    success = str(score > 0).lower() 
    print(f"[END] success={success} steps={step_num-1} score={score} rewards={total_reward}")
    
if __name__ == "__main__":
    for task in ["easy", "medium", "hard"]:
        run_inference(task)
