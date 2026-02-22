
import td
# We are currently in /AudioLinkCore_V01/DemucsManager probably.
# Let's find AudioLinkCore_V01 and DemucsManager

# Find the highest level AudioLinkCore
try:
    core = parent() # Assuming they run it inside or we just search globally
    core = op('/AudioLinkCore_V01')
    
    if not core:
        print('Could not find /AudioLinkCore_V01 directly.')
        # Search all
        for comp in root.findChildren(type=COMP):
            if comp.name.startswith('AudioLinkCore'):
                core = comp
                print('Found core at:', core.path)
                break
                
    if core:
        dm = core.op('DemucsManager')
        if dm:
            print('Found DemucsManager:', dm.path)
            
            # 1. Fix sel_original
            sel = dm.op('sel_original')
            if sel:
                # Need to point to File_IO_/Audio_File_IN_IO which is inside core
                file_io = core.op('File_IO_/Audio_File_IN_IO')
                if file_io:
                    # set path relative to sel
                    rel = sel.relativePath(file_io)
                    sel.par.chops = rel
                    print('Fixed sel_original CHOPs path to:', rel)
                else:
                    print('Could not find File_IO_/Audio_File_IN_IO inside', core.path)
                    
            # 2. Fix Callbacks DAT for Scripts
            for script_name, cb_name in [
                ('iso_original', 'iso_callbacks_original'),
                ('iso_instruments', 'iso_callbacks_instruments'),
                ('iso_vocals', 'iso_callbacks_vocals')
            ]:
                script = dm.op(script_name)
                cb = dm.op(cb_name)
                if script and cb:
                    rel = script.relativePath(cb)
                    script.par.callbacks = rel
                    print(f'Fixed {script_name} callbacks to:', rel)
                
            print('--- All fixes applied! ---')
            
except Exception as e:
    print('Error applying fixes:', e)

