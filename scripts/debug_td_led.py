# debug_td_led.py
# Run this via Textport or as a script to dump internal state
path = '/AudioLinkLight_V01/LED_OUTPUT/led_exec'
ex = op(path)
out_file = 'c:/Users/0008112871/OneDrive - Sony/ドキュメント/AntiGravity/AudioLinkLight_Draft/td_debug_output.txt'

with open(out_file, 'w', encoding='utf-8') as f:
    if not ex:
        f.write(f"ERROR: Node {path} not found\n")
    else:
        f.write(f"Node: {path}\n")
        f.write(f"Active: {ex.par.active}\n")
        f.write(f"FrameStart: {ex.par.framestart}\n")
        
        # Check source
        src_path = '/AudioLinkLight_V01/LED_OUTPUT/led_source'
        src = op(src_path)
        if src:
            f.write(f"Source: {src_path} (Res: {src.width}x{src.height})\n")
            # Check if source has any color
            pix = src.numpyArray()
            if pix is not None:
                max_val = pix.max()
                f.write(f"Source Max Value: {max_val}\n")
            else:
                f.write("Source numpyArray is None\n")
        else:
            f.write(f"ERROR: Source {src_path} not found\n")

    # Check for any current Python errors in the project
    import td
    errors = root.errors(recursive=True)
    if errors:
        f.write("\nPROJECT ERRORS:\n")
        for e in errors:
            f.write(f"  {e.owner.path}: {e.message}\n")
    else:
        f.write("\nNo errors found in project.\n")

print(f"Debug info written to {out_file}")
