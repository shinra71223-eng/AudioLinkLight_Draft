# AudioLinkCore - KICK PARSER (Fallback Support, Envelope Fix) w/ Peak Hold Envelope V2
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

STATE = {}
def get_state(op_path):
    global STATE
    if op_path not in STATE: STATE[op_path] = {}
    return STATE[op_path]
# -------------------------

def onCook(scriptOp):
    import numpy as np
    scriptOp.clear()
    scriptOp.numSamples = 1
    scriptOp.appendChan('Kick')
    
    is_kick = 0.0
    
    if len(scriptOp.inputs) >= 1:
        in_chop = scriptOp.inputs[0]
        if in_chop.numChans >= 1:
            # FALLBACK SUPPORT: Use ch[0] for instruments
            trans_arr = np.abs(in_chop[0].numpyArray())
            num_bins = len(trans_arr)
            hz = 22050.0 / (num_bins - 1) if num_bins > 1 else 1.0
            
            b_s, b_e = max(0, int(40 / hz)), min(int(80 / hz), num_bins)
            c_s, c_e = max(0, int(2000 / hz)), min(int(5000 / hz), num_bins)
            
            if b_s < b_e and c_s < c_e:
                 e_body = np.mean(trans_arr[b_s:b_e]) * 5.0
                 e_click = np.mean(trans_arr[c_s:c_e]) * 5.0
                 
                 state = get_state(scriptOp.path)
                 if state.get('_v') != 311:
                     state['hist_body'] = []
                     state['hist_click'] = []
                     state['last'] = 0
                     state['kick_env'] = 0.0 
                     state['_v'] = 311
                 
                 state['hist_body'].append(e_body)
                 state['hist_click'].append(e_click)
                 if len(state['hist_body']) > 60:
                     state['hist_body'].pop(0)
                 if len(state['hist_click']) > 60:
                     state['hist_click'].pop(0)
                 
                 sorted_b = sorted(state['hist_body'])
                 idx25 = max(0, len(sorted_b) // 4)
                 floor_b = sorted_b[idx25] if sorted_b else 0.01
                 
                 ratio_b = e_body / max(floor_b, 0.01)
                 
                 cur = scriptOp.time.frame
                 last_kick = state.get('last', 0)
                 
                 if cur < last_kick:
                     last_kick = 0
                     
                 lock = (cur - last_kick) < 3 
                 body_hit = (ratio_b > 2.0 and e_body > 0.5)
                 
                 # THE ENVELOPE FIX
                 trigger_happened = False
                 if body_hit and not lock:
                      state['kick_env'] = 1.0 
                      state['last'] = cur
                      trigger_happened = True
                 else:
                      state['kick_env'] = max(0.0, state['kick_env'] - 0.15)
                      
                 is_kick = state['kick_env']
    
    scriptOp['Kick'][0] = is_kick
