# check_td_env.py
import td

print("=== TouchDesigner Environment Check ===")

def check_symbol(name):
    try:
        val = globals().get(name) or getattr(td, name, None)
        print(f"{name}: {val} (Type: {type(val)})")
    except Exception as e:
        print(f"{name}: Error: {e}")

symbols = [
    'selectTOP', 'nullTOP', 'glslTOP', 'dattoTOP', 'textDAT', 'tableDAT',
    'rectangleTOP', 'compositeTOP', 'baseCOMP', 'project'
]

for s in symbols:
    check_symbol(s)

print("\n--- Testing create() methods ---")
test_base = op('/AudioLinkLight_V01').create(baseCOMP, 'env_test_base')
try:
    # Test string with family
    t1 = test_base.create('selectTOP', 'test_sel_str_family')
    print("create('selectTOP'): SUCCESS")
    t1.destroy()
except Exception as e:
    print(f"create('selectTOP'): FAILED - {e}")

try:
    # Test string without family
    t2 = test_base.create('select', 'test_sel_str')
    print("create('select'): SUCCESS")
    t2.destroy()
except Exception as e:
    print(f"create('select'): FAILED - {e}")

try:
    # Test class
    t3 = test_base.create(selectTOP, 'test_sel_class')
    print("create(selectTOP): SUCCESS")
    t3.destroy()
except Exception as e:
    print(f"create(selectTOP): FAILED - {e}")

test_base.destroy()
print("=== Check Complete ===")
