# TouchDesigner API Reference

DO NOT GUESS PARAMETER NAMES. USE THIS REFERENCE.

## Base COMP / OP API

### Common OP Methods & Attributes
```python
COMP.OPType (type: str)
COMP.accessPrivateContents()
COMP.activeViewer (type: bool)
COMP.addError()
COMP.addPrivacy()
COMP.addScriptError()
COMP.addWarning()
COMP.allowCooking (type: bool)
COMP.appendCustomPage()
COMP.asType()
COMP.base (type: str)
COMP.blockPrivateContents()
COMP.builtinPars (type: list)
COMP.bypass (type: bool)
COMP.changeType()
COMP.children (type: list)
COMP.childrenCPUCookAbsFrame (type: int)
COMP.childrenCPUCookTime (type: float)
COMP.childrenCPUMemory()
COMP.childrenCookAbsFrame (type: int)
COMP.childrenCookTime (type: float)
COMP.childrenGPUCookAbsFrame (type: int)
COMP.childrenGPUCookTime (type: float)
COMP.childrenGPUMemory()
COMP.clearScriptErrors()
COMP.cloneImmune (type: bool)
COMP.clones (type: list)
COMP.closeViewer()
COMP.collapseSelected()
COMP.color (type: tuple)
COMP.comment (type: str)
COMP.componentCloneImmune (type: bool)
COMP.cook()
COMP.cookAbsFrame (type: int)
COMP.cookEndTime (type: float)
COMP.cookFrame (type: float)
COMP.cookStartTime (type: float)
COMP.cookTime (type: float)
COMP.cookedPreviousFrame (type: bool)
COMP.cookedThisFrame (type: bool)
COMP.copy()
COMP.copyOPs()
COMP.copyParameters()
COMP.cpuCookTime (type: float)
COMP.cpuMemory (type: int)
COMP.create()
COMP.curBlock (type: NoneType)
COMP.curPar (type: NoneType)
COMP.curSeq (type: NoneType)
COMP.current (type: bool)
COMP.currentChild (type: containerCOMP)
COMP.currentPage (type: Page)
COMP.customPages (type: PageList)
COMP.customParGroups (type: list)
COMP.customPars (type: list)
COMP.customTuplets (type: list)
COMP.dependenciesTo()
COMP.destroy()
COMP.destroyCustomPars()
COMP.digits (type: NoneType)
COMP.dirty (type: bool)
COMP.display (type: bool)
COMP.dock (type: NoneType)
COMP.docked (type: list)
COMP.errors()
COMP.evalExpression()
COMP.expose (type: bool)
COMP.ext (type: Ext)
COMP.extensions (type: list)
COMP.extensionsReady (type: bool)
COMP.externalTimeStamp (type: int)
COMP.family (type: str)
COMP.fetch()
COMP.fetchOwner()
COMP.fileFolder (type: str)
COMP.filePath (type: str)
COMP.findChildren()
COMP.gpuCookTime (type: float)
COMP.gpuMemory (type: int)
COMP.icon (type: str)
COMP.id (type: int)
COMP.initializeExtensions()
COMP.inputCOMPConnectors (type: list)
COMP.inputCOMPs (type: list)
COMP.inputConnectors (type: list)
COMP.inputs (type: list)
COMP.internalOPs (type: dict)
COMP.internalPars (type: dict)
COMP.iop()
COMP.ipar()
COMP.isBase (type: bool)
COMP.isCHOP (type: bool)
COMP.isCOMP (type: bool)
COMP.isCustom (type: bool)
COMP.isDAT (type: bool)
COMP.isFilter (type: bool)
COMP.isMAT (type: bool)
COMP.isMultiInputs (type: bool)
COMP.isObject (type: bool)
COMP.isPOP (type: bool)
COMP.isPanel (type: bool)
COMP.isPrivacyActive (type: bool)
COMP.isPrivacyLicensed (type: bool)
COMP.isPrivate (type: bool)
COMP.isSOP (type: bool)
COMP.isTOP (type: bool)
COMP.label (type: str)
COMP.layout()
COMP.licenseType (type: str)
COMP.loadByteArray()
COMP.loadTox()
COMP.lock (type: bool)
COMP.maxInputs (type: int)
COMP.minInputs (type: int)
COMP.mod()
COMP.name (type: str)
COMP.nodeCenterX (type: int)
COMP.nodeCenterY (type: int)
COMP.nodeHeight (type: int)
COMP.nodeWidth (type: int)
COMP.nodeX (type: int)
COMP.nodeY (type: int)
COMP.numChildren (type: int)
COMP.numChildrenRecursive (type: int)
COMP.op()
COMP.opType (type: str)
COMP.openMenu()
COMP.openParameters()
COMP.openViewer()
COMP.opex()
COMP.ops()
COMP.outputCOMPConnectors (type: list)
COMP.outputCOMPs (type: list)
COMP.outputConnectors (type: list)
COMP.outputs (type: list)
COMP.pages (type: PageList)
COMP.par (type: ParCollection)
COMP.parGroup (type: ParGroupCollection)
COMP.parGroups()
COMP.parent()
COMP.pars()
COMP.passive (type: bool)
COMP.path (type: str)
COMP.pickable (type: bool)
COMP.privacyDeveloperEmail (type: str)
COMP.privacyDeveloperName (type: str)
COMP.privacyFirmCode (type: int)
COMP.privacyProductCode (type: int)
COMP.progressiveUnload()
COMP.progressiveUnloader (type: ProgressiveUnloader)
COMP.python (type: bool)
COMP.recursiveChildren (type: int)
COMP.relativePath()
COMP.reload()
COMP.removePrivacy()
COMP.render (type: bool)
COMP.replicator (type: NoneType)
COMP.resetNetworkView()
COMP.resetNodeSize()
COMP.resetPars()
COMP.resetViewer()
COMP.save()
COMP.saveByteArray()
COMP.saveExternalTox()
COMP.scriptErrors()
COMP.selected (type: bool)
COMP.selectedChildren (type: list)
COMP.seq (type: SequenceCollection)
COMP.setInputs()
COMP.setVar()
COMP.shortcutPath()
COMP.showCustomOnly (type: bool)
COMP.showDocked (type: bool)
COMP.sortCustomPages()
COMP.storage (type: dict)
COMP.store()
COMP.storeStartupValue()
COMP.subType (type: str)
COMP.supported (type: int)
COMP.tags (type: DependSet)
COMP.time (type: timeCOMP)
COMP.totalCooks (type: int)
COMP.type (type: str)
COMP.unload()
COMP.unsetVar()
COMP.unstore()
COMP.unstoreStartupValue()
COMP.valid (type: bool)
COMP.var()
COMP.vars()
COMP.vfs (type: VFS)
COMP.viewer (type: bool)
COMP.visibleLevel (type: int)
COMP.warnings()
```

