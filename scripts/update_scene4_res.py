# update_scene4_res.py
# Updates all TOPs in SCENE_4 to 88x50 resolution.

SCENE_PATH = '/AudioLinkLight_V01/SCENE_4'
NEW_W = 88
NEW_H = 50

def run():
    scene = op(SCENE_PATH)
    if not scene:
        print(f"Error: {SCENE_PATH} not found")
        return

    print(f"Updating resolution of all TOPs in {SCENE_PATH} to {NEW_W}x{NEW_H}...")
    for o in scene.children:
        if o.isTOP:
            # Some TOPs might not have resolution parameters (like Null, Out if they inherit)
            # but we force them if they have the parameters.
            if hasattr(o.par, 'resolutionw'):
                o.par.resolutionw = NEW_W
                o.par.resolutionh = NEW_H
                print(f"  Updated {o.name}")
            elif hasattr(o.par, 'outputresolution'):
                o.par.outputresolution = 'custom'
                o.par.resolutionw = NEW_W
                o.par.resolutionh = NEW_H
                print(f"  Updated {o.name} (via outputresolution)")

if __name__ == '__main__':
    run()
