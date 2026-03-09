# find_u1_d1.py
out_file = 'c:/Users/0008112871/OneDrive - Sony/ドキュメント/AntiGravity/AudioLinkLight_Draft/find_u1_d1.txt'
with open(out_file, 'w', encoding='utf-8') as f:
    for n in root.findChildren(type=TOP):
        if n.name in ['led_source_u1', 'led_source_d1']:
            f.write(f"PATH: {n.path}\n")
print("Done")
