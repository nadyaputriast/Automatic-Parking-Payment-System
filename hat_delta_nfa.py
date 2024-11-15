from delta_function import delta

def hat_delta(states, input_char):
    next_states = set()

    for state in states:
        trans = delta(state, input_char)
        next_states.update(trans)
    
    return next_states