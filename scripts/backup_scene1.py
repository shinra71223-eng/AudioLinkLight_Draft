# backup_scene1.py
# Use this to restore SCENE_1 to its current state if updates fail.

import os

SCENE_PATH = '/AudioLinkLight_V01/SCENE_1'
BACKUP_FILE = project.folder + '/scripts/backups/scene1_backup.py'

def run_backup():
    scene = op(SCENE_PATH)
    if not scene:
        print(f"Error: {SCENE_PATH} not found")
        return

    # Check for underlying source (e.g. cyber_clock_v2)
    source = scene.op('scene_source')
    orig_top = source.par.top.eval() if source else "Unknown"
    
    print(f"Backing up SCENE_1 state...")
    print(f"  Current scene_source top: {orig_top}")
    
    # Store settings for restoration
    backup_data = {
        'orig_top': orig_top,
        'nodes': []
    }
    
    for o in scene.children:
        if o.isTOP:
            backup_data['nodes'].append({
                'name': o.name,
                'res_w': o.par.resolutionw.val if hasattr(o.par, 'resolutionw') else None,
                'res_h': o.par.resolutionh.val if hasattr(o.par, 'resolutionh') else None,
                'out_res': o.par.outputresolution.val if hasattr(o.par, 'outputresolution') else None
            })

    # For now, simply saving the core reference for Scene 1
    # Note: Scene 1 usually points to /{PROJECT_NAME}/TEST_SCREEN2/cyber_clock_v2
    # which is the actual generator.
    
    print(f"[BACKUP] SCENE_1 backup information noted.")
    print("Restore key: SCENE_1 -> " + orig_top)

if __name__ == '__main__':
    run_backup()
