# AudioLinkCore - SNARE/HIHAT/CLAP PARSER (Fallback Support, Envelope Fix)
import numpy as np

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
        self.signals.append(0)
        self.filtered.append(val)
        self.avg_filter.append(0)
        self.std_filter.append(0)
        y = self.filtered[-self.lag-1:]
        if len(y) < 2: return 0.0
        avg = sum(y[:-1]) / len(y[:-1])
        variance = sum([((x - avg) ** 2) for x in y[:-1]]) / len(y[:-1])
        std = variance ** 0.5
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

def onCook(scriptOp):
    scriptOp.clear()
    scriptOp.numSamples = 1
    scriptOp.appendChan('Snare')
    scriptOp.appendChan('Hihat')
    scriptOp.appendChan('Clap')
    
    is_snare = 0.0
    is_hihat = 0.0
    is_clap = 0.0
    
    if len(scriptOp.inputs) >= 1:
        in_chop = scriptOp.inputs[0]
        if in_chop.numChans >= 1:
            # FALLBACK SUPPORT: Use ch[0] for instruments
            vis_arr = np.abs(in_chop[0].numpyArray())
            num_bins = len(vis_arr)
            hz = 22050.0 / (num_bins - 1) if num_bins > 1 else 100
            
            s_s, s_e = max(0, int(400/hz)), min(num_bins, int(4000/hz))
            h_s, h_e = max(0, int(6000/hz)), min(num_bins, int(15000/hz))
            c_s, c_e = max(0, int(2000/hz)), min(num_bins, int(5000/hz)) 
            
            e_mid = np.mean(vis_arr[s_s:s_e]) if s_s < s_e else 0.0
            e_hi = np.mean(vis_arr[h_s:h_e]) if h_s < h_e else 0.0
            e_clap = np.mean(vis_arr[c_s:c_e]) * 8.0 if c_s < c_e else 0.0
            
            state = get_state(scriptOp.path)
            if state.get('_v') != 111: 
                state['z_s'] = ZScoreDetector(lag=15, threshold=1.5)
                state['z_h'] = ZScoreDetector(lag=10, threshold=2.0)
                state['z_c'] = ZScoreDetector(lag=12, threshold=1.2) 
                
                state['p_m'] = 0.0
                state['p_h'] = 0.0
                state['p_c'] = 0.0
                
                state['snare_env'] = 0.0
                state['hihat_env'] = 0.0
                state['clap_env'] = 0.0
                
                state['last_snare'] = 0
                state['last_hihat'] = 0
                state['last_clap'] = 0
                
                state['_v'] = 111
                
            d_m = max(0.0, e_mid - state['p_m'])
            d_h = max(0.0, e_hi - state['p_h'])
            d_c = max(0.0, e_clap - state['p_c'])
            
            state['p_m'], state['p_h'], state['p_c'] = e_mid, e_hi, e_clap
            
            z_s = state['z_s'].update(d_m)
            z_h = state['z_h'].update(d_h)
            z_c = state['z_c'].update(d_c)
            
            cur = scriptOp.time.frame
            
            # -- Snare Envelope Fix --
            last_snare = state['last_snare']
            if cur < last_snare: last_snare = 0 
            snare_lock = (cur - last_snare) < 3 
            
            if z_s > 0.6 and e_mid > 0.0002 and d_m > 0.001 and not snare_lock: 
                state['snare_env'] = 1.0
                state['last_snare'] = cur
            else:
                state['snare_env'] = max(0.0, state['snare_env'] - 0.15)
            is_snare = state['snare_env']
            
            # -- Hihat Envelope Fix --
            last_hihat = state['last_hihat']
            if cur < last_hihat: last_hihat = 0
            hihat_lock = (cur - last_hihat) < 3
            
            if z_h > 1.0 and e_hi > 0.00005 and not hihat_lock: 
                state['hihat_env'] = 1.0
                state['last_hihat'] = cur
            else:
                state['hihat_env'] = max(0.0, state['hihat_env'] - 0.15)
            is_hihat = state['hihat_env']
            
            # -- Clap Envelope Fix --
            last_clap = state['last_clap']
            if cur < last_clap: last_clap = 0
            clap_lock = (cur - last_clap) < 2
            
            if z_c > 1.2 and e_clap > 0.005 and not clap_lock: 
                state['clap_env'] = 1.0
                state['last_clap'] = cur
            else:
                state['clap_env'] = max(0.0, state['clap_env'] - 0.25)
            is_clap = state['clap_env']
            
    scriptOp['Snare'][0] = is_snare
    scriptOp['Hihat'][0] = is_hihat
    scriptOp['Clap'][0] = is_clap
