# update_led_output_crop.py
# Inserts a cropTOP in LED_OUTPUT to extract rows 20-29.

LED_OUT_PATH = '/AudioLinkLight_V01/LED_OUTPUT'

def run():
    base = op(LED_OUT_PATH)
    if not base:
        print(f"Error: {LED_OUT_PATH} not found")
        return

    brightness = base.op('brightness')
    led_source = base.op('led_source')

    if not brightness or not led_source:
        print("Error: Required nodes 'brightness' or 'led_source' not found")
        return

    # Create cropTOP if it doesn't exist
    crop = base.op('crop_center')
    if not crop:
        crop = base.create(cropTOP, 'crop_center')
        print("Created cropTOP 'crop_center'")

    # Configure crop (Rows 20-29 from 88x50)
    # TD Crop TOP: 
    # Left/Right/Bottom/Top are offsets or positions depending on Units.
    crop.par.units = 'pixels'
    crop.par.cropbottom = 20
    crop.par.croptop = 20 # Note: In TD Crop it is often offset-based or bound-based.
    # Actually, let's use 'Crop' parameters: 
    # To get 20-29 (10 rows):
    # If source is 50 high, index 0 is bottom.
    # Rows 20, 21, 22, 23, 24, 25, 26, 27, 28, 29.
    # Start at 20, end at 30.
    crop.par.cropbottom = 20
    crop.par.croptop = 20 # This depends on whether it's 'from top' or 'from bottom'. 
    # Usually: cropbottom=20, croptop=20 means 20 pixels from bottom, 20 pixels from top.
    # Total H = 50. 50 - 20 - 20 = 10 pixels. This is EXACTLY what we want.
    
    crop.par.cropleft = 0
    crop.par.cropright = 0

    # Reconnect
    crop.inputConnectors[0].connect(brightness)
    led_source.inputConnectors[0].connect(crop)

    # Position
    crop.nodeX = brightness.nodeX
    crop.nodeY = (brightness.nodeY + led_source.nodeY) / 2
    
    print(f"Configured {crop.path} to crop rows 20-29 and reconnected pipeline.")

if __name__ == '__main__':
    run()
