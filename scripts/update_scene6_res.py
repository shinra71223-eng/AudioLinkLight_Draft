# update_scene6_res.py
import td

SCENE_PATH = '/AudioLinkLight_V01/SCENE_6'

def update():
    scene = op(SCENE_PATH)
    if not scene:
        print(f"Error: {SCENE_PATH} not found")
        return

    print(f"Updating resolutions in {SCENE_PATH} to 88x50...")
    
    # Target resolution
    target_w = 88
    target_h = 50

    # Find all TOPs except those that should inherit or have fixed res
    for top in scene.findChildren(type=TOP):
        # Skip nodes that are specifically meant to be different or are inputs
        # But for most scene nodes, we want them at 88x50
        try:
            # Set resolution if parameters exist
            if hasattr(top.par, 'w') and hasattr(top.par, 'h'):
                top.par.w = target_w
                top.par.h = target_h
                # Set fit mode to 'Match Monitor' or 'Custom Resolution' if needed
                # Usually setting w/h directly works if they are already in Custom mode
                print(f"  Set {top.name} to {target_w}x{target_h}")
        except Exception as e:
            print(f"  Failed to update {top.name}: {e}")

    print("Resolution update complete.")

if __name__ == '__main__':
    update()
