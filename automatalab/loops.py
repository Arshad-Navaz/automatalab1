def analyse_termination(transitions, start, halt):
    path = []
    first_seen = {}
    state = start
    while state != halt:
        if state in first_seen:
            cycle = path[first_seen[state]:] + [state]
            return {"terminates": False, "path": path + [state],
                    "cycle": cycle, "steps": len(path)}
        if state not in transitions:
            raise ValueError(f"Missing successor for non-halting state {state}")
        first_seen[state] = len(path)
        path.append(state)
        state = transitions[state]
    return {"terminates": True, "path": path + [halt],
            "cycle": None, "steps": len(path)}

def step_budget(transitions, start, halt, budget):
    if budget < 0:
        raise ValueError("Budget must be non-negative")
    path = []
    state = start
    for _ in range(budget + 1):
        if state == halt:
            return {"terminates": True, "path": path + [halt]}
        if state not in transitions:
            raise ValueError(f"Missing successor for {state}")
        path.append(state)
        state = transitions[state]
    return {"terminates": False, "path": path}
