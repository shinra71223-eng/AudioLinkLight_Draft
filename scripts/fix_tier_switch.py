import td

def fix_tier_switch_path():
    print("\n--- [FIX] Updating tier_switch Path inside mod_process_manager ---")
    dat = op('/AudioLinkLight_V01/DemucsManager/mod_process_manager')
    if not dat:
        print("ERROR: DAT not found.")
        return

    text = dat.text

    # Let's locate the _set_tier_switch definition
    import re
    
    # We want to replace the entire _set_tier_switch method with the correct path
    
    # The new version
    new_method = """    def _set_tier_switch(self, tier):
        \"\"\"Set the tier_switch CHOP at track start only.\"\"\"
        try:
            # FIX: Look for it INSIDE DemucsManager itself, not the parent
            sw = self.ownerComp.op('tier_switch')
            if sw:
                val = min(1, tier)  # 0=original, 1=demucs
                sw.par.index = val
                print(f'[DemucsManager] tier_switch = {val} (Tier {tier})')
            else:
                print(f'[DemucsManager] ERROR: tier_switch not found inside DemucsManager!')
            
            # --- SAFE AUDIO ROUTING LOCK ---
            # Automatically assign fixed file paths instead of using an active Expression
            core = self.ownerComp.parent().op('AudioLinkCore')
            if core:
                tfile = self.ownerComp.par.Targetfile.eval()
                dpath = self.ownerComp.par.Demucssavepath.eval()
                for ain in core.findChildren(type=audiofileinCHOP):
                    ain.par.file.expr = ''  # Kill the live expression completely
                    stem = ain.name.split('_')[1]
                    if tier > 0 and dpath:
                        ain.par.file = f"{dpath}/{stem}.wav"
                    else:
                        ain.par.file = tfile
                print(f"[DemucsManager] [LOCK] AudioLinkCore routing fixed for this track.")
        except Exception as e:
            print(f'[DemucsManager] tier_switch error: {e}')"""

    # We will use regex to find the start of _set_tier_switch up to OnFileChange
    pattern = re.compile(r'    def _set_tier_switch\(self, tier\):.*?    def OnFileChange\(self, filepath\):', re.DOTALL)
    
    if pattern.search(text):
        new_text = pattern.sub(new_method + "\n\n    def OnFileChange(self, filepath):", text)
        dat.text = new_text
        print("✅ Fixed tier_switch routing path successfully! Switch will now work.")
        
        # Manually trigger it right now to fix the current track
        try:
            current_tier = op('/AudioLinkLight_V01/DemucsManager').par.Currenttier.eval()
            sw = op('/AudioLinkLight_V01/DemucsManager/tier_switch')
            if sw:
                sw.par.index = min(1, current_tier)
                print(f"-> Manually updated active tier_switch to {sw.par.index}")
        except Exception as e:
            print(f"Error triggering manual switch: {e}")
            
    else:
        print("ERROR: Could not find _set_tier_switch method in dat.text.")

fix_tier_switch_path()
