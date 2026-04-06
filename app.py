import io
import sys
import json
import re
from flask import Flask, render_template, request, jsonify
from inference import run_inference

app = Flask(__name__)

# Dictionary to generate simulated reasoning mappings for UI display
REASONING_MAP = {
    # Tests
    "Blood test": "Analyzing systemic biomarkers, sugar levels, and metabolic indicators.",
    "ECG": "Evaluating electrical activity of the heart for cardiovascular abnormalities.",
    "Chest X-ray": "Imaging lung fields to rule out respiratory, structural, or asthmatic complications.",
    "CT Scan": "Gathering detailed cross-sectional diagnostic imaging for complex tissue anomalies.",
    # Diagnoses
    "Asthma": "Confirmed via wheezing, breathlessness, and potential chest tightness.",
    "Heart Attack": "Confirmed via acute chest pain, elevated troponin, or severe ECG abnormalities.",
    "Depression": "Confirmed via persistent low mood, sadness, and psychological fatigue.",
    "Kidney Stones": "Confirmed via localized severe back pain and associated urinary symptoms.",
    "Diabetes": "Confirmed via elevated blood sugar and characteristic fatigue."
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_episode():
    data = request.json or {}
    difficulty = data.get("difficulty", "easy")
    
    # Capture stdout securely without modifying inference.py logic
    old_stdout = sys.stdout
    sys.stdout = capture = io.StringIO()
    
    try:
        run_inference(difficulty)
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify({"error": str(e)}), 500
        
    sys.stdout = old_stdout
    output = capture.getvalue()
    
    # Intelligently parse the native console logs
    steps = []
    final_diagnosis = "Unknown"
    score = 0.0
    total_reward = 0.0
    
    for line in output.split('\n'):
        if line.startswith("[STEP]"):
            try:
                # Regex safely maps variables exactly from your logging architecture
                step_match = re.search(r"step=(\d+)", line)
                step_num = int(step_match.group(1)) if step_match else 0
                
                action_match = re.search(r"action=(\{.*?\})\s+reward", line)
                action_dict = json.loads(action_match.group(1)) if action_match else {}
                
                reward_match = re.search(r"reward=([-0-9.]+)", line)
                reward = float(reward_match.group(1)) if reward_match else 0.0
                
                if action_dict:
                    action_type = action_dict.get("action_type", "")
                    value = action_dict.get("value", "")
                    
                    if action_type == "diagnose":
                        final_diagnosis = value
                        
                    steps.append({
                        "step": step_num,
                        "action_type": action_type,
                        "value": value,
                        "reward": reward,
                        "reason": REASONING_MAP.get(value, "Gathering contextual patient feedback.")
                    })
            except Exception as parse_e:
                print("Parse error on step:", parse_e)
                
        elif line.startswith("[END]"):
            score_match = re.search(r"score=([0-9.]+)", line)
            if score_match:
                score = float(score_match.group(1))
                
            rew_match = re.search(r"rewards=([-0-9.]+)", line)
            if rew_match:
                total_reward = float(rew_match.group(1))
                
    return jsonify({
        "steps": steps,
        "final_diagnosis": final_diagnosis,
        "score": score,
        "total_reward": total_reward,
        "raw_output": output
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
