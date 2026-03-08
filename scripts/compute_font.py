#!/usr/bin/env python3
"""Compute 4x8 bitmap font data for GLSL shader."""

# Font: 4 wide x 8 tall
# Encoding: bit_index = col + row * 4
# col: 0=left, 3=right
# row: 0=bottom, 7=top
# Rows listed top-to-bottom in definitions

CHARS = {
    '0': [".XX.","X..X","X..X","X..X","X..X","X..X","X..X",".XX."],
    '1': [".X..","XX..",".X..",".X..",".X..",".X..",".X..","XXX."],
    '2': [".XX.","X..X","...X","..X.",".X..","X...","X...","XXXX"],
    '3': ["XXXX","...X","..X.",".XX.","...X","...X","X..X",".XX."],
    '4': ["..X.",".XX.","X.X.","X.X.","XXXX","..X.","..X.","..X."],
    '5': ["XXXX","X...","XXX.","...X","...X","...X","X..X",".XX."],
    '6': [".XX.","X...","X...","XXX.","X..X","X..X","X..X",".XX."],
    '7': ["XXXX","...X","...X","..X.","..X.",".X..",".X..",".X.."],
    '8': [".XX.","X..X","X..X",".XX.","X..X","X..X","X..X",".XX."],
    '9': [".XX.","X..X","X..X",".XXX","...X","...X","..X.",".XX."],
    'A': [".XX.","X..X","X..X","X..X","XXXX","X..X","X..X","X..X"],
    'B': ["XXX.","X..X","X..X","XXX.","X..X","X..X","X..X","XXX."],
    'C': [".XX.","X..X","X...","X...","X...","X...","X..X",".XX."],
    'D': ["XXX.","X..X","X..X","X..X","X..X","X..X","X..X","XXX."],
    'E': ["XXXX","X...","X...","XXX.","X...","X...","X...","XXXX"],
    'F': ["XXXX","X...","X...","XXX.","X...","X...","X...","X..."],
    'G': [".XX.","X..X","X...","X...","X.XX","X..X","X..X",".XXX"],
    'H': ["X..X","X..X","X..X","XXXX","X..X","X..X","X..X","X..X"],
    'I': ["XXX.",".X..",".X..",".X..",".X..",".X..",".X..","XXX."],
    'K': ["X..X","X.X.","XX..","XX..","XX..","X.X.","X.X.","X..X"],
    'L': ["X...","X...","X...","X...","X...","X...","X...","XXXX"],
    'M': ["X..X","XXXX","XXXX","X..X","X..X","X..X","X..X","X..X"],
    'N': ["X..X","XX.X","XX.X","X.XX","X.XX","X..X","X..X","X..X"],
    'O': [".XX.","X..X","X..X","X..X","X..X","X..X","X..X",".XX."],
    'P': ["XXX.","X..X","X..X","XXX.","X...","X...","X...","X..."],
    'R': ["XXX.","X..X","X..X","XXX.","XX..","X.X.","X..X","X..X"],
    'S': [".XXX","X...","X...",".XX.","...X","...X","...X","XXX."],
    'T': ["XXXX",".XX.",".XX.",".XX.",".XX.",".XX.",".XX.",".XX."],
    'U': ["X..X","X..X","X..X","X..X","X..X","X..X","X..X",".XX."],
    'X': ["X..X","X..X",".XX.",".XX.",".XX.",".XX.","X..X","X..X"],
    '-': ["....","....","....","XXXX","....","....","....","...."],
    ' ': ["....","....","....","....","....","....","....","...."],
    '/': ["...X","...X","..X.","..X.",".X..",".X..","X...","X..."],
    '!': [".XX.",".XX.",".XX.",".XX.",".XX.","....",".XX.",".XX."],
    'J': ["..XX","..X.","..X.","..X.","..X.","..X.","X.X.",".X.."],
}

def encode(rows):
    val = 0
    for r_idx, row_str in enumerate(reversed(rows)):
        for c_idx, ch in enumerate(row_str):
            if ch == 'X':
                bit_idx = c_idx + r_idx * 4
                val |= (1 << bit_idx)
    return val

INDEX_MAP = "0123456789ABCDEFGHIKLMNOPRSTUX-! /J"
print("// 4x8 Bitmap Font Data (auto-generated)")
print(f"// Index: {INDEX_MAP}")
print()

vals = []
for i, ch in enumerate(INDEX_MAP):
    if ch in CHARS:
        v = encode(CHARS[ch])
        vals.append(v)
        print(f"//  [{i:2d}] '{ch}' = {v}")
    else:
        vals.append(0)
        print(f"//  [{i:2d}] '{ch}' = 0  (MISSING)")

print()
print(f"int fontData[{len(vals)}] = int[{len(vals)}](")
for i, v in enumerate(vals):
    ch = INDEX_MAP[i]
    comma = "," if i < len(vals) - 1 else ""
    print(f"    {v}{comma}  // {i}: '{ch}'")
print(");")
