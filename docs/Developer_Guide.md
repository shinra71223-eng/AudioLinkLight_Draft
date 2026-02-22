# Developer Guide: AudioLinkCore V01
> **Version:** 1.0.0 (V01 Final Release)
> **Date:** 2026-02-22

Welcome to the definitive backend core for generating high-fidelity visualizer triggers from audio. `AudioLinkCore_V01` is designed to be highly robust, recovering gracefully from missing source files and providing strictly normalized envelopes for rendering smooth visual effects.

## 1. System Architecture

### 1-Channel Fallback & 2-Channel High-Fidelity
- **Tier 1/2 (2-Channel):** Demucs separates audio into `vocals.wav` and `no_vocals.wav` inside the `separated/` folder. This provides absolute separation giving high emotional context to vocals and accurate rhythmic parsing to instruments.
- **Tier 0 (1-Channel Fallback):** If `DemucsManager` determines either the Vocal or No-Vocal track is missing, it dynamically shuts off Demucs linkage and routes pure 1-Channel (Mixed Audio) to all parsers. *This means your visualizer will NEVER stop running, and will intelligently adapt its parsing to the mixed stream while attempting to regenerate Demucs sources in the background.*

### DemucsManager V2 (Cache Safeties)
`DemucsManager` checks cache validity using a strict `AND` logic operator internally. A cache tier is ONLY considered valid if `no_vocals.wav` **AND** `vocals.wav` both explicitly physically exist in the target directory. If one is deleted, auto-recovery (Tier 0) immediately begins.

## 2. Output Interfaces & Max Envelopes

A key update in AudioLinkCore V01 is the standardizing of envelope behaviors for rhythmic sections (Kick, Snare, Hihat, Clap). The parsing engine guarantees that the exact frame a hit is detected will output **exactly `1.0`**. Decay logic (`-0.15` or `-0.25` per frame) only begins on frame 2.

This provides visual developers with mathematical certainty when creating shader logic or threshold triggers.

### CHOP Outputs Matrix

| Channel | Typical Use-Case | Envelope Behavior |
| --- | --- | --- |
| `Kick` | Bass drum / Heartbeats | Max 1.0 peak, 3-frame hold, 0.15 decay |
| `Snare` | Sharp cracks / Flashes | Max 1.0 peak, 3-frame hold, 0.15 decay |
| `Hihat` | Strobe / Twinkle | Max 1.0 peak, 3-frame hold, 0.15 decay |
| `Clap` | Sharp, violent transient | Max 1.0 peak, 2-frame hold, 0.25 decay (fast!) |
| `uSubBass` | Slow breathing visuals | EMA scale maxing at 1.0 |
| `uBassEnergy` | Fast wobble / distort | Z-score peaking up to 1.0 via dynamic limits |
| `uSidechain` | Ducking background fx | Inverts (1.0 -> 0.0) based on kick hits |
| `uVocalIntensity`| Main vocalist emotion | EMA scale driven by climax overdrive |
| `uVocalHarshness`| Scratching/Grit fx | High freq band ratios |
| `uVocalBreath` | Breathing animations | Deep V-Valley detection algorithm |
| `uMelodyIntensity`| Fast arpeggio sparks | EMA scale with 10x decay multiplier vs vocals |

## 3. Node & DAT Structure

AudioLinkCore houses `Audio Spectrum CHOP` internally converting the input to FFT frequency arrays mapped mathematically to 22,050 Hz.
- `in1` receives either the generated CHOP channels from FILE_IO_ directly, or reads the files requested by DemucsManager.
- `parse_kick`, `parse_snare`, `parse_bass`, `parse_vocal`, `parse_melody` run parallel isolated state machines using inline generic Object classes (`ZScoreDetector`).

### 3.1 Script Independence
Every Script CHOP manages its own internal history mapping via a `STATE` dictionary keyed to its path. This eliminates all dependencies on external modules and allows TouchDesigner nodes to be moved, copied, or deleted with zero crashing.

## 4. Modifying Code / Custom Logic
If you wish to edit values (e.g., make Kick decay faster), edit the Python DAT under `AudioLinkCore/parse_kick_callbacks` directly.
Example:
```python
state['kick_env'] = max(0.0, state['kick_env'] - 0.20) # Changed from 0.15
```

## 5. Integrating with ESP32
Since the signals are strictly bounded (mostly clamping to `0` ~ `1`), you can safely send these outputs via OSC Out or Serial to your microcontrollers without blowing integer caps on LEDs. Multiply by 255 for RGB brightness metrics.
