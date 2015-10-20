def from_DT_Switch_to_low_high(x):
    # 0 - 1 translated to low / high
    if str(x) == "0":
        return "low"
    else:
        return "high"