## Node Parameter Reference

### noiseTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `type` | Type | ParMode.CONSTANT | simplex3d |
| `seed` | Seed | ParMode.CONSTANT | 1.0 |
| `period` | Period | ParMode.CONSTANT | 1.0 |
| `harmon` | Harmonics | ParMode.CONSTANT | 2 |
| `spread` | Harmonic Spread | ParMode.CONSTANT | 2.0 |
| `gain` | Harmonic Gain | ParMode.CONSTANT | 0.7 |
| `rough` | Roughness | ParMode.CONSTANT | 0.5 |
| `exp` | Exponent | ParMode.CONSTANT | 1.0 |
| `amp` | Amplitude | ParMode.CONSTANT | 0.5 |
| `offset` | Offset | ParMode.CONSTANT | 0.5 |
| `mono` | Monochrome | ParMode.CONSTANT | True |
| `aspectcorrect` | Aspect Correct | ParMode.CONSTANT | True |
| `xord` | Transform Order | ParMode.CONSTANT | srt |
| `rord` | Rotate Order | ParMode.CONSTANT | xyz |
| `tx` | Translate | ParMode.CONSTANT | 0.0 |
| `ty` | Translate | ParMode.CONSTANT | 0.0 |
| `tz` | Translate | ParMode.CONSTANT | 0.0 |
| `rx` | Rotate | ParMode.CONSTANT | 0.0 |
| `ry` | Rotate | ParMode.CONSTANT | 0.0 |
| `rz` | Rotate | ParMode.CONSTANT | 0.0 |
| `sx` | Scale | ParMode.CONSTANT | 1.0 |
| `sy` | Scale | ParMode.CONSTANT | 1.0 |
| `sz` | Scale | ParMode.CONSTANT | 1.0 |
| `px` | Pivot | ParMode.CONSTANT | 0.0 |
| `py` | Pivot | ParMode.CONSTANT | 0.0 |
| `pz` | Pivot | ParMode.CONSTANT | 0.0 |
| `t4d` | Translate 4D | ParMode.CONSTANT | 0.0 |
| `s4d` | Scale 4D | ParMode.CONSTANT | 1.0 |
| `rgb` | RGB | ParMode.CONSTANT | add |
| `inputscale` | Input Scale | ParMode.CONSTANT | 1.0 |
| `noisescale` | Noise Scale | ParMode.CONSTANT | 1.0 |
| `alpha` | Alpha | ParMode.CONSTANT | one |
| `dither` | Dither | ParMode.CONSTANT | False |
| `gradient` | Gradient | ParMode.CONSTANT | False |
| `mode` | Mode | ParMode.CONSTANT | performance |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | resolution |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### levelTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `clampinput` | Clamp Input | ParMode.CONSTANT | automatic |
| `invert` | Invert | ParMode.CONSTANT | 0.0 |
| `blacklevel` | Black Level | ParMode.CONSTANT | 0.0 |
| `brightness1` | Brightness 1 | ParMode.CONSTANT | 1.0 |
| `gamma1` | Gamma 1 | ParMode.CONSTANT | 1.0 |
| `contrast` | Contrast | ParMode.CONSTANT | 1.0 |
| `inlow` | In Low | ParMode.CONSTANT | 0.0 |
| `inhigh` | In High | ParMode.CONSTANT | 1.0 |
| `outlow` | Out Low | ParMode.CONSTANT | 0.0 |
| `outhigh` | Out High | ParMode.CONSTANT | 1.0 |
| `lowr` | Low R | ParMode.CONSTANT | 0.0 |
| `highr` | High R | ParMode.CONSTANT | 1.0 |
| `lowg` | Low G | ParMode.CONSTANT | 0.0 |
| `highg` | High G | ParMode.CONSTANT | 1.0 |
| `lowb` | Low B | ParMode.CONSTANT | 0.0 |
| `highb` | High B | ParMode.CONSTANT | 1.0 |
| `lowa` | Low A | ParMode.CONSTANT | 0.0 |
| `higha` | High A | ParMode.CONSTANT | 1.0 |
| `stepping` | Apply Stepping | ParMode.CONSTANT | False |
| `stepsize` | Step Size | ParMode.CONSTANT | 0.0 |
| `threshold` | Threshold | ParMode.CONSTANT | 0.0 |
| `clamplow` | Clamp Low | ParMode.CONSTANT | 0.0 |
| `clamphigh` | Clamp High | ParMode.CONSTANT | 1.0 |
| `soften` | Soften | ParMode.CONSTANT | 0.0 |
| `gamma2` | Gamma 2 | ParMode.CONSTANT | 1.0 |
| `opacity` | Opacity | ParMode.CONSTANT | 1.0 |
| `brightness2` | Brightness 2 | ParMode.CONSTANT | 1.0 |
| `clamp` | Clamp | ParMode.CONSTANT | False |
| `clamplow2` | Clamp Low | ParMode.CONSTANT | 0.0 |
| `clamphigh2` | Clamp High | ParMode.CONSTANT | 1.0 |
| `premultrgbbyalpha` | Pre-Multiply RGB by Alpha | ParMode.CONSTANT | False |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### circleTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `radiusx` | Radius | ParMode.CONSTANT | 0.4 |
| `radiusy` | Radius | ParMode.CONSTANT | 0.4 |
| `radiusunit` | Radius Unit | ParMode.CONSTANT | fractionaspect |
| `rotate` | Rotate | ParMode.CONSTANT | 0.0 |
| `centerx` | Center | ParMode.CONSTANT | 0.0 |
| `centery` | Center | ParMode.CONSTANT | 0.0 |
| `centerunit` | Center Unit | ParMode.CONSTANT | fraction |
| `justifyh` | Justify Horizontal | ParMode.CONSTANT | center |
| `justifyv` | Justify Vertical | ParMode.CONSTANT | center |
| `fillcolorr` | Fill Color | ParMode.CONSTANT | 1.0 |
| `fillcolorg` | Fill Color | ParMode.CONSTANT | 1.0 |
| `fillcolorb` | Fill Color | ParMode.CONSTANT | 1.0 |
| `fillalpha` | Fill Alpha | ParMode.CONSTANT | 1.0 |
| `borderr` | Border Color | ParMode.CONSTANT | 0.0 |
| `borderg` | Border Color | ParMode.CONSTANT | 0.0 |
| `borderb` | Border Color | ParMode.CONSTANT | 0.0 |
| `borderalpha` | Border Alpha | ParMode.CONSTANT | 1.0 |
| `bgcolorr` | Background Color | ParMode.CONSTANT | 0.0 |
| `bgcolorg` | Background Color | ParMode.CONSTANT | 0.0 |
| `bgcolorb` | Background Color | ParMode.CONSTANT | 0.0 |
| `bgalpha` | Background Alpha | ParMode.CONSTANT | 0.0 |
| `premultrgbbyalpha` | Pre-Multiply RGB by Alpha | ParMode.CONSTANT | True |
| `borderwidth` | Border Width | ParMode.CONSTANT | 0.0 |
| `borderwidthunit` | Border Width Unit | ParMode.CONSTANT | fraction |
| `borderoffset` | Border Offset | ParMode.CONSTANT | 0.0 |
| `beginarcangle` | Arc Angles | ParMode.CONSTANT | 0.0 |
| `endarcangle` | Arc Angles | ParMode.CONSTANT | 0.0 |
| `antialias` | Anti-Alias | ParMode.CONSTANT | True |
| `ispolygon` | Polygon | ParMode.CONSTANT | False |
| `sides` | Sides | ParMode.CONSTANT | 3 |
| `softness` | Softness | ParMode.CONSTANT | 0.0 |
| `softnessunit` | Softness Unit | ParMode.CONSTANT | fractionaspect |
| `softnessoffset` | Softness Offset | ParMode.CONSTANT | 0.0 |
| `softnesstype` | Softness Type | ParMode.CONSTANT | halfcosine |
| `combineinput` | Combine with Input | ParMode.CONSTANT | compres |
| `operand` | Operation | ParMode.CONSTANT | over |
| `swaporder` | Swap Order | ParMode.CONSTANT | False |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### compositeTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `tops` | TOPs | ParMode.CONSTANT |  |
| `previewgrid` | Preview Grid | ParMode.CONSTANT | False |
| `selectinput` | Select Input | ParMode.CONSTANT | False |
| `inputindex` | Input Index | ParMode.CONSTANT | 0 |
| `operand` | Operation | ParMode.CONSTANT | multiply |
| `swaporder` | Swap Operation Order | ParMode.CONSTANT | False |
| `size` | Fixed Layer | ParMode.CONSTANT | input2 |
| `prefit` | Pre-Fit Overlay | ParMode.CONSTANT | fill |
| `justifyh` | Justify Horizontal | ParMode.CONSTANT | center |
| `justifyv` | Justify Vertical | ParMode.CONSTANT | center |
| `extend` | Extend Overlay | ParMode.CONSTANT | zero |
| `r` | Rotate | ParMode.CONSTANT | 0.0 |
| `tx` | Translate | ParMode.CONSTANT | 0.0 |
| `ty` | Translate | ParMode.CONSTANT | 0.0 |
| `tunit` | Translate Units | ParMode.CONSTANT | fraction |
| `sx` | Scale | ParMode.CONSTANT | 1.0 |
| `sy` | Scale | ParMode.CONSTANT | 1.0 |
| `px` | Pivot | ParMode.CONSTANT | 0.5 |
| `py` | Pivot | ParMode.CONSTANT | 0.5 |
| `punit` | Pivot Units | ParMode.CONSTANT | fraction |
| `tstepx` | Translate Step | ParMode.CONSTANT | 0.0 |
| `tstepy` | Translate Step | ParMode.CONSTANT | 0.0 |
| `tstepunit` | Translate Step Units | ParMode.CONSTANT | fraction |
| `legacyxform` | Legacy Transform | ParMode.CONSTANT | False |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `convertLegacyOperand`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### resolutionTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `highqualresize` | High Quality Resize | ParMode.CONSTANT | False |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### cropTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `cropleft` | Crop Left | ParMode.CONSTANT | 0.0 |
| `cropleftunit` | Crop Left Unit | ParMode.CONSTANT | fraction |
| `cropright` | Crop Right | ParMode.CONSTANT | 1.0 |
| `croprightunit` | Crop Right Unit | ParMode.CONSTANT | fraction |
| `cropbottom` | Crop Bottom | ParMode.CONSTANT | 0.0 |
| `cropbottomunit` | Crop Bottom Unit | ParMode.CONSTANT | fraction |
| `croptop` | Crop Top | ParMode.CONSTANT | 1.0 |
| `croptopunit` | Crop Top Unit | ParMode.CONSTANT | fraction |
| `extend` | Extend | ParMode.CONSTANT | repeat |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### crossTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `cross` | Cross | ParMode.CONSTANT | 0.5 |
| `size` | Fixed Layer | ParMode.CONSTANT | input2 |
| `prefit` | Pre-Fit Overlay | ParMode.CONSTANT | fill |
| `justifyh` | Justify Horizontal | ParMode.CONSTANT | center |
| `justifyv` | Justify Vertical | ParMode.CONSTANT | center |
| `extend` | Extend Overlay | ParMode.CONSTANT | zero |
| `r` | Rotate | ParMode.CONSTANT | 0.0 |
| `tx` | Translate | ParMode.CONSTANT | 0.0 |
| `ty` | Translate | ParMode.CONSTANT | 0.0 |
| `tunit` | Translate Unit | ParMode.CONSTANT | fraction |
| `sx` | Scale | ParMode.CONSTANT | 1.0 |
| `sy` | Scale | ParMode.CONSTANT | 1.0 |
| `px` | Pivot | ParMode.CONSTANT | 0.5 |
| `py` | Pivot | ParMode.CONSTANT | 0.5 |
| `punit` | Pivot Unit | ParMode.CONSTANT | fraction |
| `legacyxform` | Legacy Transform | ParMode.CONSTANT | False |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### outTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `selecttop` | Select TOP | ParMode.CONSTANT |  |
| `label` | Label | ParMode.EXPRESSION |  |
| `connectorder` | Connect Order | ParMode.CONSTANT | 0.0 |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### selectTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `top` | TOP | ParMode.CONSTANT |  |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### constantTOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `colorr` | Color | ParMode.CONSTANT | 1.0 |
| `colorg` | Color | ParMode.CONSTANT | 1.0 |
| `colorb` | Color | ParMode.CONSTANT | 1.0 |
| `alpha` | Alpha | ParMode.CONSTANT | 1.0 |
| `premultrgbbyalpha` | Pre-Multiply RGB by Alpha | ParMode.CONSTANT | True |
| `rgbaunit` | RGBA Units | ParMode.CONSTANT | u1 |
| `combineinput` | Combine with Input | ParMode.CONSTANT | compres |
| `operand` | Operation | ParMode.CONSTANT | multiply |
| `swaporder` | Swap Order | ParMode.CONSTANT | False |
| `outputresolution` | Output Resolution | ParMode.CONSTANT | useinput |
| `resolutionw` | Resolution | ParMode.CONSTANT | 256 |
| `resolutionh` | Resolution | ParMode.CONSTANT | 256 |
| `resmult` | Use Global Res Multiplier | ParMode.CONSTANT | True |
| `outputaspect` | Output Aspect | ParMode.CONSTANT | useinput |
| `aspect1` | Aspect | ParMode.CONSTANT | 1.0 |
| `aspect2` | Aspect | ParMode.CONSTANT | 1.0 |
| `inputfiltertype` | Input Smoothness | ParMode.CONSTANT | linear |
| `fillmode` | Fill Viewer | ParMode.CONSTANT | best |
| `filtertype` | Viewer Smoothness | ParMode.CONSTANT | linear |
| `npasses` | Passes | ParMode.CONSTANT | 1 |
| `chanmask` | Channel Mask | ParMode.CONSTANT | 15 |
| `format` | Pixel Format | ParMode.CONSTANT | useinput |
| `parmcolorspace` | Parameter Color Space | ParMode.CONSTANT | srgb |
| `parmreferencewhite` | Parameter Reference White | ParMode.CONSTANT | default |

