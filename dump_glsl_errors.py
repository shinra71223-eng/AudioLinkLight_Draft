# dump_glsl_errors.py
import traceback
try:
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN/cyber_clock')
    if glsl:
        info = op('/AudioLinkLight_V01/TEST_SCREEN').create(infoDAT, 'temp_info_err')
        info.par.op = glsl.path
        with open(project.folder + '/glsl_errors_2.txt', 'w', encoding='utf-8') as err_file:
            err_file.write(info.text)
        print('Errors dumped to glsl_errors_2.txt')
        info.destroy()
    else:
        print('cyber_clock not found')
except Exception as e:
    print(e)
