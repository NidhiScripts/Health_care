import random
from typing import Dict, Any, List

DISEASES = ["Asthma", "Heart Attack", "Depression", "Kidney Stones", "Diabetes"]

DISEASE_DATA = {
    "Asthma": {
        "easy_symptoms": ["Shortness of breath", "Wheezing", "Coughing"],
        "medium_symptoms": ["Shortness of breath", "Chest tightness"],
        "hard_symptoms": ["Shortness of breath", "Fatigue"],
        "medical_history": ["History of allergies", "Family history of asthma"],
        "hard_medical_history": ["History of anxiety (confounding)", "Smoker"],
        "current_medication": ["Albuterol inhaler (PRN)", "None"],
        "hard_current_medication": ["Anti-anxiety meds (Xanax)"],
        "tests": {
            "Spirometry": "Reduced FEV1, reversible with bronchodilator",
            "Chest X-ray": "Hyperinflation",
            "Blood test": "Normal",
            "ECG": "Normal"
        }
    },
    "Heart Attack": {
        "easy_symptoms": ["Severe chest pain", "Radiating arm pain", "Sweating"],
        "medium_symptoms": ["Shortness of breath", "Chest pressure"],
        "hard_symptoms": ["Fatigue", "Mild chest discomfort", "Nausea"],
        "medical_history": ["Hypertension", "High cholesterol"],
        "hard_medical_history": ["History of acid reflux (confounding)"],
        "current_medication": ["Statins", "Aspirin"],
        "hard_current_medication": ["Antacids"],
        "tests": {
            "ECG": "ST elevation",
            "Troponin": "Elevated",
            "Chest X-ray": "Normal",
            "Blood test": "Normal"
        }
    },
    "Depression": {
        "easy_symptoms": ["Persistent sadness", "Loss of interest", "Suicidal thoughts"],
        "medium_symptoms": ["Fatigue", "Insomnia"],
        "hard_symptoms": ["Unexplained physical aches", "Fatigue", "Lack of concentration"],
        "medical_history": ["Previous depressive episode", "None"],
        "hard_medical_history": ["Hypothyroidism (treated)"],
        "current_medication": ["None", "SSRIs (stopped 6 months ago)"],
        "hard_current_medication": ["Levothyroxine"],
        "tests": {
            "PHQ-9": "Score > 15 (Severe)",
            "Blood test": "Normal",
            "Thyroid Panel": "Normal",
            "ECG": "Normal"
        }
    },
    "Kidney Stones": {
        "easy_symptoms": ["Severe flank pain", "Blood in urine", "Pain on urination"],
        "medium_symptoms": ["Back pain", "Nausea"],
        "hard_symptoms": ["Vague abdominal pain", "Frequent urination"],
        "medical_history": ["Previous kidney stones", "Gout"],
        "hard_medical_history": ["Frequent UTIs (confounding)"],
        "current_medication": ["None", "Thiazide diuretics"],
        "hard_current_medication": ["Antibiotics (recent)"],
        "tests": {
            "Urinalysis": "Hematuria (blood in urine)",
            "CT Scan": "Calculus present in ureter",
            "Blood test": "Normal",
            "Ultrasound": "Hydronephrosis"
        }
    },
    "Diabetes": {
        "easy_symptoms": ["Frequent urination", "Excessive thirst", "Unexplained weight loss"],
        "medium_symptoms": ["Fatigue", "Blurred vision"],
        "hard_symptoms": ["Frequent infections", "Fatigue", "Tingling in feet"],
        "medical_history": ["Family history of diabetes", "Obesity"],
        "hard_medical_history": ["Peripheral neuropathy (suspected)"],
        "current_medication": ["None"],
        "hard_current_medication": ["Gabapentin"],
        "tests": {
            "Fasting Blood Sugar": "> 126 mg/dL",
            "HbA1c": "> 6.5%",
            "Urinalysis": "Glucose present",
            "Blood test": "Elevated glucose"
        }
    }
}

VALID_TESTS = {
    "Spirometry", "Chest X-ray", "Blood test", "ECG", "Troponin", 
    "PHQ-9", "Thyroid Panel", "Urinalysis", "CT Scan", "Ultrasound",
    "Fasting Blood Sugar", "HbA1c"
}

def generate_patient(difficulty: str, seed: int = None) -> Dict[str, Any]:
    if seed is not None:
        random.seed(seed)
    
    disease = random.choice(DISEASES)
    data = DISEASE_DATA[disease]
    
    patient = {
        "true_disease": disease,
        "test_results": data["tests"]
    }
    
    if difficulty == "easy":
        patient["symptoms"] = list(data["easy_symptoms"])
        patient["medical_history"] = [random.choice(data["medical_history"])]
        patient["current_medication"] = [random.choice(data["current_medication"])]
    elif difficulty == "medium":
        patient["symptoms"] = list(data["medium_symptoms"])
        patient["medical_history"] = [random.choice(data["medical_history"])]
        patient["current_medication"] = [random.choice(data["current_medication"])]
    elif difficulty == "hard":
        patient["symptoms"] = list(data["hard_symptoms"])
        patient["medical_history"] = [random.choice(data["hard_medical_history"])]
        patient["current_medication"] = [random.choice(data["hard_current_medication"])]
        
    return patient

def is_useful_test(test_name: str, disease: str) -> bool:
    # A test is useful if it gives an abnormal/specific result for the true disease
    res = DISEASE_DATA[disease]["tests"].get(test_name, "Normal")
    if res in ["Normal", "Not indicated"]:
        return False
    return True
