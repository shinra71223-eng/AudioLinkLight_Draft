# inspect_speed_parameters.py
def inspect():
    temp = op('/AudioLinkLight_V01/TEST_SCREEN2').create(speedCHOP, 'temp_speed')
    print("\n--- Speed CHOP Parameters ---")
    for p in temp.pars():
        print(f"{p.name}: {p.label}")
    temp.destroy()

inspect()
