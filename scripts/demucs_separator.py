import sys
import os
import argparse
import tempfile
import shutil
import json
import time
import subprocess

# Fix encoding for Korean/Japanese filenames on Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 1. Setup Environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bin_dir = os.path.join(project_root, 'bin')
os.environ['PATH'] = bin_dir + os.pathsep + os.environ['PATH']

# 2. Monkeypatch Torchaudio BEFORE importing demucs
import torch
import torchaudio
import soundfile as sf
import numpy as np

print("Applying Torchaudio Monkeypatch...")

def patched_info(filepath, format=None):
    # Use soundfile to get info
    try:
        sinfo = sf.info(filepath)
        # Construct a mock AudioMetaData-like object or whatever torchaudio.info returns
        # valid torchaudio.info returns AudioMetaData object
        # but Demucs might just access .sample_rate and .num_channels
        
        class MockInfo:
            def __init__(self, sr, chans, frames):
                self.sample_rate = sr
                self.num_channels = chans
                self.num_frames = frames
                self.bits_per_sample = 16 # Assumption
                self.encoding = 'PCM_S'
        
        return MockInfo(sinfo.samplerate, sinfo.channels, sinfo.frames)
    except Exception as e:
        # Fallback to original if file not found or SF fails
        # But original is broken, so raise
        raise e

def patched_load(filepath, frame_offset=0, num_frames=-1, normalize=True, channels_first=True, format=None):
    # Use soundfile to read
    # sf.read(file, start=, stop=)
    try:
        start = frame_offset
        stop = None
        if num_frames > 0:
            stop = start + num_frames
            
        data, sr = sf.read(filepath, start=start, stop=stop, always_2d=True, dtype='float32')
        
        # data is (Time, Channels)
        # torchaudio expects (Channels, Time)
        tensor = torch.from_numpy(data.T)
        
        return tensor, sr
    except Exception as e:
        raise e

def patched_save(filepath, src, sample_rate, **kwargs):
    # src is Tensor (Channels, Time)
    # sf.write expects (Time, Channels) numpy
    try:
        data = src.detach().cpu().numpy().T
        sf.write(filepath, data, sample_rate)
    except Exception as e:
        raise e

# Apply Patch
torchaudio.info = patched_info
torchaudio.load = patched_load
torchaudio.save = patched_save

print("Monkeypatch Applied (Load/Save/Info). Importing Demucs...")
from demucs import separate

# ---------------------------------------------------------
# Helper: Convert mp3 to wav using ffmpeg if needed
def convert_to_wav(input_path, ffmpeg_exe):
    fd, temp_path = tempfile.mkstemp(suffix='.wav')
    os.close(fd)
    cmd = [ffmpeg_exe, '-y', '-i', input_path, '-acodec', 'pcm_s16le', '-ar', '44100', temp_path]
    print(f"Converting to WAV using local FFmpeg...")
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        subprocess.check_call(cmd)
    return temp_path

# Quality Tier Definitions
QUALITY_TIERS = {
    'fast': {'model': 'htdemucs',    'shifts': 0, 'overlap': 0.25, 'tier': 1},
    'hq':   {'model': 'htdemucs_ft', 'shifts': 5, 'overlap': 0.5,  'tier': 2},
}
def safe_move_stems(src_dir, dst_dir):
    """Move stem files from src to dst, handling OneDrive locks.
    Instead of renaming the whole directory, copies individual files."""
    os.makedirs(dst_dir, exist_ok=True)
    
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dst_file = os.path.join(dst_dir, filename)
        if os.path.isfile(src_file):
            # Overwrite existing file
            for attempt in range(3):
                try:
                    shutil.copy2(src_file, dst_file)
                    break
                except PermissionError:
                    if attempt < 2:
                        time.sleep(1)  # Wait for OneDrive to release
                    else:
                        print(f"Warning: Could not copy {filename} after 3 attempts")
    
    # Try to clean up source directory
    try:
        shutil.rmtree(src_dir, ignore_errors=True)
    except:
        pass

