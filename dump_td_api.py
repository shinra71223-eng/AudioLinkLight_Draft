# dump_td_api.py
# Dumps TouchDesigner node types, parameter names, and core OP methods
# to a Markdown reference file so the AI stops guessing parameter names.

import os

def dump_api():
    try:
        out_path = 'td_api_reference.md'
        pf = project.folder
        if pf:
            out_path = pf + '/docs/td_api_reference.md'
            
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('# TouchDesigner API Reference\n\n')
            f.write('DO NOT GUESS PARAMETER NAMES. USE THIS REFERENCE.\n\n')

            # 1. Base COMP API (How to create/connect nodes)
            f.write('## Base COMP / OP API\n\n')
            f.write('### Common OP Methods & Attributes\n')
            f.write('```python\n')
            
            # Use root as an example COMP
            comp_attrs = [a for a in dir(root) if not a.startswith('_')]
            for a in comp_attrs:
                try:
                    val = getattr(root, a)
                    if callable(val):
                        f.write(f'COMP.{a}()\n')
                    else:
                        f.write(f'COMP.{a} (type: {type(val).__name__})\n')
                except:
                    pass
            f.write('```\n\n')

            # 2. Extract parameters for common node types by creating temp instances
            f.write('## Node Parameter Reference\n\n')
            
            temp_comp = root.create(baseCOMP, 'temp_api_dumper')
            
            nodes_to_check = {
                'noiseTOP': noiseTOP,
                'levelTOP': levelTOP,
                'circleTOP': circleTOP,
                'compositeTOP': compositeTOP,
                'resolutionTOP': resolutionTOP,
                'cropTOP': cropTOP,
                'crossTOP': crossTOP,
                'outTOP': outTOP,
                'selectTOP': selectTOP,
                'constantTOP': constantTOP,
                'selectCHOP': selectCHOP,
                'mathCHOP': mathCHOP,
                'mergeCHOP': mergeCHOP,
                'renameCHOP': renameCHOP,
                'switchCHOP': switchCHOP
            }
            
            for name, op_type in nodes_to_check.items():
                f.write(f'### {name}\n\n')
                f.write('| Parameter Name | Label | Mode | Value |\n')
                f.write('|---|---|---|---|\n')
                
                try:
                    temp_node = temp_comp.create(op_type, 'temp_' + name)
                    for p in temp_node.pars():
                        # p.name is the Python attribute name (e.g. 'resolutionw')
                        # p.label is the UI name (e.g. 'Resolution')
                        # p.val is the current value
                        # p.mode is the mode (constant, expression, export)
                        f.write(f'| `{p.name}` | {p.label} | {p.mode} | {p.val} |\n')
                    
                    # Also list specific attributes of the node object itself
                    specific_attrs = [a for a in dir(temp_node) if not a.startswith('_') and a not in comp_attrs]
                    if specific_attrs:
                        f.write('\n**Node-specific methods/attributes:**\n')
                        f.write('`' + '`, `'.join(specific_attrs) + '`\n\n')
                        
                except Exception as e:
                    f.write(f'**Error creating {name}: {e}**\n\n')
            
            temp_comp.destroy()
            
            f.write('## Enums\n\n')
            f.write('```python\n')
            f.write('ParMode.CONSTANT\n')
            f.write('ParMode.EXPRESSION\n')
            f.write('ParMode.EXPORT\n')
            f.write('```\n')

        print(f'API Reference dumped successfully to: {out_path}')

    except Exception as e:
        import traceback
        print(f"Error during execution: {e}")
        traceback.print_exc()

dump_api()
