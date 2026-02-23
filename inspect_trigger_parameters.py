# inspect_trigger_parameters.py
def inspect():
    temp = op('/AudioLinkLight_V01/TEST_SCREEN2').create(triggerCHOP, 'temp_trigger')
    print("\n--- Trigger CHOP Parameters ---")
    for p in temp.pars():
        print(f"{p.name}: {p.label}")
    temp.destroy()

inspect()
