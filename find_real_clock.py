# find_real_clock.py
import traceback

def find():
    try:
        print("\n=== Scanning for Real Clock Source ===")
        # Search for any CHOP with 'hour' channel
        chops = op('/AudioLinkLight_V01').findChildren(type=CHOP)
        for c in chops:
            chan_names = [chan.name for chan in c.chans()]
            if 'hour' in chan_names or 'minute' in chan_names:
                print(f"FOUND CHOP: {c.path} (Channels: {chan_names})")
                print(f"  Sample Values: hour={c['hour'] if 'hour' in chan_names else 'N/A'}, min={c['minute'] if 'minute' in chan_names else 'N/A'}")
        
        # Search for any DAT with 'hour'
        dats = op('/AudioLinkLight_V01').findChildren(type=DAT)
        for d in dats:
            if d.name == 'clock_updater_v2':
                print(f"INFO: clock_updater_v2 type is {type(d)}")
                if hasattr(d, 'row'): # It's a table
                     print(f"  Rows: {[r.val for r in d.col(0)] if d.numCols > 0 else 'No cols'}")

        # Check for common clock names
        for name in ['clock', 'time', 'clock_dat', 'clock_data']:
             match = op('/AudioLinkLight_V01/TEST_SCREEN2/' + name)
             if match:
                 print(f"FOUND candidate in TEST_SCREEN2: {match.path} ({type(match)})")

    except Exception as e:
        traceback.print_exc()

find()
