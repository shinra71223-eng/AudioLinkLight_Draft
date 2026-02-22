# AudioLinkCore_V01 Release

This folder contains the complete and final assets for **AudioLinkCore V01**, featuring robust max-1.0 envelopes, dynamic 1-channel fallback, and the V2 DemucsManager patch.

## Contents
* `AudioLinkCore_V01.tox` : Use TouchDesigner to save your `AudioLinkCore` COMP component out to this directory to bundle it for git. (Right-click AudioLinkCore -> "Save Component .tox")
* `build_demucs_manager_v2.py` : Script to deploy the updated DemucsManager (safety patched) to any new project.
* `Developer_Guide.md` : Technical architecture parameters and logic documentation.
* `dats/` : A folder tracking the absolute exact Python logic stored within the `parse_*_callbacks` scripts in your V01 TD environment.

## What's New in V01
1. **Mathematics Guarantee:** Kick, Snare, Hihat, and Clap hits output exactly `1.0` upon detection, ensuring no missed thresholds in your visual engine.
2. **Absolute Reliability (Fallback):** If your target file doesn't have an AI-separated vocal track, AudioLinkCore catches the exception and dynamically recycles the instrumental track into the vocal parser using dual-referencing to mimic context emotion. It never crashes.
3. **Safety Caching (V2):** Your manager validates actual WAV presence (`vocals.wav` and `no_vocals.wav`) before trusting cache `.json` files.

## How To Install in a New Project
1. Drag and drop `AudioLinkCore_V01.tox` into your new TouchDesigner grid.
2. Drag and drop `build_demucs_manager_v2.py` into a Text DAT and click "Run Script".
3. Hook your Audio File Out to Demucs, and hook Demucs into AudioLink!
