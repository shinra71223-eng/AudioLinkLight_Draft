# check_hierarchy.py
# Dumps the paths of nodes inside AudioLinkLight_V01 to verify relative paths.

def check():
    core = None
    for comp in root.findChildren(type=COMP):
        if 'AudioLinkLight_V' in comp.name:
            core = comp
            break
    if not core:
        print('ERROR: AudioLinkLight not found')
        return

    print(f'=== Children of {core.path} ===')
    for child in core.findChildren(depth=1):
        print(f'  {child.name} (type: {child.OPType})')
        if child.name == 'AudioLinkCore':
            # Check outputs of AudioLinkCore
            for out in child.findChildren(type=outCHOP, depth=1):
                print(f'    -> found outCHOP: {out.path}')

check()
