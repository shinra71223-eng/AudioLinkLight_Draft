# find_source.py
out_file = 'c:/Users/0008112871/OneDrive - Sony/ドキュメント/AntiGravity/AudioLinkLight_Draft/find_source_result.txt'

with open(out_file, 'w', encoding='utf-8') as f:
    f.write("Searching for TOPs containing 'source' or 'USB'...\n\n")
    found = False
    for n in root.findChildren(type=TOP):
        name_lower = n.name.lower()
        if 'source' in name_lower or 'usb' in name_lower:
            f.write(f"PATH: {n.path}\n")
            found = True
    
    if not found:
        f.write("No matching TOPs found.\n")

print("Done. Results in find_source_result.txt")
