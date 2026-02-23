import td

def apply_safe_patch():
    print("\n--- [SAFE PATCH] Fixing DemucsManager ---")
    dat = op('/AudioLinkLight_V01/DemucsManager/mod_process_manager')
    if not dat:
        print("ERROR: DAT not found.")
        return

    text = dat.text

    # Fix 1: WinError 2 (Path Encoding)
    old_init = '''    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.project_root = td.project.folder'''
        
    new_init = '''    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.project_root = self._fix_unicode(td.project.folder)'''

    if old_init in text:
        text = text.replace(old_init, new_init)
        print("-> Fixed WinError 2: Applied _fix_unicode to project_root.")
    else:
        print("-> WARNING matching __init__: Path issue already fixed or code mismatch.")

    # Fix 2: Audio Routing Lock
    old_switch = '''    def _set_tier_switch(self, tier):
        """Set the tier_switch CHOP at track start only."""
        try:
            sw = self.ownerComp.parent().op('tier_switch')
            if sw:
                val = min(1, tier)  # 0=original, 1=demucs
                sw.par.index = val
                print(f'[DemucsManager] tier_switch = {val} (Tier {tier})')
        except Exception as e:
            print(f'[DemucsManager] tier_switch error: {e}')'''

    new_switch = '''    def _set_tier_switch(self, tier):
        """Set the tier_switch CHOP at track start only."""
        try:
            sw = self.ownerComp.parent().op('tier_switch')
            if sw:
                val = min(1, tier)  # 0=original, 1=demucs
                sw.par.index = val
                print(f'[DemucsManager] tier_switch = {val} (Tier {tier})')
            
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
            print(f'[DemucsManager] tier_switch error: {e}')'''

    if old_switch in text:
        text = text.replace(old_switch, new_switch)
        print("-> Added Audio Routing Lock logic to _set_tier_switch.")
    else:
        print("-> WARNING matching _set_tier_switch: Logic already applied or code mismatch.")

    dat.text = text
    print("✅ Safe patch applied successfully! Please play the next track to test.")

apply_safe_patch()
