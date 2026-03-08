# inspect_spectrum.py
SPECTRUM_PATH = '/AudioLinkLight_V01/AudioLinkCore/demucs_spectrum'
spec = op(SPECTRUM_PATH)

if spec:
    print("="*60)
    print(f"INSPECTING: {spec.name} ({spec.type})")
    print("="*60)
    
    # Check key parameters for spectrum analysis
    params = ['dboutput', 'frequencylog', 'highcut', 'lowcut', 'fftlength']
    for p_name in params:
        p = getattr(spec.par, p_name, None)
        if p is not None:
            print(f"  {p.name:15}: {p.val}")
            
    print(f"\n  Active Channels: {[c.name for c in spec.chans()]}")
    print(f"  Sample Count: {spec.numSamples}")
    
    # Check data range of the first few samples
    if spec.numSamples > 0:
        vals = [spec[0][i] for i in range(min(10, spec.numSamples))]
        print(f"  Top 10 Samples (ch0): {[round(v, 6) for v in vals]}")
        
    print("="*60)
else:
    print(f"Node {SPECTRUM_PATH} not found.")
