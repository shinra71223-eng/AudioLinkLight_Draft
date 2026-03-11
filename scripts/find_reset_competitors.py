# find_reset_competitors.py
print("\n--- SEARCHING FOR COMPETING RESET SCRIPTS ---")

# 1. Search for text content
for n in root.findChildren(type=DAT):
    if n.isDAT and n.text and 'led_exec_multi' in n.text:
        print(f"MATCH (text): {n.path}")

# 2. Search for references to RESET_Button
target_btn = op('/AudioLinkLight_V01/LED_OUTPUT/RESET_Button')
if target_btn:
    for n in root.findChildren(type=panelexecuteDAT):
        if n.par.panel == target_btn.path or n.par.panel == target_btn:
            if n.name != 'reset_logic':
                print(f"MATCH (reference): {n.path}")

print("--- SEARCH COMPLETE ---")
