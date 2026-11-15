"""Cycle detection in deterministic finite transition systems."""
def analyse(transitions: dict[str,str], start: str, halt: str):
    seen={}; path=[]; state=start
    while state != halt:
        if state in seen:
            cycle=path[seen[state]:]+[state]
            return {"terminates":False,"path":path+[state],"cycle":cycle,"steps":len(path)}
        if state not in transitions: raise ValueError(f"No successor for {state}")
        seen[state]=len(path); path.append(state); state=transitions[state]
    return {"terminates":True,"path":path+[halt],"cycle":None,"steps":len(path)}
