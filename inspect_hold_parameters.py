# inspect_hold_parameters.py
def inspect():
    temp = op('/AudioLinkLight_V01/TEST_SCREEN2').create(holdCHOP, 'temp_hold')
    print("\n--- Hold CHOP Parameters ---")
    for p in temp.pars():
        print(f"{p.name}: {p.label}")
    temp.destroy()

inspect()
