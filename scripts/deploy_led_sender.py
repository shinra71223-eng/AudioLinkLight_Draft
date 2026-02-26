# deploy_led_sender.py
# Run in TD Textport:
#   exec(open(project.folder + '/scripts/deploy_led_sender.py', encoding='utf-8').read())
#
# Creates/updates led_exec Execute DAT inside TEST_SCREEN with pyserial-based sender.
# Also ensures led_source Null TOP exists.

TARGET = '/AudioLinkLight_V01/TEST_SCREEN'

base = op(TARGET)
if base is None:
    print(f'[ERROR] {TARGET} not found')
else:
    # ---- led_exec: Execute DAT with pyserial sender ----
    dat_name = 'led_exec'
    d = base.op(dat_name)
    if d is not None:
        d.par.active = False
        d.destroy()

    d = base.create(executeDAT, dat_name)
    d.par.framestart = True
    d.par.active = False  # start inactive - user turns on manually

    # Load script content
    script_path = project.folder + '/scripts/dats/led_sender_pyserial.py'
    with open(script_path, encoding='utf-8') as f:
        d.text = f.read()

    d.nodeX = 400
    d.nodeY = 0

    # ---- led_source: Null TOP (if not exists) ----
    src = base.op('led_source')
    if src is None:
        src = base.create(nullTOP, 'led_source')
        src.nodeX = 200
        src.nodeY = 0

    # ---- pat_noise: test pattern (if not exists) ----
    noise = base.op('pat_noise')
    if noise is None:
        noise = base.create(noiseTOP, 'pat_noise')
        noise.par.resx = 88
        noise.par.resy = 10
        noise.par.mono = False
        noise.nodeX = 0
        noise.nodeY = 0

    print('=' * 50)
    print('[deploy_led_sender] Done!')
    print(f'  led_exec   : created (active=False)')
    print(f'  led_source : {"exists" if base.op("led_source") else "created"}')
    print()
    print('Next steps:')
    print('  1. Connect a TOP to led_source (e.g. pat_noise)')
    print('  2. Activate:')
    print("     op('" + TARGET + "/led_exec').par.active = True")
    print('  3. Stop:')
    print("     op('" + TARGET + "/led_exec').run('stop')")
    print('  4. Manual test:')
    print("     op('" + TARGET + "/led_exec').run('test_solid', 200, 0, 0)")
    print('=' * 50)
