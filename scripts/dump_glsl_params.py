import td

scene = op('/AudioLinkLight_V01/SCENE_6')
if scene:
    glsl = scene.op('glsl_baseball')
    if glsl:
        print("Parameters of glsl_baseball:")
        for p in glsl.pars():
            print(f"Name: {p.name}, Label: {p.label}, Page: {p.page.name}, Val: {p.val}")
