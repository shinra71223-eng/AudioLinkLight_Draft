# update_scene4_full.py
# This script combines the resolution update and the crop insertion.
# Copy-paste this into the TouchDesigner Textport and press Enter.

def run_update():
    # 1. Update ALL SCENE_X Resolutions to 88x50
    root = op('/AudioLinkLight_V01')
    new_w, new_h = 88, 50
    
    for i in range(1, 7):
        scene_path = f'/AudioLinkLight_V01/SCENE_{i}'
        scene = op(scene_path)
        if not scene:
            print(f"Skip: {scene_path} not found")
            continue
            
        print(f"Updating resolution of all TOPs in {scene_path} to {new_w}x{new_h}...")
        for o in scene.children:
            if o.isTOP:
                if hasattr(o.par, 'resolutionw'):
                    o.par.resolutionw = new_w
                    o.par.resolutionh = new_h
                elif hasattr(o.par, 'outputresolution'):
                    o.par.outputresolution = 'custom'
                    o.par.resolutionw = new_w
                    o.par.resolutionh = new_h

            # --- Visual Adjustments for 50px Height ---
            # Horizontal Shooting Stars (rect_star0-3)
            # Original sizey was 0.1 (1px in 10px height). Now 1/50 = 0.02.
            if o.name.startswith('rect_star'):
                if hasattr(o.par, 'sizey'): o.par.sizey = 0.02 # 1 pixel in 50px height
                
                # Adjust centery to fit in the LED window (Rows 20-29)
                # Normalized range for rows 20-29 in 50px height is approx [-0.09, 0.09]
                if hasattr(o.par, 'centery'):
                    orig_y = o.par.centery.val
                    # Map old [-0.5, 0.5] (10px) to new [-0.1, 0.1] (center 10px of 50px)
                    new_y = orig_y * (10.0 / 50.0) 
                    o.par.centery = new_y
                print(f"  Adjusted {o.name} size/position")

            # Vertical Lines (rect_v0-3)
            # Original sizex was 2/88. This is absolute pixel count, so it stays.
            # But they are currently full height (1.0). If you want them only in the LED area:
            # if o.name.startswith('rect_v'):
            #     if hasattr(o.par, 'sizey'): o.par.sizey = 0.2 # 10/50

    # 2. Insert Crop in LED_OUTPUT
    led_out_path = '/AudioLinkLight_V01/LED_OUTPUT'
    base = op(led_out_path)
    if not base:
        print(f"Error: {led_out_path} not found")
    else:
        scene_select = base.op('scene_select')
        brightness = base.op('brightness')
        led_source = base.op('led_source')
        
        if not brightness or not led_source:
            print("Error: Required nodes 'brightness' or 'led_source' not found")
        else:
            # --- Ensure resolution propagates as 88x50 until the crop ---
            # Set to 'Use Input' (typically 0 or 'input')
            for node in [scene_select, brightness]:
                if node and hasattr(node.par, 'outputresolution'):
                    node.par.outputresolution = 0 # Use Input
                    print(f"  Set {node.name} to 'Use Input' resolution")

            crop = base.op('crop_center') or base.create(cropTOP, 'crop_center')
            
            # Corrected Parameter Names based on diagnosis:
            # Units: 0=Fraction, 1=Pixels
            crop.par.cropbottomunit = 1  
            crop.par.croptopunit = 1
            crop.par.cropleftunit = 1
            crop.par.croprightunit = 1
            
            # Values (Rows 20-29 from 88x50)
            crop.par.cropbottom = 20
            crop.par.croptop = 20
            crop.par.cropleft = 0
            crop.par.cropright = 0

            # Fix Common settings for LED (Nearest Neighbor)
            # 0=Nearest, 1=Linear
            if hasattr(crop.par, 'inputfiltertype'): crop.par.inputfiltertype = 0
            if hasattr(crop.par, 'filtertype'): crop.par.filtertype = 0
            
            crop.inputConnectors[0].connect(brightness)
            
            # Ensure led_source also inherits the 88x10 from the crop
            if hasattr(led_source.par, 'outputresolution'):
                led_source.par.outputresolution = 0 # Use Input
            led_source.inputConnectors[0].connect(crop)
            
            # nodeX, nodeY are not touched to preserve manual layout.
            print(f"Configured {crop.path} to crop rows 20-29 and reconnected pipeline.")

    print("\n[SUCCESS] SCENE_4 expanded to 88x50 and LED_OUTPUT crop configured.")

run_update()
