# diagnose_crop_params.py
# Run this in TD Textport to see the exact parameter names for a Crop TOP.

def run_diagnosis():
    # Create a temporary Crop TOP if one doesn't exist to inspect it
    temp_crop = op('/AudioLinkLight_V01/LED_OUTPUT').create(cropTOP, 'temp_crop_diagnose')
    
    print("="*60)
    print(f"DIAGNOSING PARAMETERS FOR: {temp_crop.type}")
    print("="*60)
    
    # List all parameters and their labels
    for p in temp_crop.par:
        print(f"Label: {p.label:<20} | Name: {p.name}")
    
    print("="*60)
    
    # Clean up
    temp_crop.destroy()

run_diagnosis()
