# debug_creation.py
import td
from td import glslTOP

scene_path = '/AudioLinkLight_V01/SCENE_6'
scene = op(scene_path)
if not scene: scene = op('SCENE_6')

print(f"--- Diagnostic for {scene_path} ---")
if not scene:
    print("CRITICAL: SCENE_6 not found!")
else:
    print(f"Scene found: {scene.path}")
    print(f"Scene type: {type(scene)}")
    
    test_name = 'glsl_test_node'
    print(f"Attempting to create {test_name}...")
    try:
        # Method 1
        node1 = scene.create(glslTOP, test_name + '1')
        print(f"Method 1 (glslTOP): {node1}")
        
        # Method 2
        node2 = scene.create('glsl', test_name + '2')
        print(f"Method 2 ('glsl'): {node2}")
        
        if node1: node1.destroy()
        if node2: node2.destroy()
    except Exception as e:
        print(f"Creation failed with error: {e}")
