# AudioLinkCore - VOCAL DIAGNOSTIC V18 (Climax Overdrive & No Gravity Cap)
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

def onCook(scriptOp):
    scriptOp.clear()
    scriptOp.numSamples = 1
    scriptOp.appendChan('uVocalIntensity')
    scriptOp.appendChan('uVocalHarshness')
    scriptOp.appendChan('uVocalSustain')
    scriptOp.appendChan('uVocalVibrato')
    scriptOp.appendChan('uVocalOnset')
    scriptOp.appendChan('uVocalEnergyRaw')
    scriptOp.appendChan('uVocalBreath')
    
    vi, vh, vs, vv, vo, vr, vb = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    
    if len(scriptOp.inputs) >= 1:
        in_chop = scriptOp.inputs[0]
        if in_chop.numChans >= 2:
            # Vocal channel
            v_arr = np.abs(in_chop[1].numpyArray())
            e_p = np.mean(v_arr)
            hz = 22050.0 / (len(v_arr) - 1) if len(v_arr) > 1 else 21.5
            
            # Context Energy (Bass/Instrumental)
            e_context = np.mean(np.abs(in_chop[0].numpyArray()))
            
            # Harshness & Breath band calculations
            if e_p < 0.005:
                 vh = 0.0
            else:
                 i_l, i_m, i_h = int(350/hz), int(1000/hz), int(4000/hz)
                 if i_l < i_m < i_h and i_h < len(v_arr):
                      el, eh = np.sum(v_arr[i_l:i_m]), np.sum(v_arr[i_m:i_h])
                      e_tot = el + eh
                      if e_tot > 0.001: 
                           val = eh / e_tot
                           vh = min(1.0, val * 1.5)
                      else:
                           vh = 0.0
                 else:
                      vh = 0.0
                 
            state = get_state(scriptOp.path)
            
            # Increment version to 918 for clean dictionary reset
            if state.get('_v') != 918:
                 state['h'] = []
                 state['s'] = 0.0
                 state['pk'] = 0.01          
                 state['pk_raw'] = 0.01      
                 
                 state['env_total'] = 0.01 
                 state['ema_vi'] = 0.0
                 
                 state['recent_onsets'] = [] 
                 state['z_onset'] = ZScoreDetector(lag=15, threshold=1.8, influence=0.2)
                 state['last_onset'] = 0
                 state['vo_env'] = 0.0
                 
                 # NEW: V-Valley Tracker Variables
                 state['prev_vr'] = 0.0
                 state['valley_state'] = 0 # 0: normal/rising, 1: dropping (tracking valley)
                 state['valley_peak'] = 0.0
                 state['valley_bottom'] = 1.0
                 state['breath_env'] = 0.0
                 
                 state['_v'] = 918
                 
            # --- 1. Vocal Energy Raw (Instantaneous) ---
            state['pk_raw'] = max(state['pk_raw'] * 0.999, e_p)
            safe_pk_raw = max(state['pk_raw'], 0.001)
            vr = min(1.0, e_p / safe_pk_raw)

            # --- 2. Contextual Emotion Processing ---
            state['env_total'] = state['env_total'] * 0.95 + e_context * 0.05
            context_mult = 1.0 + min(0.5, state['env_total'] * 10.0)
            
            state['pk'] = max(state['pk'] * 0.995, e_p * context_mult)
            safe_pk = max(state['pk'], 0.01)
            
            state['h'].append(e_p)
            if len(state['h']) > 30: state['h'].pop(0)
            
            arr = np.array(state['h'])
            mu = np.mean(arr)
            cv = np.std(arr) / (mu + 1e-5)
            
            if mu > 0.0005:
                 if cv < 0.2:
                      state['s'] += 1/60.0 
                      vv = 0.0
                 elif cv < 0.6:
                      vv = min(1.0, (cv - 0.2) / 0.4)
                      state['s'] = max(0.0, state['s'] - 1.0/60.0) 
                 else:
                      state['s'] = max(0.0, state['s'] - 2.0/60.0) 
            else:
                 state['s'] = max(0.0, state['s'] - 4.0/60.0) 
                 
            vs = min(1.0, state['s'] / 1.5)
            
            # --- 3. Onset & Density Detection ---
            z_val = state['z_onset'].update(e_p)
            cur_frame = scriptOp.time.frame
            last_onset = state.get('last_onset', 0)
            
            if cur_frame < last_onset:
                last_onset = 0
                state['recent_onsets'] = []
                
            lock = (cur_frame - last_onset) < 6 
            
            onset_triggered = False
            if z_val > state['z_onset'].threshold and e_p > 0.01 and not lock:
                 state['vo_env'] = 1.0
                 state['last_onset'] = cur_frame
                 onset_triggered = True
                 state['recent_onsets'].append(cur_frame)
                 
            span_frames = 180
            state['recent_onsets'] = [f for f in state['recent_onsets'] if (cur_frame - f) <= span_frames]
            
            # Higher weighting for density (up to 0.50 later)
            density_score = min(1.0, len(state['recent_onsets']) / 5.0) 
                 
            state['vo_env'] = max(0.0, state['vo_env'] - 0.1)
            vo = state['vo_env']
            
            # --- 4. V-Valley Breath Detection ---
            prev_vr = state['prev_vr']
            delta_vr = vr - prev_vr
            is_breathing = False
            breath_score = 0.0
            
            # State Machine for Envelope Shape Tracking
            if delta_vr < -0.01:
                # Falling: Enter Valley state, track depth
                if state['valley_state'] == 0:
                    state['valley_state'] = 1
                    state['valley_peak'] = prev_vr
                    state['valley_bottom'] = vr
                else:
                    state['valley_bottom'] = min(state['valley_bottom'], vr)
                    
            elif delta_vr > 0.02 and state['valley_state'] == 1:
                # Rising sharply from a valley: Recovery! Evaluate the V-shape
                depth = state['valley_peak'] - state['valley_bottom']
                
                # If we dropped from high, hit near zero, and are now shooting up...
                if depth > 0.3 and state['valley_bottom'] < 0.15:
                    is_breathing = True
                    # Breath score is based on how deep the drop was
                    breath_score = min(1.0, depth * 1.5)
                    state['breath_env'] = breath_score
                    
                # Reset state
                state['valley_state'] = 0
            
            elif delta_vr >= 0:
                # Rising normally or flat
                state['valley_state'] = 0
                
            state['prev_vr'] = vr
            
            state['breath_env'] = max(0.0, state['breath_env'] - 0.03) # visual decay
            vb = state['breath_env']

            # --- 5. EMA Target Calculation (with Nerfed Volume & Mega Bonuses) ---
            raw_ratio = min(1.0, (e_p * context_mult) / safe_pk)
            
            # V17 FIX: 2-Stage Volume Sensitivity (Hard Nerf)
            if raw_ratio < 0.5:
                # Stage 1: Maxes out at 0.15 when volume is 50%
                vol_score = raw_ratio * 0.3
            else:
                # Stage 2: Scales the remaining 50% up to ONLY 0.40 (instead of 1.0)
                vol_score = 0.15 + (raw_ratio - 0.5) * 0.5
            
            # Sustain Bonus (Amplified when > 0.5)
            sustain_bonus = vs * 0.15
            if vs > 0.5:
                sustain_bonus += (vs - 0.5) * 1.0 # HUGE Extra up to 0.50 bonus
                
            # Vibrato Bonus (Amplified when > 0.5)
            vibrato_bonus = vv * 0.10
            if vv > 0.5:
                vibrato_bonus += (vv - 0.5) * 1.0 # HUGE Extra up to 0.50 bonus
                
            # Breath Bonus (Amplified when > 0.5)
            breath_bonus = vb * 0.15
            if vb > 0.5:
                breath_bonus += (vb - 0.5) * 1.0 # HUGE Extra up to 0.50 bonus
            
            total_bonus = sustain_bonus + vibrato_bonus + breath_bonus
            
            # Target incorporates Nerfed Volume, Density (Max 0.40), AND all Bonuses directly
            target_vi = min(1.0, vol_score + (density_score * 0.40) + total_bonus)
            
            # --- 6. Temporal Smoothing (EMA) with Dynamic Release & Overdrive Attack ---
            current_ema = state.get('ema_vi', 0.0)
            
            # V17 FIX: Dynamic Release Rate
            # If we hold emotion (bonuses active), decay slowly (0.005). 
            # If normal singing (no bonuses), decay faster (0.012) to return to base 0.5 approx.
            release_rate = 0.005 if total_bonus > 0.1 else 0.012
            
            if target_vi > current_ema:
                # V18 FIX: Climax Overdrive
                # When target is very high AND we have strong bonuses, accelerate the attack x3!
                attack_rate = 0.015
                if target_vi >= 0.85 and total_bonus > 0.4:
                    attack_rate = 0.05
                    
                new_ema = current_ema * (1.0 - attack_rate) + target_vi * attack_rate
            else:
                new_ema = current_ema * (1.0 - release_rate) + target_vi * release_rate
                
            # Relaxed Silence Gate
            if vr < 0.01:
                # If we detected a deep V-valley (breath) recently, maintain some heat
                if vb > 0.1:
                    new_ema = max(new_ema, 0.25)
                else:
                    new_ema *= 0.95 
                
            new_ema = max(0.0, min(1.0, new_ema))
            state['ema_vi'] = new_ema
            vi = new_ema
                    
    scriptOp['uVocalIntensity'][0] = vi
    scriptOp['uVocalHarshness'][0] = vh
    scriptOp['uVocalSustain'][0] = vs
    scriptOp['uVocalVibrato'][0] = vv
    scriptOp['uVocalOnset'][0] = vo
    scriptOp['uVocalEnergyRaw'][0] = vr
    scriptOp['uVocalBreath'][0] = vb
