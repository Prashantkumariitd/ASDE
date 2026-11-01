VALID={"candidate","supported","independently_replicated","disconfirmed","unresolved"}
def validate_status(status):
    if status not in VALID: raise ValueError("Invalid epistemic status")
    if status=="independently_replicated": raise ValueError("Requires recorded independent verification")
    return status