**Node-specific methods/attributes:**
`aspect`, `aspectHeight`, `aspectWidth`, `cudaMemory`, `curPass`, `depth`, `height`, `newestSliceWOffset`, `numpyArray`, `pixelFormat`, `pixelFormatName`, `sample`, `width`

### selectCHOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `chops` | CHOPs | ParMode.CONSTANT |  |
| `channames` | Channel Names | ParMode.CONSTANT | * |
| `renamefrom` | Rename from | ParMode.CONSTANT | * |
| `renameto` | Rename to | ParMode.CONSTANT |  |
| `filterdigits` | Filter by Digits | ParMode.CONSTANT | False |
| `digits` | Digits | ParMode.CONSTANT | 0 |
| `stripdigits` | Strip Digits | ParMode.CONSTANT | True |
| `align` | Align | ParMode.CONSTANT | auto |
| `autoprefix` | Automatic Prefix | ParMode.CONSTANT | True |
| `timeslice` | Time Slice | ParMode.CONSTANT | False |
| `scope` | Scope | ParMode.CONSTANT | * |
| `srselect` | Sample Rate Match | ParMode.CONSTANT | max |
| `exportmethod` | Export Method | ParMode.CONSTANT | datindex |
| `autoexportroot` | Export Root | ParMode.EXPRESSION |  |
| `exporttable` | Export Table | ParMode.CONSTANT |  |

