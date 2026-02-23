# dump_glsl_errors_v3.py
import traceback
import os

try:
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    if glsl:
        info = op('/AudioLinkLight_V01/TEST_SCREEN2').create(infoDAT, 'temp_info_err')
        info.par.op = glsl.path
        
        err_msg = info.text
        out_path = os.path.join(project.folder, 'glsl_errors_test2.txt')
        
        with open(out_path, 'w', encoding='utf-8') as err_file:
            err_file.write(err_msg)
            
        print(f"Errors dumped to {out_path}")
        info.destroy()
    else:
        print('cyber_clock_v2 not found')
except Exception as e:
    traceback.print_exc()
