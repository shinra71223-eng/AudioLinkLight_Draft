# AudioLinkCore - BASS PARSER (2-stem)
import numpy as np

# --- Inlined Utilities ---
class ZScoreDetector:
    def __init__(self, lag=10, threshold=2.0, influence=0.5):
        self.lag = lag
        self.threshold = threshold
        self.influence = influence
        self.signals = [0] * lag
        self.filtered = [0] * lag
        self.avg_filter = [0] * lag
        self.std_filter = [0] * lag
        
    def update(self, val):
        import numpy as np
        self.signals.append(0)
        self.filtered.append(val)
        self.avg_filter.append(0)
        self.std_filter.append(0)
        
        y = self.filtered[-self.lag-1:]
        if len(y) < 2: return 0.0
        
        avg = np.mean(y[:-1])
        std = np.std(y[:-1])
        current = y[-1]
        z = 0.0 if std == 0 else (current - avg) / std
        
        self.avg_filter[-1] = avg
        self.std_filter[-1] = std
        
        if abs(z) > self.threshold:
            self.signals[-1] = 1 if z > 0 else -1
            self.filtered[-1] = self.influence * current + (1 - self.influence) * self.filtered[-2]
        else:
            self.signals[-1] = 0
            self.filtered[-1] = current
        return z

# Inline state management (No external core module dependency)
STATE = {}
def get_state(op_path):
    global STATE
    if op_path not in STATE: STATE[op_path] = {}
    return STATE[op_path]
# -------------------------

def onCook(scriptOp):
    scriptOp.clear()
    scriptOp.numSamples = 1
    
    scriptOp.appendChan('uSubBass')
    scriptOp.appendChan('uBassEnergy')
    scriptOp.appendChan('uSidechain')

    val_sub = 0.0
    val_wobble = 0.0
    val_sc = 0.0

    if len(scriptOp.inputs) >= 1:
        in_chop = scriptOp.inputs[0]
        if in_chop.numChans >= 2:
            # Demucs Source: [Bass, Vocals, ...] usually
            b_arr = np.abs(in_chop[0].numpyArray())
            d_arr = np.abs(in_chop[0].numpyArray()) # Reference to Bass channel for Sidechain calculation
            hz = 22050.0 / (len(b_arr) - 1) if len(b_arr) > 1 else 21.5
            
            state = get_state(scriptOp.path)
            
            # Reset Check (changed _v to force a clean slate)
            if state.get('_v') != 3:
                 state['p_s'] = 0.0001
                 state['p_k'] = 0.0001
                 state['e_k'] = 0.0
                 state['p_w'] = 0.0001 # Initialize peak tracker for Wobble (Bass Energy)
                 state['z_b'] = ZScoreDetector(lag=15, threshold=1.5)
                 state['_v'] = 3
                 
            # 1. Sub Bass
            idx_sub = max(1, int(150/hz))
            e_sub = np.sum(b_arr[:idx_sub])
            
            # Update: slightly faster decay (0.999 -> 0.995) for better silence tracking
            state['p_s'] = max(state['p_s'] * 0.995, e_sub)
            if state['p_s'] > 0.0001: 
                val_sub = min(1.0, e_sub / state['p_s'])
            
            # 2. Wobble (Bass Energy) - THE FIX
            ib1, ib2 = int(40/hz), int(100/hz)
            if ib1 < ib2:
                 e_w_raw = np.mean(b_arr[ib1:ib2])
                 
                 # Dynamic Peak Normalization instead of fixed *10 multiplier
                 state['p_w'] = max(state['p_w'] * 0.995, e_w_raw)
                 safe_pw = max(state['p_w'], 0.001)
                 
                 e_w_norm = min(1.0, e_w_raw / safe_pw)
                 zb = state['z_b'].update(e_w_norm)
                 
                 # Apply Z-score boost to the normalized value
                 val_wobble = min(1.0, e_w_norm * 1.5) if zb > 1.0 else e_w_norm
                 
            # 3. Sidechain
            ek = np.sum(d_arr[:idx_sub])
            state['p_k'] = max(state['p_k'] * 0.999, ek)
            kn = ek / state['p_k'] if state['p_k'] > 0.001 else 0.0
            state['e_k'] = state['e_k'] * 0.5 + kn * 0.5
            val_sc = max(0.0, 1.0 - state['e_k'] * 1.5)
            
    # Outputs
    scriptOp['uSubBass'][0] = val_sub
    scriptOp['uBassEnergy'][0] = val_wobble
    scriptOp['uSidechain'][0] = val_sc
