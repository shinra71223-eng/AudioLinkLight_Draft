# inspect_bloom.py
SCENE_PATH = '/AudioLinkLight_V01/SCENE_5'
scene = op(SCENE_PATH)

def dump_node(o):
    print(f"\n[{o.type}] {o.name}")
    print(f"  Resolution: {o.width}x{o.height}")
    print(f"  Inputs: {[i.owner.name for i in o.inputs if i]}")
    for p in o.pars('*'):
        if p.mode == ParMode.EXPRESSION or (p.val != p.default and not p.isMenu):
            # Only print relevant params
            if any(k in p.name.lower() for k in ['color', 'alpha', 'scale', 'sx', 'sy', 'tx', 'ty', 'rz', 'radius', 'soft', 'thresh', 'operand', 'top']):
                val_str = f"{p.val}" if p.mode != ParMode.EXPRESSION else f"EXPR: {p.expr} (current: {p.val})"
                print(f"    {p.name}: {val_str}")

if scene:
    print("="*60)
    print("BLOOM DIAGNOSTICS")
    print("="*60)
    for o in scene.children:
        dump_node(o)
    
    # Check AudioLink too
    audio = op('/AudioLinkLight_V01/AudioLinkCore/out1')
    if audio:
        print("\nAUDIO CHANNELS:")
        for c in audio.chans():
            print(f"  {c.name}: {c[0]:.4f}")
    else:
        print("\nAudioLinkCore/out1 NOT FOUND")
    print("="*60)
else:
    print("SCENE_5 NOT FOUND")
