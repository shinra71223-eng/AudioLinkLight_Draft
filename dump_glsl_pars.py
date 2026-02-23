import traceback

try:
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    if glsl:
        print(f"--- Parameters for {glsl.path} containing 'chop' or 'array' ---")
        for p in glsl.pars():
            if 'chop' in p.name.lower() or 'array' in p.name.lower() or 'uni' in p.name.lower():
                print(f"{p.name}: {p.val}")
    else:
        print("Not found")
except Exception as e:
    traceback.print_exc()
