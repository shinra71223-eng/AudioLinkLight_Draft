# find_active_glsl_dats.py
import traceback

try:
    print("\n--- Scanning for GLSL DATs in the network ---")
    comps = [c for c in op('/').findChildren(type=glslTOP) if 'TEST_SCREEN' in c.path]
    
    if comps:
        for glsl in comps:
            # Check what pixel DAT is attached
            try:
                pixel_dat_path = glsl.par.pixeldat.eval()
                if pixel_dat_path:
                    pixel_dat = op(pixel_dat_path)
                    print(f"GLSL TOP found: {glsl.path}")
                    if pixel_dat:
                        print(f"  -> Linked Pixel DAT: {pixel_dat.path}")
                        print(f"  -> Is this DAT currently being edited: {pixel_dat.viewer}")
                    else:
                        print(f"  -> Bad Link! Missing Pixel DAT at path: {pixel_dat_path}")
            except Exception as e:
                print(f"  -> Could not evaluate pixeldat for {glsl.name}: {e}")
    else:
        print("No GLSL TOPs found containing 'TEST_SCREEN' in path.")
        
    print("--- Scan Complete ---\n")
except Exception as e:
    traceback.print_exc()
