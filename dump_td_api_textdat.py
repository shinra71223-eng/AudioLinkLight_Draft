# dump_td_api_textdat.py
# Paste this into a Text DAT in TouchDesigner and run the DAT.
# It writes a Markdown API reference to the project's docs folder.

import os

def dump_api_textdat():
    try:
        # Determine output path inside the TouchDesigner project folder if available
        out_path = 'td_api_reference.md'
        try:
            pf = project.folder
        except NameError:
            pf = None

        if pf:
            docs_dir = os.path.join(pf, 'docs')
            if not os.path.exists(docs_dir):
                os.makedirs(docs_dir)
            out_path = os.path.join(docs_dir, 'td_api_reference.md')

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('# TouchDesigner API Reference\n\n')
            f.write('DO NOT GUESS PARAMETER NAMES. USE THIS REFERENCE.\n\n')

            f.write('## Base COMP / OP API\n\n')
            f.write('### Common OP Methods & Attributes\n')
            f.write('```python\n')

            # Use root as example COMP (available in Text DAT scope)
            comp_attrs = [a for a in dir(root) if not a.startswith('_')]
            for a in comp_attrs:
                try:
                    val = getattr(root, a)
                    if callable(val):
                        f.write(f'COMP.{a}()\n')
                    else:
                        f.write(f'COMP.{a} (type: {type(val).__name__})\n')
                except Exception:
                    pass
            f.write('```\n\n')

            f.write('## Node Parameter Reference\n\n')

            # Create a temporary COMP under root to instantiate example nodes
            temp_name = 'temp_api_dumper'
            # Destroy if exists
            if temp_name in [c.name for c in root.findChildren(depth=1)]:
                try:
                    root.op(temp_name).destroy()
                except Exception:
                    pass

            temp_comp = root.create(baseCOMP, temp_name)

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
                    # iterate visible parameters
                    for p in temp_node.pars():
                        try:
                            p_name = getattr(p, 'name', '')
                            p_label = getattr(p, 'label', '')
                            p_mode = getattr(p, 'mode', '')
                            p_val = getattr(p, 'val', '')
                            f.write(f'| `{p_name}` | {p_label} | {p_mode} | {p_val} |\n')
                        except Exception:
                            pass

                    # Node-specific attributes/methods
                    specific_attrs = [a for a in dir(temp_node) if not a.startswith('_') and a not in comp_attrs]
                    if specific_attrs:
                        f.write('\n**Node-specific methods/attributes:**\n')
                        f.write('`' + '`, `'.join(specific_attrs) + '`\n\n')

                    # clean up the temp node
                    try:
                        temp_node.destroy()
                    except Exception:
                        pass

                except Exception as e:
                    f.write(f'**Error creating {name}: {e}**\n\n')

            # destroy temp comp
            try:
                temp_comp.destroy()
            except Exception:
                pass

            f.write('## Enums\n\n')
            f.write('```python\n')
            f.write('ParMode.CONSTANT\n')
            f.write('ParMode.EXPRESSION\n')
            f.write('ParMode.EXPORT\n')
            f.write('```\n')

        print(f'API Reference dumped successfully to: {out_path}')

    except Exception as e:
        import traceback
        print(f'Error during execution: {e}')
        traceback.print_exc()

# Run when pasted into a Text DAT and executed
dump_api_textdat()
