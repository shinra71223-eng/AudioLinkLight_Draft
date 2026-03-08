# diagnose_text_op.py
import td

print("=== Operator Type Ambiguity Diagnosis ===")

def test_create(parent, type_str):
    print(f"\nTesting: create('{type_str}')")
    try:
        tmp_name = f"diag_{type_str}_tmp"
        existing = parent.op(tmp_name)
        if existing: existing.destroy()
        
        node = parent.create(type_str, tmp_name)
        print(f"  SUCCESS: Created {node.type} ({type(node)})")
        
        # Check if it has .text (DAT characteristic)
        if hasattr(node, 'text'):
            print("  HAS .text attribute (likely a DAT)")
        else:
            print("  NO .text attribute (likely a TOP/CHOP/SOP)")
            
        node.destroy()
    except Exception as e:
        print(f"  FAILED: {e}")

root = op('/AudioLinkLight_V01')
if not root:
    print("Error: /AudioLinkLight_V01 not found.")
else:
    # Test common ambiguous names
    test_create(root, 'text')
    test_create(root, 'textDAT')
    test_create(root, 'textTOP')
    test_create(root, 'null')
    test_create(root, 'nullTOP')
    test_create(root, 'nullDAT')
    test_create(root, 'select')
    test_create(root, 'selectTOP')
    test_create(root, 'selectDAT')
    test_create(root, 'datto')
    test_create(root, 'dattoTOP')
    test_create(root, 'datToTOP')

print("\n=== Check Complete ===")
