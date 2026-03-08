# find_format_param.py
import td

# Target node
glsl = op('/AudioLinkLight_V01/SCENE_6/glsl_baseball')

if glsl:
    print("\n--- Searching for Pixel Format parameters in glsl_baseball ---")
    
    found = False
    for p in glsl.pars():
        name = p.name.lower()
        label = p.label.lower()
        
        # 'format', 'pixel', 'color' が名前に含まれるパラメータを探す
        if 'format' in name or 'format' in label or 'pixel' in label:
            print(f"- [Par: {p.name}] Label: '{p.label}' (Page: {p.page.name}) | Current Value: {p.val}")
            if p.isMenu:
                print(f"  Menu Names: {p.menuNames}")
            found = True
            
    if not found:
        print("Could not find any parameter related to Pixel Format.")
        
    print("------------------------------------------------------------\n")
else:
    print("Node not found.")
