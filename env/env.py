from typing import Tuple, Dict, Any, Optional
from .models import Observation, Action
from .tasks import generate_patient, VALID_TESTS, DISEASES, is_useful_test
from .graders import grade_episode

class HealthDiagnosisEnv:
    def __init__(self, difficulty: str = "easy"):
        self.difficulty = difficulty
        self.max_steps = 10
        self.reset()
        
    def reset(self, seed: Optional[int] = None) -> Observation:
        self.patient = generate_patient(self.difficulty, seed)
        self.step_count = 0
        self.tests_done = []
        self.test_results = {}
        
        return self._get_obs()
        
    def _get_obs(self) -> Observation:
        return Observation(
            symptoms=self.patient["symptoms"],
            medical_history=self.patient["medical_history"],
            current_medication=self.patient["current_medication"],
            tests_done=list(self.tests_done),
            test_results=dict(self.test_results),
            step_count=self.step_count
        )
        
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        self.step_count += 1
        reward = -1.0 # each step time penalty
        done = False
        info = {
            "true_disease": self.patient["true_disease"],
            "test_relevance": False,
            "invalid_action_flag": False
        }
        
        if self.step_count >= self.max_steps:
            done = True
            
        if action.action_type == "test":
            test_name = action.value
            if test_name not in VALID_TESTS:
                info["invalid_action_flag"] = True
                reward -= 3.0
            elif test_name in self.tests_done:
                reward -= 5.0
            else:
                self.tests_done.append(test_name)
                # each test cost penalty
                reward -= 2.0
                
                # Check usefulness
                if is_useful_test(test_name, self.patient["true_disease"]):
                    info["test_relevance"] = True
                    reward += 2.0
                    
                # get result
                res = self.patient["test_results"].get(test_name, "Normal")
                self.test_results[test_name] = res
                
        elif action.action_type == "diagnose":
            done = True
            disease_guess = action.value
            
            if disease_guess not in DISEASES:
                info["invalid_action_flag"] = True
                reward -= 5.0
                correct = False
            elif disease_guess == self.patient["true_disease"]:
                reward += 10.0
                correct = True
                # Implicit correct use of context in higher difficulties
                if self.difficulty in ["medium", "hard"]:
                    reward += 2.0  # correct use of medical history
                    reward += 1.0  # correct use of medication context
            else:
                reward -= 10.0
                correct = False
                # Penalties for ignoring context in higher difficulties
                if self.difficulty in ["medium", "hard"]:
                    reward -= 3.0  # ignoring important history
                    reward -= 2.0  # ignoring relevant medication
                    
            info["score"] = grade_episode(correct, len(self.tests_done), self.step_count, self.max_steps)
            
        else:
            info["invalid_action_flag"] = True
            reward -= 3.0
            
        if self.step_count >= self.max_steps and action.action_type != "diagnose":
            info["score"] = 0.0
            
        return self._get_obs(), reward, done, info
        
    def state(self) -> Dict[str, Any]:
        return {
            "difficulty": self.difficulty,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "patient": dict(self.patient),
            "tests_done": list(self.tests_done),
            "test_results": dict(self.test_results)
        }
