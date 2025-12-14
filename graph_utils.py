def safety_color(p):
    if p < 0.3:
        return "green"
    elif p < 0.7:
        return "orange"
    else:
        return "red"
