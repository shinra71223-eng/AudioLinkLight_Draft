# check_glsl_error.py
def check():
    glsl = op('/AudioLinkLight_V01/SCENE_6/glsl_baseball')
    if glsl:
        print("GLSL TOP: ", glsl.path)
        print("Errors: ", glsl.errors())
        print("Warnings: ", glsl.warnings())
        # Also check the info DAT if it exists
        info = op('/AudioLinkLight_V01/SCENE_6/glsl_baseball_info')
        if info:
            print("Info DAT content: ", info.text if hasattr(info, 'text') else 'N/A')
    else:
        print("glsl_baseball not found")

if __name__ == '__main__':
    check()
