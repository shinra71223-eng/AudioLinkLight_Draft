# find_project_root.py
import td
print("=== Project Root Search ===")

# 1. Check for AudioLinkLight_V01 globally
all_comps = root.findChildren(type=containerCOMP, name='AudioLinkLight_V01', maxDepth=3)
if all_comps:
    for c in all_comps:
        print(f"Found: {c.path}")
else:
    print("AudioLinkLight_V01 not found at root level.")
    # Try searching for any container that might be the root
    potential = root.findChildren(type=containerCOMP, name='AudioLink*', maxDepth=2)
    for p in potential:
        print(f"Potential Root: {p.path}")

# 2. Check current operator parent
# If the user is running from a specific network context
print(f"Current project: {project.name}")
print(f"Project folder: {project.folder}")

print("=== Search Complete ===")
