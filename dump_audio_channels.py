# dump_audio_channels.py
# Lists all COMPs at root level, then finds AudioLinkCore and dumps channels

print("\n=== All root-level COMPs ===")
for comp in root.children:
    print(f"  {comp.name} (type={type(comp).__name__})")

# Try to find anything with "audio" or "Audio" in name
print("\n=== Searching for Audio-related COMPs (recursive) ===")
for comp in root.findChildren(type=COMP, depth=2):
    if 'audio' in comp.name.lower() or 'core' in comp.name.lower():
        print(f"  FOUND: {comp.path}  (name={comp.name})")
        out = comp.op('out1')
        if out is not None:
            print(f"    out1 has {out.numChans} channels:")
            for i in range(out.numChans):
                ch = out[i]
                print(f"      [{i}] '{ch.name}' = {ch.eval():.4f}")

# Also check what sel_audio inside TEST_SCREEN is actually connected to
print("\n=== TEST_SCREEN/sel_audio status ===")
ts = root.op('TEST_SCREEN')
if ts is None:
    # Try deeper
    for comp in root.findChildren(type=COMP, depth=3):
        if comp.name == 'TEST_SCREEN':
            ts = comp
            break

if ts is not None:
    sel = ts.op('sel_audio')
    if sel is not None:
        print(f"  sel_audio.par.chop = {sel.par.chop.eval()}")
        print(f"  sel_audio numChans = {sel.numChans}")
        for i in range(sel.numChans):
            ch = sel[i]
            print(f"    [{i}] '{ch.name}' = {ch.eval():.4f}")
    else:
        print("  sel_audio not found in TEST_SCREEN")
else:
    print("  TEST_SCREEN not found")
