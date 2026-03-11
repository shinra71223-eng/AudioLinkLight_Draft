# AudioLinkCore - MELODY INTENSITY (Derived from Vocal V18)
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
        avg = sum(y[:-1]) / len(y[:-1]) # Safe average
        
        # Safe std dev
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
    scriptOp.appendChan('uMelodyIntensity')
    scriptOp.appendChan('uMelodyEnergyRaw')
    scriptOp.appendChan('uMelodyOnset')
    
    mi, mr, mo = 0.0, 0.0, 0.0
    
    if len(scriptOp.inputs) >= 1:
        in_chop = scriptOp.inputs[0]
        if in_chop.numChans >= 2:
            # 楽器全体 (Instruments)
            raw_arr = np.abs(in_chop[0].numpyArray())
            hz = 22050.0 / (len(raw_arr) - 1) if len(raw_arr) > 1 else 21.5
            
            # Kick(0-80Hz)やHihat(高音)への過剰反応を防ぐため、200Hz〜6000Hzをメロディ帯域とする
            m_s, m_e = max(0, int(200/hz)), min(len(raw_arr), int(6000/hz))
            e_p = np.mean(raw_arr[m_s:m_e]) if m_s < m_e else 0.0
            
            # Vocalをコンテキスト(盛り上がり)として使用
            e_context = np.mean(np.abs(in_chop[1].numpyArray()))
            
            state = get_state(scriptOp.path)
            
            if state.get('_v') != 201:
                 state['pk'] = 0.01          
                 state['pk_raw'] = 0.01      
                 state['env_total'] = 0.01 
                 state['ema_mi'] = 0.0
                 
                 state['recent_onsets'] = [] 
                 state['z_onset'] = ZScoreDetector(lag=15, threshold=1.8, influence=0.2)
                 state['last_onset'] = 0
                 state['mo_env'] = 0.0
                 
                 state['_v'] = 201
                 
            # --- 1. Melody Energy Raw ---
            state['pk_raw'] = max(state['pk_raw'] * 0.999, e_p)
            safe_pk_raw = max(state['pk_raw'], 0.001)
            mr = min(1.0, e_p / safe_pk_raw)

            # --- 2. Contextual Emotion ---
            state['env_total'] = state['env_total'] * 0.95 + e_context * 0.05
            context_mult = 1.0 + min(0.5, state['env_total'] * 10.0) # ボーカルが歌っている時はメロディも熱量UP
            
            state['pk'] = max(state['pk'] * 0.995, e_p * context_mult)
            safe_pk = max(state['pk'], 0.01)
            
            # --- 3. Onset & Density (手数・密度) ---
            z_val = state['z_onset'].update(e_p)
            cur = scriptOp.time.frame
            last_onset = state.get('last_onset', 0)
            
            if cur < last_onset:
                last_onset = 0
                state['recent_onsets'] = []
                
            lock = (cur - last_onset) < 6 
            
            if z_val > state['z_onset'].threshold and e_p > 0.005 and not lock:
                 state['mo_env'] = 1.0
                 state['last_onset'] = cur
                 state['recent_onsets'].append(cur)
                 
            span_frames = 180 # 3秒間の密度を測定
            state['recent_onsets'] = [f for f in state['recent_onsets'] if (cur - f) <= span_frames]
            
            # ギターやピアノのアルペジオなど、手数が多ければ+0.50の特大ボーナス
            density_score = min(1.0, len(state['recent_onsets']) / 6.0) 
                 
            state['mo_env'] = max(0.0, state['mo_env'] - 0.1)
            mo = state['mo_env']

            # --- 4. Target Calculation (Nerfed Volume + Density) ---
            raw_ratio = min(1.0, (e_p * context_mult) / safe_pk)
            
            if raw_ratio < 0.5:
                vol_score = raw_ratio * 0.4
            else:
                vol_score = 0.20 + (raw_ratio - 0.5) * 0.8
            
            # メロディのインテンシティは、音量と手数の純粋な足し算 (S/V/Bは除外)
            target_mi = min(1.0, vol_score + (density_score * 0.50))
            
            # --- 5. EMA & Fast Smoothing (Melody Adjustment) ---
            current_ema = state.get('ema_mi', 0.0)
            
            # MELODY ADJUSTMENT (V21): Very fast response times. We want to follow the wave, not hold emotion.
            release_rate = 0.08  # 10x faster than vocal
            attack_rate = 0.15   # 10x faster than vocal
            
            if target_mi > current_ema:
                if target_mi >= 0.85 and density_score > 0.4:
                    attack_rate = 0.30 # Instant jump for intense arpeggios
                new_ema = current_ema * (1.0 - attack_rate) + target_mi * attack_rate
            else:
                new_ema = current_ema * (1.0 - release_rate) + target_mi * release_rate
                
            new_ema = max(0.0, min(1.0, new_ema))
            state['ema_mi'] = new_ema
            mi = new_ema
                    
    scriptOp['uMelodyIntensity'][0] = mi
    scriptOp['uMelodyEnergyRaw'][0] = mr
    scriptOp['uMelodyOnset'][0] = mo
