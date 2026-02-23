import td

def inspect_demucs_routing():
    print("--- [Safe Inspect] Audio Routing ---")
    try:
        # Check DemucsManager
        demucs = op('/AudioLinkLight_V01/DemucsManager')
        if demucs:
            print("FOUND: /AudioLinkLight_V01/DemucsManager")
            print(f"  Targetfile: {demucs.par.Targetfile.eval()}")
            print(f"  Demucssavepath: {demucs.par.Demucssavepath.eval()}")
            print(f"  Currenttier: {demucs.par.Currenttier.eval()}")
        else:
            print("NOT FOUND: /AudioLinkLight_V01/DemucsManager")
            
        print("\n--- AudioLinkCore Inputs ---")
        core = op('/AudioLinkLight_V01/AudioLinkCore')
        if core:
            for ain in core.findChildren(type=audiofileinCHOP):
                print(f"Node: {ain.path}")
                print(f"  Expression: {ain.par.file.expr}")
                print(f"  Current Evaluated Path: {ain.par.file.eval()}")
        else:
            print("NOT FOUND: /AudioLinkLight_V01/AudioLinkCore")
            
    except Exception as e:
        print(f"Error inspecting: {e}")

inspect_demucs_routing()