**Node-specific methods/attributes:**
`chan`, `chans`, `convertToKeyframes`, `end`, `export`, `exportChanges`, `isTimeSlice`, `numChans`, `numSamples`, `numpyArray`, `rate`, `start`

### mathCHOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `preop` | Channel Pre OP | ParMode.CONSTANT | off |
| `chanop` | Combine Channels | ParMode.CONSTANT | off |
| `chopop` | Combine CHOPs | ParMode.CONSTANT | off |
| `postop` | Channel Post OP | ParMode.CONSTANT | off |
| `match` | Match by | ParMode.CONSTANT | index |
| `align` | Align | ParMode.CONSTANT | auto |
| `interppars` | Interp Pars per Sample | ParMode.CONSTANT | False |
| `integer` | Integer | ParMode.CONSTANT | off |
| `preoff` | Pre-Add | ParMode.CONSTANT | 0.0 |
| `gain` | Multiply | ParMode.CONSTANT | 1.0 |
| `postoff` | Post-Add | ParMode.CONSTANT | 0.0 |
| `fromrange1` | From Range | ParMode.CONSTANT | 0.0 |
| `fromrange2` | From Range | ParMode.CONSTANT | 1.0 |
| `torange1` | To Range | ParMode.CONSTANT | 0.0 |
| `torange2` | To Range | ParMode.CONSTANT | 1.0 |
| `timeslice` | Time Slice | ParMode.CONSTANT | False |
| `scope` | Scope | ParMode.CONSTANT | * |
| `srselect` | Sample Rate Match | ParMode.CONSTANT | max |
| `exportmethod` | Export Method | ParMode.CONSTANT | datindex |
| `autoexportroot` | Export Root | ParMode.EXPRESSION |  |
| `exporttable` | Export Table | ParMode.CONSTANT |  |
| `renamefrom` | Rename from | ParMode.CONSTANT | * |
| `renameto` | Rename to | ParMode.CONSTANT |  |

