# dump_ramp_params.py
SCENE_PATH = '/AudioLinkLight_V01/SCENE_5'
scene = op(SCENE_PATH)
if not scene:
    scene = op('/')

print("="*60)
print("DUMPING ALL RAMP TOP PARAMETERS")
print("="*60)

ramp = scene.create(rampTOP, 'tmp_dump_ramp')
try:
    all_pars = ramp.pars('*')
    for p in all_pars:
        print(f"Name: {p.name:20} | Label: {p.label}")
finally:
    ramp.destroy()

print("="*60)
