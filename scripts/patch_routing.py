import td

def apply_demucs_routing_patch():
    print("--- [Patch] Applying Demucs Routing to AudioLinkCore ---")
    core = op('/AudioLinkLight_V01/AudioLinkCore')
    
    if not core:
        print("ERROR: Could not find /AudioLinkLight_V01/AudioLinkCore")
        return
        
    audio_ins = core.findChildren(type=audiofileinCHOP)
    if not audio_ins:
        print("ERROR: No Audio File In CHOPs found inside AudioLinkCore")
        return
        
    for ain in audio_ins:
        # Assuming names like 'Audio_vocals', 'Audio_no_vocals', etc.
        parts = ain.name.split('_')
        if len(parts) >= 2:
            stem_name = parts[1] # 'vocals' or 'no_vocals'
            
            # The core logic rule set by user:
            # Tier 0 -> Original File (Targetfile)
            # Tier 1 -> FAST stems (Demucssavepath + stem_name)
            # Tier 2 -> HQ stems (Demucssavepath + stem_name)
            
            # We write an expression that evaluates this logic on the fly.
            expr = f"op('/AudioLinkLight_V01/DemucsManager').par.Demucssavepath.eval() + '/{stem_name}.wav' if op('/AudioLinkLight_V01/DemucsManager').par.Currenttier.eval() > 0 else op('/AudioLinkLight_V01/DemucsManager').par.Targetfile.eval()"
            
            ain.par.file.expr = expr
            print(f"Patched {ain.path}")
            print(f"  -> Expression: {expr}")
            
    print("✅ Routing Patch Applied Successfully!")

apply_demucs_routing_patch()