**Node-specific methods/attributes:**
`chan`, `chanIndex`, `chans`, `convertToKeyframes`, `end`, `export`, `exportChanges`, `isTimeSlice`, `numChans`, `numSamples`, `numpyArray`, `rate`, `sampleIndex`, `start`

### mergeCHOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `align` | Align | ParMode.CONSTANT | auto |
| `duplicate` | Duplicate Names | ParMode.CONSTANT | unique |
| `timeslice` | Time Slice | ParMode.CONSTANT | False |
| `scope` | Scope | ParMode.CONSTANT | * |
| `srselect` | Sample Rate Match | ParMode.CONSTANT | max |
| `exportmethod` | Export Method | ParMode.CONSTANT | datindex |
| `autoexportroot` | Export Root | ParMode.EXPRESSION |  |
| `exporttable` | Export Table | ParMode.CONSTANT |  |
| `renamefrom` | Rename from | ParMode.CONSTANT | * |
| `renameto` | Rename to | ParMode.CONSTANT |  |

**Node-specific methods/attributes:**
`chan`, `chans`, `convertToKeyframes`, `end`, `export`, `exportChanges`, `isTimeSlice`, `numChans`, `numSamples`, `numpyArray`, `rate`, `start`

### renameCHOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `renamefrom` | Rename from | ParMode.CONSTANT | * |
| `renameto` | Rename to | ParMode.CONSTANT |  |
| `timeslice` | Time Slice | ParMode.CONSTANT | False |
| `scope` | Scope | ParMode.CONSTANT | * |
| `srselect` | Sample Rate Match | ParMode.CONSTANT | max |
| `exportmethod` | Export Method | ParMode.CONSTANT | datindex |
| `autoexportroot` | Export Root | ParMode.EXPRESSION |  |
| `exporttable` | Export Table | ParMode.CONSTANT |  |

