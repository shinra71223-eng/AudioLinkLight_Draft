import os
import traceback

try:
    comp = op('/AudioLinkLight_V01/TEST_SCREEN2')
    if comp:
        print(f"--- Objects in {comp.path} ---")
        for child in comp.findChildren(depth=1):
            if child.type == 'glsl':
                pixel_dat = child.par.pixeldat.eval() if hasattr(child.par, 'pixeldat') else 'Unknown'
                print(f"[GLSL TOP] {child.name} (pixel shader DAT: {pixel_dat})")
            elif getattr(child, 'isDAT', False) and child.type == 'text':
                content = child.text
                preview = content[:50].replace('\n', '\\n') + '...' if len(content) > 50 else content.replace('\n', '\\n')
                print(f"[Text DAT] {child.name} (content starts with: {preview})")
            elif child.type == 'glslmulti':
                pixel_dat = child.par.pixeldat.eval() if hasattr(child.par, 'pixeldat') else 'Unknown'
                print(f"[GLSL Multi TOP] {child.name} (pixel shader DAT: {pixel_dat})")
    else:
        print("TEST_SCREEN2 not found.")
except Exception as e:
    traceback.print_exc()

