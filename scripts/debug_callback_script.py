# debug_callback_script.py
# Read the data_texture_callbacks script content
scene = op('/AudioLinkLight_V01/SCENE_6')
if not scene: scene = op('SCENE_6')

cb = scene.op('data_texture_callbacks')
if not cb:
    print("data_texture_callbacks NOT FOUND")
else:
    print(f"Type: {type(cb).__name__}, OPType: {cb.OPType}")
    print(f"Content ({len(cb.text)} chars):")
    print("="*60)
    print(cb.text)
    print("="*60)
