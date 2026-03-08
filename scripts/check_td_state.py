# check_td_state.py
import td

print("=== TouchDesigner 2025 State Check ===")

root = op('/AudioLinkLight_V01')
if not root:
    print("Error: /AudioLinkLight_V01 not found.")
else:
    print(f"Root found: {root.path} (Type: {type(root)})")
    
    # Test parent behavior
    try:
        p_attr = root.parent
        print(f"root.parent type: {type(p_attr)}")
        print(f"root.parent has 'op': {hasattr(p_attr, 'op')}")
    except Exception as e:
        print(f"root.parent access error: {e}")

    try:
        p_func = root.parent()
        print(f"root.parent() type: {type(p_func)}")
        print(f"root.parent() has 'op': {hasattr(p_func, 'op')}")
    except Exception as e:
        print(f"root.parent() access error: {e}")

    # Check for DEPLOY_SCENES
    btn = root.op('DEPLOY_SCENES')
    if btn:
        print(f"Found DEPLOY_SCENES button: {btn.path}")
    else:
        print("DEPLOY_SCENES button not found yet.")

print("\n=== Check Complete ===")
