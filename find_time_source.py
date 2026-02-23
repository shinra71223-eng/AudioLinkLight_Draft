import traceback

try:
    print("\n--- Searching for Time sources in /AudioLinkLight_V01 ---")
    # Finding all CHOPs with channels like 'hour', 'min', 'sec'
    found = False
    for chop in op('/AudioLinkLight_V01').findChildren(type=CHOP):
        chans = [c.name for c in chop.chans()]
        if any(name in chans for name in ['hour', 'minute', 'second', 'sec', 'min']):
            print(f"FOUND Time CHOP: {chop.path} (Channels: {chans})")
            found = True
            
    if not found:
        # Check system-wide or common locations
        print("No specific Time CHOP found. Using Python datetime fallback in setup script.")
except Exception as e:
    traceback.print_exc()
