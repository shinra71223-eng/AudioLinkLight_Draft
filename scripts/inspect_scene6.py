# inspect_scene6.py
import td

SCENE_PATH = '/AudioLinkLight_V01/SCENE_6'

def inspect():
    scene = op(SCENE_PATH)
    if not scene:
        print(f"Error: {SCENE_PATH} not found")
        return

    print("=" * 60)
    print(f"INSPECTING SCENE: {SCENE_PATH}")
    print("=" * 60)

    # List key TOPs and their resolutions
    for top in scene.findChildren(type=TOP):
        # We are interested in Output resolution and key nodes like Text TOPs
        if top.type == 'text' or top.name == 'out1' or top.name == 'scene_out':
            w = top.par.w if hasattr(top.par, 'w') else 'N/A'
            h = top.par.h if hasattr(top.par, 'h') else 'N/A'
            print(f"Node: {top.name:20} Type: {top.type:10} Res: {w}x{h}")

    # Check for specific scroll logic nodes
    scroll_nodes = scene.findChildren(name='*scroll*')
    for node in scroll_nodes:
        print(f"Scroll Node: {node.name:20} Type: {node.type}")

    print("=" * 60)

if __name__ == '__main__':
    inspect()
