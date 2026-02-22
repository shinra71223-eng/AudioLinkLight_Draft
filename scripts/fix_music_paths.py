# fix_music_paths.py
# Fixes music folder paths to use project-relative paths
# Run in TD Textport after moving music files to media/music/
#
# Verified TD API: par.chops (plural), par.file, par.rootfolder,
#   len(conn.connections)>0, ParMode.EXPRESSION

def fix():
    core = None
    for comp in root.findChildren(type=COMP):
        if 'AudioLinkLight_V' in comp.name:
            core = comp
            break
    if not core:
        print('ERROR: AudioLinkLight not found')
        return

    pf = project.folder  # e.g. C:/Users/.../AudioLinkLight
    music_dir = pf + '/media/music'

    fio = core.op('File_IO_')
    if not fio:
        print('ERROR: File_IO_ not found')
        return

    # 1. Fix folder_music DAT rootfolder
    fm = fio.op('folder_music')
    if fm:
        old = fm.par.rootfolder.eval()
        fm.par.rootfolder = music_dir
        print(f'folder_music.rootfolder:')
        print(f'  OLD: {old}')
        print(f'  NEW: {music_dir}')

    # 2. Fix Audio_File_IN_IO (will auto-update when playlist selects a file)
    # The file parameter uses an expression or absolute path
    # We just need to ensure folder_music points to the right place
    # The playlist system will handle the rest

    ain = fio.op('Audio_File_IN_IO')
    if ain:
        old_file = ain.par.file.eval()
        print(f'\nAudio_File_IN_IO.file:')
        print(f'  Current: {old_file}')
        # If file is an expression, leave it alone
        if ain.par.file.mode == ParMode.EXPRESSION:
            print(f'  Mode: EXPRESSION (auto-managed, OK)')
        else:
            print(f'  Mode: CONSTANT')
            # Check if any music files exist in the new folder
            import os
            if os.path.exists(music_dir):
                files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav', '.flac'))]
                if files:
                    new_file = music_dir + '/' + files[0]
                    ain.par.file = new_file
                    print(f'  NEW: {new_file}')
                else:
                    print(f'  WARNING: No music files in {music_dir}')
                    print(f'  Copy music files there, then this will auto-update on next playlist cycle')

    print('\n=== Music path fix complete ===')
    print(f'Music folder: {music_dir}')
    print('Copy your music files to media/music/ and restart playback.')

fix()
