# diagnose_scene6_color.py
import td

SCENE_PATH = '/AudioLinkLight_V01/SCENE_6'

def diagnose():
    scene = op(SCENE_PATH)
    if not scene:
        print(f"Error: {SCENE_PATH} not found")
        return

    glsl = scene.op('glsl_baseball')
    if not glsl:
        print("Error: glsl_baseball not found")
        return

    print("="*60)
    print(f"DIAGNOSING: {glsl.path}")
    print("="*60)

    # Check Pixel Format
    # 0 = Use Input, 1 = 8-bit Fixed (RGBA), etc.
    pf = glsl.par.pixelformat
    print(f"Pixel Format: {pf.val} ({pf.menuNames[pf.menuIndex]})")
    
    # Check if a monochrome format is selected
    if 'mono' in pf.menuNames[pf.menuIndex].lower() or pf.menuNames[pf.menuIndex].startswith('R '):
        print("!!! WARNING: Pixel Format is set to a monochrome mode. This is why colors don't show.")

    # Check Input 0
    in0 = glsl.inputs[0] if len(glsl.inputs) > 0 else None
    if in0:
        print(f"Input 0: {in0.path} ({in0.width}x{in0.height} {in0.pixelFormat})")

    # Check for compile errors again (just in case they missed it)
    if glsl.errors():
        print(f"GLSL Errors:\n{glsl.errors()}")

    print("="*60)

if __name__ == '__main__':
    diagnose()
