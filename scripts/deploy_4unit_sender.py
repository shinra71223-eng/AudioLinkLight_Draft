import numpy as np

# ------------------------------------------------------------------
# TouchDesigner Script DAT / Execute DAT 用送信スクリプト
# ------------------------------------------------------------------
# プロトコル: [0x55][0xAA][LEN_L][LEN_H] + [DATA...]
# 合計データ長: (880 * 3 * 3) + (972 * 3) = 10836 bytes
# ------------------------------------------------------------------

def onFrameStart(frame):
    # 4つのソースTOPを定義
    sources = [
        op('led_source_u1'),    # Sub 1 (10x88)
        op('led_source'),       # Sub 2 (10x88)
        op('led_source_d1'),    # Sub 3 (10x88)
        op('led_source_USB')    # Master (12x81)
    ]
    
    serial_op = op('serial_led') 
    if not serial_op: return

    # ヘッダー作成 (0x55 0xAA + データ長 10836)
    data_len = 10836
    header = bytearray([0x55, 0xAA, data_len & 0xFF, (data_len >> 8) & 0xFF])
    full_payload = header
    
    for i, top in enumerate(sources):
        if top is None:
            # データが足りない場合はゼロ埋め
            expected = 2640 if i < 3 else 2916
            full_payload.extend(bytearray(expected))
            continue
            
        # データを取得
        pixels = top.numpyArray()[:,:,:3] # RGBA -> RGB (Bottom-Up)
        
        # 【重要】上下反転 (TouchDesignerのBottom-UpをTop-Downに変換)
        # オリジナルコード led_sender_pyserial.py L93 の挙動を再現
        pixels = pixels[::-1, :, :]
        
        # 0-255にスケールしてバイト変換
        data = (np.clip(pixels * 255.0, 0, 255)).astype(np.uint8).tobytes()
        full_payload.extend(data)
        
    # 送信 (Serial DAT の sendBytes を使用)
    serial_op.sendBytes(full_payload)