**Node-specific methods/attributes:**
`chan`, `chans`, `convertToKeyframes`, `end`, `export`, `exportChanges`, `isTimeSlice`, `numChans`, `numSamples`, `numpyArray`, `rate`, `start`

### switchCHOP

| Parameter Name | Label | Mode | Value |
|---|---|---|---|
| `pageindex` | Page Index | ParMode.CONSTANT | 0 |
| `indexfirst` | First Input is Index | ParMode.CONSTANT | False |
| `index` | Index | ParMode.CONSTANT | 0 |
| `extend` | Extend | ParMode.CONSTANT | clamp |
| `timeslice` | Time Slice | ParMode.CONSTANT | False |
| `scope` | Scope | ParMode.CONSTANT | * |
| `srselect` | Sample Rate Match | ParMode.CONSTANT | max |
| `exportmethod` | Export Method | ParMode.CONSTANT | datindex |
| `autoexportroot` | Export Root | ParMode.EXPRESSION |  |
| `exporttable` | Export Table | ParMode.CONSTANT |  |
| `renamefrom` | Rename from | ParMode.CONSTANT | * |
| `renameto` | Rename to | ParMode.CONSTANT |  |

**Node-specific methods/attributes:**
`chan`, `chans`, `convertToKeyframes`, `end`, `export`, `exportChanges`, `isTimeSlice`, `numChans`, `numSamples`, `numpyArray`, `rate`, `start`

## Enums

```python
ParMode.CONSTANT
ParMode.EXPRESSION
ParMode.EXPORT
```