def main():
    parser = argparse.ArgumentParser(description='Demucs Separator Wrapper')
    parser.add_argument('input_file', help='Input audio file path')
    parser.add_argument('--quality', choices=['fast', 'hq'], default='fast',
                        help='Separation quality: fast (Tier 1) or hq (Tier 2)')
    args = parser.parse_args()
    
    quality = QUALITY_TIERS[args.quality]
    print(f"Quality: {args.quality} (Tier {quality['tier']}, model={quality['model']})")
    
    ffmpeg_exe = os.path.join(bin_dir, 'ffmpeg.exe')
    output_base = os.path.join(project_root, 'separated')
    input_path = os.path.abspath(args.input_file)
    
    if not os.path.exists(output_base):
        os.makedirs(output_base)

    if not os.path.exists(ffmpeg_exe):
        print(f"Warning: FFmpeg not found at {ffmpeg_exe}. Conversion might fail.")

    # 1. Pre-convert if MP3
    processing_path = input_path
    is_temp = False
    
    ext = os.path.splitext(input_path)[1].lower()
    if ext != '.wav':
        try:
            processing_path = convert_to_wav(input_path, ffmpeg_exe)
            is_temp = True
            print(f"Created Temp WAV for processing: {processing_path}")
        except Exception as e:
            print(f"Conversion failed: {e}")
            sys.exit(1)

    print(f"--- Running Demucs ({args.quality.upper()}) ---")
    
    demucs_args = [
        "-n", quality['model'],
        "--two-stems", "vocals",
        "--shifts", str(quality['shifts']),
        "--overlap", str(quality['overlap']),
        "-o", output_base,
        processing_path
    ]
    
    try:
        # Run Demucs Main Logic
        separate.main(demucs_args)
        
        # Cleanup temp wav
        if is_temp and os.path.exists(processing_path):
            try:
                os.remove(processing_path)
            except:
                pass
        
        # Determine Source and Destination
        model_folder = quality['model']  # htdemucs or htdemucs_ft
        original_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # Source path (where Demucs output it)
        if is_temp:
            temp_name = os.path.splitext(os.path.basename(processing_path))[0]
            src = os.path.join(output_base, model_folder, temp_name)
        else:
            src = os.path.join(output_base, model_folder, original_name)
        
        # Destination path (New structure: separated/fast or separated/hq)
        target_subfolder = 'fast' if args.quality == 'fast' else 'hq'
        dst = os.path.join(output_base, target_subfolder, original_name)
        
        # Move Output
        if os.path.exists(src):
            if os.path.normpath(src) != os.path.normpath(dst):
                safe_move_stems(src, dst)
                print(f"Saved to: {dst}")
                
                # Try to remove the empty model folder (e.g. separated/htdemucs) if empty
                try:
                    os.rmdir(os.path.dirname(src)) 
                except:
                    pass
        elif os.path.exists(dst):
            print(f"Output already in place: {dst}")
        else:
            print(f"Warning: Expected output not found at {src}")
        
        # Save quality.json
        if os.path.exists(dst):
            qinfo = {
                'tier': quality['tier'],
                'model': quality['model'],
                'shifts': quality['shifts'],
                'overlap': quality['overlap'],
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            with open(os.path.join(dst, 'quality.json'), 'w') as f:
                json.dump(qinfo, f, indent=2)
            print(f"quality.json saved (Tier {quality['tier']})")
                
        print(f"--- Separation Success ({args.quality.upper()}) ---")
        
    except Exception as e:
        print(f"Demucs Execution Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Final Cleanup: Remove any left-over tmp folders in separated/
        try:
            for item in os.listdir(output_base):
                item_path = os.path.join(output_base, item)
                if os.path.isdir(item_path) and item.startswith('tmp'):
                    # Check if empty or very old? For now just try strict rmdir (safe)
                    # or rmtree if we are sure it is a tmp folder we created
                    # Demucs creates specific temp folders? No, usually in root if not specified.
                    # We only delete if it looks like our temp wav folder context
                    pass
            
            # Remove the base model folders if they are empty (htdemucs, htdemucs_ft)
            for m in ['htdemucs', 'htdemucs_ft']:
                mpath = os.path.join(output_base, m)
                if os.path.exists(mpath):
                    try:
                        os.rmdir(mpath) # Only removes if empty
                    except:
                        pass
        except:
            pass

if __name__ == "__main__":
    main()
