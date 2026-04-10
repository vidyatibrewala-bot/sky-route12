import numpy as np

def grade_task(*args, **kwargs):
    """
    Generic grader for drone tasks.
    Must return a score strictly between 0 and 1.
    """
    try:
        # Extract environment from args if provided
        env = args[0] if len(args) > 0 else kwargs.get("env", None)
        
        if env and hasattr(env, 'drone_pos') and hasattr(env, 'target_pos'):
            # Calculate Euclidean distance
            p1 = np.array(env.drone_pos)
            p2 = np.array(env.target_pos)
            dist = np.linalg.norm(p1 - p2)
            
            if dist < 0.1: # Reached target
                return 0.98
            
            # Continuous score: 0.1 to 0.9 based on proximity
            # Maximum distance in 30x30 grid is ~42
            # Using a decay function to keep it away from 0.0 and 1.0
            score = 0.9 * (1.0 / (1.0 + dist/10.0))
            return float(np.clip(score, 0.01, 0.99))
                
        return 0.05
    except Exception as e:
        print(f"Grader error: {e}")
        return 0.02

def grade_normal_delivery(*args, **kwargs):
    return grade_task(*args, **kwargs)

def grade_urgent_organ_transport(*args, **kwargs):
    return grade_task(*args, **kwargs)

def grade_storm_evasion(*args, **kwargs):
    return grade_task(*args, **kwargs)

def grade_emergency_landing(*args, **kwargs):
    return grade_task(*args, **kwargs)

