def grade_task(*args, **kwargs):
    """
    Generic grader for drone tasks.
    Must return a score strictly between 0 and 1.
    """
    try:
        # Extract environment from args if provided
        env = args[0] if len(args) > 0 else kwargs.get("env", None)
        
        if env and hasattr(env, 'drone_pos') and hasattr(env, 'target_pos'):
            if env.drone_pos == env.target_pos:
                return 0.99
                
        return 0.05
    except Exception as e:
        print(f"Grader error: {e}")
        return 0.02

def grade_normal_delivery(*args, **kwargs):
    return grade_task(*args, **kwargs)

def grade_urgent_transport(*args, **kwargs):
    return grade_task(*args, **kwargs)

def grade_storm_evasion(*args, **kwargs):
    return grade_task(*args, **kwargs)

