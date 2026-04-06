from env import HealthDiagnosisEnv, Observation, Action

def main():
    print("Testing Easy Environment...")
    env = HealthDiagnosisEnv("easy")
    obs = env.reset(seed=42)
    assert isinstance(obs, Observation)
    print("Reset OK. Obs:", obs.model_dump())
    
    # Test valid action
    action = Action(action_type="test", value="Blood test")
    obs, reward, done, info = env.step(action)
    print("Step 1 (test blood test) OK. Reward:", reward, "Done:", done, "Info:", info)
    
    # Test diagnose
    action = Action(action_type="diagnose", value=info["true_disease"])
    obs, reward, done, info = env.step(action)
    print("Step 2 (diagnose correct) OK. Reward:", reward, "Done:", done, "Info:", info)
    assert done
    
    # Test max steps
    print("\nTesting Max Steps and Invalid Actions...")
    env = HealthDiagnosisEnv("hard")
    env.reset(seed=1337)
    
    # Invalid Test
    action = Action(action_type="test", value="Fake Test")
    obs, reward, done, info = env.step(action)
    assert info["invalid_action_flag"] == True
    print("Invalid test penalty applied OK:", reward)
    
    for _ in range(9):
        env.step(Action(action_type="test", value="Blood test"))
        
    action = Action(action_type="test", value="Blood test")
    obs, reward, done, info = env.step(action)
    assert done == True
    print("Max steps termination OK. Info:", info)
    
    print("\nState output:", env.state())
    print("\nAll Tests Passed!")

if __name__ == "__main__":
    main()
