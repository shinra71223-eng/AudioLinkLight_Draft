# apply_led_sender_4source.py
# Run in TD Textport:
#   exec(open(project.folder + '/scripts/apply_led_sender_4source.py', encoding='utf-8').read())

TARGET_COMP = '/AudioLinkLight_V01/LED_OUTPUT'

def run():
    base = op(TARGET_COMP)
    if not base:
        # Try fallback to TEST_SCREEN
        print(f"WARN: {TARGET_COMP} not found, trying /AudioLinkLight_V01/TEST_SCREEN")
        TARGET_COMP_FALLBACK = '/AudioLinkLight_V01/TEST_SCREEN'
        base = op(TARGET_COMP_FALLBACK)

    if not base:
        print(f"ERROR: Could not find LED_OUTPUT or TEST_SCREEN in /AudioLinkLight_V01")
        return

    print(f"Updating {base.path}/led_exec with 4-source sender...")
    
    # Ensure led_exec exists
    ex = base.op('led_exec')
    if not ex:
        ex = base.create(executeDAT, 'led_exec')
        ex.par.framestart = True
        ex.nodeX = 400
        ex.nodeY = -800
    
    # Disable while updating
    original_active = ex.par.active
    ex.par.active = False
    
    # Load and apply script
    script_path = project.folder + '/scripts/dats/led_sender_pyserial_4source.py'
    try:
        with open(script_path, encoding='utf-8') as f:
            ex.text = f.read()
    except Exception as e:
        print(f"ERROR reading script file: {e}")
        return
    
    # Ensure Source TOPs exist
    # Sources: led_source_u1, led_source, led_source_d1, led_source_USB
    SOURCES = ['led_source_u1', 'led_source', 'led_source_d1', 'led_source_USB']
    for i, name in enumerate(SOURCES):
        if not base.op(name):
            n = base.create(nullTOP, name)
            n.nodeX = i * 200
            n.nodeY = -600
            print(f"Created missing source: {name}")

    print(f"Successfully applied 4-source sender to {ex.path}")
    print("READY TO ACTIVATE: op('"+ex.path+"').par.active = True")

if __name__ == '__main__':
    run()
