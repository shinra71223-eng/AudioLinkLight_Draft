# scripts/find_screen.py
import traceback

try:
    print("--- Searching for TEST_SCREEN or polish_test ---")
    
    # ユーザーのプロジェクト全体から名前で検索
    found = op('/').findChildren(type=COMP, tags=[]) # type縛りを緩くして全検索
    
    results = []
    for comp in found:
        path_lower = comp.path.lower()
        if 'test' in path_lower or 'screen' in path_lower or 'polish' in path_lower:
            results.append(comp.path)
            
    if results:
        print("Found matching paths:")
        for r in results:
            print(f"  {r}")
    else:
        print("No matching paths found containing 'test', 'screen', or 'polish'.")
        
except Exception as e:
    print(f"Error during search: {e}")
    traceback.print_exc()
