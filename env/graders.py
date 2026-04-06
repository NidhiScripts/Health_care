def grade_episode(correct_diagnosis: bool, num_tests: int, step_count: int, max_steps: int = 10) -> float:
    if not correct_diagnosis:
        return 0.0
        
    if num_tests <= 2:
        return 1.0
        
    if step_count >= max_steps - 1:
        return 0.5
        
    return 0.7
