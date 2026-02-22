import td

def build_demucs_manager():
    print("🚀 === GENERATING DemucsManager V2 (2-Stem Auto-Recovery) === 🚀")
    root = op('/project1')
    
    manager = root.op('DemucsManager')
    if manager: manager.destroy()
        
    manager = root.create(baseCOMP, 'DemucsManager')
    manager.nodeX = 500
    manager.nodeY = 100
    manager.color = (0.2, 0.8, 0.2)
    
    page = manager.appendCustomPage('Demucs')
    page.appendStr('Targetfile', label='Target Audio File')
    page.appendStr('Statusmsg', label='Status Message')
    page.appendInt('State', label='State (0=IDLE, 1=ANALYZING, 2=READY)')
    page.appendInt('Currenttier', label='Current Quality Tier')
    page.appendToggle('Hqprocessing', label='HQ Processing Active')
    page.appendStr('Demucssavepath', label='Demucs Save Path')
    
    mod_dat = manager.create(textDAT, 'mod_process_manager')
    mod_dat.text = """import os
import subprocess
import threading
import json
try:
    import td
except:
    pass

class DemucsBridge:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.project_root = td.project.folder
        self.python_exe = self.project_root + '/.venv/Scripts/python.exe'
        self.script_path = self.project_root + '/scripts/demucs_separator.py'
        self.output_root = self.project_root + '/separated'
        self.fast_root = self.output_root + '/fast'
        self.hq_root = self.output_root + '/hq'
        
    def _is_process_running(self):
        pid = self.ownerComp.fetch('demucs_pid', 0)
        if pid > 0:
            try:
                os.kill(pid, 0)
                return True
            except:
                self.ownerComp.store('demucs_pid', 0)
                return False
        return False

    def check_valid_stems(self, target_dir):
        # V2 FIX: Strictly require BOTH vocals.wav AND no_vocals.wav for a valid cache
        return os.path.exists(os.path.join(target_dir, 'no_vocals.wav')) and os.path.exists(os.path.join(target_dir, 'vocals.wav'))

    def get_tier_from_json(self, target_dir):
        qpath = os.path.join(target_dir, 'quality.json')
        if os.path.exists(qpath):
            try:
                with open(qpath, 'r') as f:
                    return json.load(f).get('tier', 0)
            except:
                return 0
        return 0

    def get_best_available_path(self, filename):
        hq_path = os.path.join(self.hq_root, filename)
        if self.check_valid_stems(hq_path):
            return hq_path, 2
            
        fast_path = os.path.join(self.fast_root, filename)
        if self.check_valid_stems(fast_path):
            return fast_path, 1
            
        leg_path = os.path.join(self.output_root, 'htdemucs', filename)
        if self.check_valid_stems(leg_path):
            return leg_path, max(1, self.get_tier_from_json(leg_path))
            
        return None, 0

    def OnFileChange(self, filepath):
        if not filepath:
            return
        filepath = os.path.abspath(filepath)
        filename = os.path.splitext(os.path.basename(filepath))[0]
        self.ownerComp.par.Targetfile = filepath
        
        best_path, tier = self.get_best_available_path(filename)
        
        if tier > 0:
            self.ownerComp.par.Statusmsg = f"Ready (Tier {tier})"
            self.ownerComp.par.State = 2
            self.ownerComp.par.Currenttier = tier
            self.ownerComp.par.Demucssavepath = best_path
            
            if tier < 2 and not self._is_process_running():
                print(f"[DemucsManager] Tier {tier} cache found. Starting HQ upgrade...")
                self.start_separation(filepath, 'hq')
            return
            
        if self._is_process_running():
            cq = self.ownerComp.fetch('demucs_quality', '')
            if cq != 'fast':
                self._kill_process()
            else:
                return
                
        self.ownerComp.par.Currenttier = 0
        self.ownerComp.par.Demucssavepath = ""
        self.start_separation(filepath, 'fast')

    def _kill_process(self):
        pid = self.ownerComp.fetch('demucs_pid', 0)
        if pid > 0:
            try:
                os.kill(pid, 9)
            except:
                pass
        self.ownerComp.store('demucs_pid', 0)
        self.ownerComp.par.Hqprocessing = 0

    def start_separation(self, filepath, quality):
        if quality == 'fast':
            self.ownerComp.par.State = 1
        else:
            self.ownerComp.par.Hqprocessing = 1
            
        self.ownerComp.par.Statusmsg = f"Separating ({quality.upper()})..."
        cmd = [self.python_exe, self.script_path, filepath, '--quality', quality]
        
        env = os.environ.copy()
        env['TQDM_DISABLE'] = '1'
        
        try:
            CREATE_NO_WINDOW = 0x08000000
            process = subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            self.ownerComp.store('demucs_pid', process.pid)
            self.ownerComp.store('demucs_quality', quality)
            print(f"[DemucsManager] Started {quality.upper()} (PID: {process.pid})")
        except Exception as e:
            print(f"[DemucsManager] Launch failed: {e}")
            return
            
        def wait_thread(pid, qual, fpath):
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                print(f"[DemucsManager] {qual.upper()} Success!")
            else:
                print(f"[DemucsManager] {qual.upper()} Exited code {process.returncode}")
            
            fpath_safe = fpath.replace('\\\\', '/')
            cmd_str = f"args[0]._on_complete({pid}, '{qual}', r'''{fpath_safe}''', {process.returncode})"
            try:
                td.run(cmd_str, self, delayFrames=1)
            except:
                pass
                
        t = threading.Thread(target=wait_thread, args=(process.pid, quality, filepath))
        t.daemon = True
        t.start()

    def _on_complete(self, pid, qual, fpath, retcode):
        current_pid = self.ownerComp.fetch('demucs_pid', 0)
        if current_pid == pid:
            self.ownerComp.store('demucs_pid', 0)
            self.ownerComp.store('demucs_quality', '')
            
        if qual == 'hq':
            self.ownerComp.par.Hqprocessing = 0
            
        if retcode == 0:
            filename = os.path.splitext(os.path.basename(fpath))[0]
            best_path, tier = self.get_best_available_path(filename)
            if tier > 0:
                self.ownerComp.par.Currenttier = tier
                self.ownerComp.par.Demucssavepath = best_path
                self.ownerComp.par.Statusmsg = f"Ready (Tier {tier})"
                self.ownerComp.par.State = 2
                print(f"[DemucsManager] Separation mapped to path: {best_path}")
"""

    parexec = manager.create(parameterexecuteDAT, 'watch_file_io')
    parexec.par.op = '/project1/File_IO_/Audio_File_IN_IO'
    parexec.par.pars = 'file'
    parexec.text = """def onValueChange(par, prev):
    mod = parent().op('mod_process_manager').module
    if hasattr(mod, 'DemucsBridge'):
        bridge = mod.DemucsBridge(parent())
        bridge.OnFileChange(par.eval())
"""
    parexec.par.active = True

    print(" -> Rewiring AudioLinkCore to DemucsManager")
    core = root.op('AudioLinkCore')
    if core:
        for ain in core.findChildren(type=audiofileinCHOP):
            stem_name = ain.name.split('_')[1]
            ain.par.file.expr = f"op('/project1/DemucsManager').par.Demucssavepath.eval() + '/{stem_name}.wav'"
            # Force them to evaluate immediately
            try:
                _ = ain.par.file.eval()
            except:
                pass
    else:
        print("WARNING: AudioLinkCore not found to rewire.")

    print("✅ DemucsManager completely built and hooked into FILE_IO_ and AudioLinkCore!")
    
    # Try triggering currently playing file
    try:
        current_file = op('/project1/File_IO_/Audio_File_IN_IO').par.file.eval()
        if current_file:
            getattr(mod_dat.module, 'DemucsBridge')(manager).OnFileChange(current_file)
    except:
        pass

build_demucs_manager()
