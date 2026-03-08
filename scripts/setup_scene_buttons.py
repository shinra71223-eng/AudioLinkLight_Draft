# setup_scene_buttons.py
# ================================================================
# Connects button1..6 in LED_OUTPUT to scene_select index.
# ================================================================
import td

led_out = op('/AudioLinkLight_V01/LED_OUTPUT')
if not led_out: led_out = op('LED_OUTPUT')

if not led_out:
    print("Error: LED_OUTPUT not found.")
else:
    scene_sel = led_out.op('scene_select')
    if not scene_sel:
        scene_sel = op('/AudioLinkLight_V01/scene_select') or op('/scene_select')
        
    if not scene_sel:
        print("Error: 'scene_select' operator not found!")
    else:
        # Create or update Panel Execute DAT
        pe = led_out.op('scene_btn_exec')
        if not pe:
            pe = led_out.create('panelexecuteDAT', 'scene_btn_exec')
            
        # Assign panels (the button COMPs to monitor)
        try: pe.par.panels = 'button1 button2 button3 button4 button5 button6'
        except: pass
        
        # Monitor the 'state' value
        try: pe.par.panelv = 'state'
        except:
            try: pe.par.panel = 'state'
            except: pass
        
        # Turn ON offToOn
        pe.par.offtoon = 1
        
        script_code = f"""def onOffToOn(panelValue):
    btn_name = panelValue.owner.name
    try:
        idx = int(btn_name.replace('button', ''))
        
        # Override expression if any, and set the integer value manually
        target_op = op('{scene_sel.path}')
        target_op.par.index.expr = ''
        target_op.par.index = idx - 1
        
        print(f"Switched scene to index {{idx-1}} via {{btn_name}}")
    except Exception as e:
        print(f"Error switching scene: {{e}}")
"""
        pe.text = script_code
        pe.nodeX = 400
        pe.nodeY = -200
        
        print(f"SUCCESS: Connected {pe.par.panels} to {scene_sel.path}'s index parameter!")
