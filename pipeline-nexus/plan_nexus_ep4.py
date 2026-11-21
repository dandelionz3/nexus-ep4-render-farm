#!/usr/bin/env python3
# plan_nexus_ep4.py — generator plan.json NEXUS ZERO Episode 4 "WITHOUT YOU".
# Satu baris per frame (f 0..1439). Per frame: rig tiap karakter, intensitas
# lampu, kamera (x,y,z,target,focus,lens,roll Dutch), flag.
# Murni Python (tanpa bpy). Pola: plan_nexus_ep3.py.
# Set: ruang inti GELAP (RX=80, 60x48 m, dinding 16 m, wajah NEXUS HILANG,
# gerbang 5x6 m TERBUKA PENUH sejak S1) + kota fajar di balik dinding belakang
# (pusat y~55, menara + layar GELAP + lampu hangat #FFC98A).
# TIDAK ADA flash putih di Ep 4 (berakhir hitam + end card).
# TIDAK ADA merah di Ep 4 — satu frame pun (sensor Sentinel PADAM, lampu
# nexus/eye/hallred = 0 selalu).
# Flag baru Ep 4: wall_collapse (S4, 0..1 dinding runtuh), duplicates_scatter
# (S6, 0..1 — 213 Kairo masing-masing ke arah berbeda), city_warm (S4/S7,
# 0..1 lampu kota menyala berurutan), scar_flow (S7, 0..1 biru mengalir ke
# grid), dawn (S4/S7/S8, 0..1 langit fajar + cahaya hangat).
# Flag warisan: gate_open = 1.0 di SEMUA frame; scar_glow = True di semua
# frame (kilau biru TERANG lanjutan Ep 3 S6); kairo213_eyes = True di semua
# frame (mata biru TERBUKA lanjutan Ep 3 S7); nexus_face = False SELALU.
#   python3 plan_nexus_ep4.py [plan.json]
import json
import math
import os
import sys

N = 1440
RX = 80.0   # offset ruang inti NEXUS (sama dengan build_scene_nexus_ep2/3.py)
ALL_CHARS = ["KAI", "EVA"] + [f"SEN{i}" for i in range(1, 9)] + ["RES1", "RES2", "CIV1", "CIV2"]


def clamp(x, a, b):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def seg_t(f, a, b):
    return clamp((f - a) / max(1, b - a), 0.0, 1.0)


def shake(f, amp, freq=1.7):
    return amp * (math.sin(f * 0.9 * freq) * 0.6 + math.sin(f * 2.3 * freq + 1.3) * 0.4)


def walk_cycle(phase, amp, arm_amp=None):
    if arm_amp is None:
        arm_amp = amp * 0.8
    return {
        "legL": amp * math.sin(phase),
        "legR": -amp * math.sin(phase),
        "armL": -arm_amp * math.sin(phase),
        "armR": arm_amp * math.sin(phase),
        "bob": 0.045 * abs(math.cos(phase)),
    }


def char(x=0, y=0, z=0, rot=0, lean=0, squash=1.0, crouch=0.0, pitch=0.0,
         head_tilt=0, head_turn=0, armL=0, armR=0, legL=0, legR=0,
         eye_red=False, vis=True, mouthW=1.0, mouthH=1.0):
    return {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3), "rot": round(rot, 2),
            "lean": round(lean, 2), "squash": round(squash, 3), "crouch": round(crouch, 3),
            "pitch": round(pitch, 2), "head_tilt": round(head_tilt, 2),
            "head_turn": round(head_turn, 2), "armL": round(armL, 2), "armR": round(armR, 2),
            "legL": round(legL, 2), "legR": round(legR, 2),
            "eye_red": bool(eye_red), "vis": bool(vis),
            "mouthW": round(mouthW, 2), "mouthH": round(mouthH, 2)}


def hidden():
    return char(vis=False)


def cam(x, y, z, tx, ty, tz, focus, lens, roll=0.0):
    return {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3),
            "tx": round(tx, 3), "ty": round(ty, 3), "tz": round(tz, 3),
            "focus": round(focus, 2), "lens": round(lens, 1),
            "roll": round(roll, 2)}


def lights(nexus=0, gate=400, rim=0, eye=0, core=150, eva=0, fill=60,
           dawn=0, warm=0):
    """Ep 4: nexus=0 SELALU (wajah hilang), eye=0 SELALU (sensor padam),
    rim = rim BIRU di belakang EVA/bekas luka (bukan merah), gate = putih
    gerbang, eva = biru EVA, fill = isi ruangan gelap (rendah), core = denyut
    data core di soket, dawn = cahaya fajar hangat (S4+), warm = lampu kota
    hangat (S4/S7)."""
    return {"nexus": round(nexus, 1), "gate": round(gate, 1), "rim": round(rim, 1),
            "eye": round(eye, 1), "core": round(core, 1), "eva": round(eva, 1),
            "fill": round(fill, 1), "dawn": round(dawn, 1),
            "warm": round(warm, 1)}


def sentinel_frozen(x, y, rot=180):
    """Sentinel MEMBEKU (S1/S2/S5 Ep 4): satu lutut setengah tertekuk, badan
    condong, sensor PADAM (eye_red=False — tidak ada merah di Ep 4)."""
    return char(x, y, 0, rot=rot, lean=6, crouch=0.25, head_tilt=3,
                armL=8, armR=-4, legL=18, legR=-8, eye_red=False)


def hidden_sen():
    return hidden()


rows = []
for f in range(N):
    chars = {}
    # Core SUDAH terpasang di soket sejak S6 Ep 1; backpack tergeletak di
    # lantai ruang inti sejak S6 Ep 1 — keduanya ada di SEMUA segmen Ep 4,
    # TIDAK dibawa masuk gerbang, TIDAK dibawa ke kota. Gerbang TERBUKA
    # PENUH sejak S1 (gate_open = 1 konstan). Bekas luka menyala TERANG
    # sejak frame 0 (lanjutan Ep 3 S6); mata 213 Kairo TERBUKA sejak frame 0
    # (lanjutan Ep 3 S7). Wajah NEXUS TIDAK ADA (nexus_face = False selalu).
    props = {"core_in_hand": False, "core_table": False, "core_socket": True,
             "backpack": False, "backpack_dropped": True, "rain": False,
             "gate": True, "scar_glow": True, "nexus_face": False,
             "kairo213_eyes": True}
    gate_open = 1.0
    wall_collapse = 0.0
    duplicates_scatter = 0.0
    city_warm = 0.0
    scar_flow = 0.0
    dawn = 0.0
    flash_white = False  # TIDAK ADA flash di Ep 4

    # ================= S1 HOOK (0-71) — "THE FACE WAS GONE." =================
    if f < 72:
        # 214 Kairo melangkah keluar gerbang ke ruang inti GELAP; langit-langit
        # KOSONG — wajah NEXUS HILANG; hanya cahaya biru 214 bekas luka + EVA.
        # Shake halus HANYA di S1 (kamera ikut hening sesudahnya).
        t = seg_t(f, 0, 71)
        kai_y = lerp(20.0, 10.0, smooth(t))
        eva_y = lerp(19.0, 9.0, smooth(t))
        ph = f * 0.35
        c = walk_cycle(ph, 26)
        sh = shake(f, 0.03)
        chars["KAI"] = char(RX, kai_y, c["bob"], rot=180, lean=6, head_tilt=0,
                            armL=c["armL"], armR=c["armR"],
                            legL=c["legL"], legR=c["legR"])
        chars["EVA"] = char(RX + 2.0, eva_y, c["bob"], rot=180, lean=2, head_tilt=0,
                            armL=c["armL"], armR=c["armR"],
                            legL=c["legL"], legR=c["legR"])
        for _sx, _nm in ((-3, "SEN1"), (3, "SEN2")):
            chars[_nm] = sentinel_frozen(RX + _sx, 12, rot=0)
        if f < 24:
            # 1a: low-angle hero, slow push-in, Dutch 8 derajat
            chars_cam = cam(RX + 0.6, lerp(-7.0, -5.5, smooth(seg_t(f, 0, 23))) + sh,
                            lerp(1.0, 1.1, smooth(seg_t(f, 0, 23))),
                            RX, 12.0, 1.5, lerp(10.0, 8.0, smooth(seg_t(f, 0, 23))),
                            lerp(52, 50, seg_t(f, 0, 23)), roll=8)
        elif f < 48:
            # 1b: push-in lanjut, Kairo + EVA membesar
            chars_cam = cam(RX + 0.6, lerp(-5.5, -4.0, smooth(seg_t(f, 24, 47))) + sh,
                            lerp(1.1, 1.2, smooth(seg_t(f, 24, 47))),
                            RX + 0.5, 11.0, 1.45, lerp(8.0, 6.5, smooth(seg_t(f, 24, 47))),
                            lerp(50, 48, seg_t(f, 24, 47)), roll=8)
        else:
            # 1c: wide hero, Kairo ~25% tinggi frame; judul besar (ASS saja)
            chars_cam = cam(RX, -8.0, 2.0, RX, 14.0, 1.5, 16.0, 48, roll=8)
        li = lights(gate=450, rim=200, eva=300, fill=60, core=150)
        for _p in ("SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8",
                   "RES1", "RES2", "CIV1", "CIV2"):
            chars[_p] = hidden()
    # ================= S2 NEXUS MENGAKU (72-287) =================
    elif f < 288:
        if f < 144:
            # 2a: tilt-up lambat ke langit-langit kosong — TAHAN 2 detik pada
            # kekosongan (f120-143 kamera diam menatap langit-langit kosong).
            t = seg_t(f, 72, 119)
            hold = 1.0 if f >= 120 else smooth(t)
            chars["KAI"] = char(RX, 10.0, 0, rot=180, lean=4,
                                head_tilt=lerp(0, -14, hold),
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 9.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            for _sx, _nm in ((-3, "SEN1"), (3, "SEN2")):
                chars[_nm] = sentinel_frozen(RX + _sx, 12, rot=0)
            chars_cam = cam(RX, -2.0, 1.5, RX, 4.0, lerp(1.5, 12.0, hold),
                            lerp(8.0, 14.0, hold), lerp(50, 55, hold))
            li = lights(gate=400, rim=150, eva=300, fill=55, core=150)
        elif f < 216:
            # 2b: cut ke Sentinel — sensor PADAM, gelap total, patung sistem mati
            chars["KAI"] = char(RX, 10.0, 0, rot=180, lean=4, head_tilt=-8,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 9.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            for _sx, _nm in ((-3, "SEN1"), (3, "SEN2")):
                chars[_nm] = sentinel_frozen(RX + _sx, 12, rot=0)
            chars_cam = cam(RX + 3.0, 6.0, 1.8, RX - 3.0, 12.0, 1.5, 8.0, 52)
            li = lights(gate=400, rim=150, eva=320, fill=55, core=150)
        else:
            # 2c: Kairo + EVA diam mendengarkan suara kecil dari kegelapan
            t = seg_t(f, 216, 287)
            chars["KAI"] = char(RX, 10.0, 0, rot=180, lean=4, head_tilt=-8,
                                head_turn=lerp(0, -15, smooth(t)),
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 9.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            for _sx, _nm in ((-3, "SEN1"), (3, "SEN2")):
                chars[_nm] = sentinel_frozen(RX + _sx, 12, rot=0)
            chars_cam = cam(RX + 1.0, -2.0, 1.8, RX + 1.0, 10.0, 1.5, 10.0, 50)
            li = lights(gate=400, rim=150, eva=350, fill=55, core=150)
        for _p in ("SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8",
                   "RES1", "RES2", "CIV1", "CIV2"):
            chars[_p] = hidden()
    # ================= S3 SIAPA YANG MEMBANGUN GERBANG? (288-599) =================
    elif f < 600:
        if f < 360:
            # 3a: tracking two-shot — Kairo + EVA berjalan pelan di ruangan gelap
            t = seg_t(f, 288, 359)
            kai_y = lerp(10.0, 13.0, smooth(t))
            eva_y = lerp(9.0, 12.0, smooth(t))
            ph = f * 0.30
            c = walk_cycle(ph, 20)
            chars["KAI"] = char(RX, kai_y, c["bob"], rot=180, lean=5, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars["EVA"] = char(RX + 2.0, eva_y, c["bob"], rot=180, lean=2, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars_cam = cam(RX + 3.0, kai_y - 8.0, 1.6, RX + 1.0, kai_y + 1.0, 1.4,
                            6.0, 50)
            li = lights(gate=500, rim=180, eva=lerp(350, 500, smooth(t)),
                        fill=55, core=150)
        elif f < 480:
            # 3b: gerbang membesar di belakang; teks "WHO BUILT THE GATE?"
            t = seg_t(f, 360, 479)
            kai_y = lerp(13.0, 16.0, smooth(t))
            eva_y = lerp(12.0, 15.0, smooth(t))
            ph = f * 0.30
            c = walk_cycle(ph, 20)
            chars["KAI"] = char(RX, kai_y, c["bob"], rot=180, lean=5, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars["EVA"] = char(RX + 2.0, eva_y, c["bob"], rot=180, lean=2, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars_cam = cam(RX + 2.0, kai_y - 7.0, 1.5, RX, 18.0, 3.0, 12.0, 55)
            li = lights(gate=550, rim=180, eva=500, fill=55, core=150)
        else:
            # 3c: wide dari belakang Kairo + EVA — menoleh ke 213 Kairo
            t = seg_t(f, 480, 599)
            chars["KAI"] = char(RX, 16.0, 0, rot=180, lean=4,
                                head_turn=lerp(0, 30, smooth(t)),
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 15.0, 0, rot=180, lean=2,
                                head_turn=lerp(0, 25, smooth(t)),
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, 8.0, 2.0, RX, 18.0, 1.5, 12.0, 48)
            li = lights(gate=550, rim=200, eva=500, fill=55, core=150)
        for _p in ("SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8",
                   "RES1", "RES2", "CIV1", "CIV2"):
            chars[_p] = hidden()
    # ================= S4 DINDING RUNTUH (600-863) =================
    elif f < 864:
        if f < 672:
            # 4a: dinding mulai RUNTUH — panel gelap jatuh seperti kaca, lambat
            wall_collapse = smooth(seg_t(f, 600, 671))
            dawn = 0.35 * smooth(seg_t(f, 600, 671))
            chars["KAI"] = char(RX, 16.0, 0, rot=180, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 15.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, -6.0, 2.5, RX, 24.0, 4.0, 20.0, 46)
            li = lights(gate=500, rim=150, eva=500, fill=55, core=150,
                        dawn=300 * dawn, warm=0)
        elif f < 768:
            # 4b: reveal fajar — langit gradien hangat, layar GELAP
            wall_collapse = 1.0
            dawn = lerp(0.35, 0.8, smooth(seg_t(f, 672, 767)))
            city_warm = 0.3 * smooth(seg_t(f, 672, 767))
            t = seg_t(f, 672, 767)
            chars["KAI"] = char(RX, 16.0, 0, rot=180, lean=4, head_tilt=lerp(0, -6, smooth(t)),
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 15.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, lerp(-6.0, -2.0, smooth(t)), lerp(2.5, 3.5, smooth(t)),
                            RX, lerp(24.0, 45.0, smooth(t)), lerp(4.0, 6.0, smooth(t)),
                            lerp(20.0, 30.0, smooth(t)), lerp(46, 44, t))
            li = lights(gate=400, rim=150, eva=500, fill=70, core=150,
                        dawn=800 * dawn, warm=300 * city_warm)
        else:
            # 4c: wide kota fajar — Kairo kecil di ambang, lampu pertama menyala
            wall_collapse = 1.0
            dawn = 0.8
            city_warm = lerp(0.3, 0.5, smooth(seg_t(f, 768, 863)))
            chars["KAI"] = char(RX, 22.0, 0, rot=180, lean=4, head_tilt=-6,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 21.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, 10.0, 4.0, RX, 50.0, 8.0, 40.0, 44)
            li = lights(gate=350, rim=150, eva=500, fill=80, core=150,
                        dawn=800 * dawn, warm=300 * city_warm)
        for _p in ("SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8",
                   "RES1", "RES2", "CIV1", "CIV2"):
            chars[_p] = hidden()
    # ================= S5 NEXUS MEMOHON (864-1055) =================
    elif f < 1056:
        wall_collapse = 1.0  # dinding sudah runtuh (tetap terbuka ke fajar)
        dawn = 0.8
        city_warm = 0.5
        if f < 936:
            # 5a: tracking melewati Sentinel — Kairo tidak menoleh
            t = seg_t(f, 864, 935)
            kai_y = lerp(16.0, 10.0, smooth(t))
            ph = f * 0.30
            c = walk_cycle(ph, 20)
            chars["KAI"] = char(RX, kai_y, c["bob"], rot=180, lean=5, head_tilt=0,
                                armL=c["armL"], armR=c["armR"],
                                legL=c["legL"], legR=c["legR"])
            chars["EVA"] = char(RX + 2.0, 15.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            for _sx, _nm in ((-3, "SEN1"), (3, "SEN2")):
                chars[_nm] = sentinel_frozen(RX + _sx, 12, rot=0)
            chars_cam = cam(RX + 3.0, kai_y - 8.0, 1.7, RX, kai_y + 1.0, 1.5,
                            6.0, 50)
            li = lights(gate=350, rim=150, eva=500, fill=70, core=150,
                        dawn=800 * dawn, warm=300 * city_warm)
        elif f < 1008:
            # 5b: ECU bekas luka — berkilau biru terang, satu-satunya cahaya di wajah
            t = seg_t(f, 936, 1007)
            chars["KAI"] = char(RX, 10.0, 0, rot=0, lean=6, head_tilt=-4,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 15.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            for _sx, _nm in ((-3, "SEN1"), (3, "SEN2")):
                chars[_nm] = sentinel_frozen(RX + _sx, 12, rot=0)
            chars_cam = cam(lerp(RX + 0.3, RX + 0.15, smooth(t)), lerp(7.5, 7.6, smooth(t)),
                            lerp(1.65, 1.62, smooth(t)),
                            RX, 10.0, 1.6, lerp(2.5, 2.4, smooth(t)), lerp(75, 85, t))
            li = lights(gate=300, rim=200, eva=600, fill=60, core=150,
                        dawn=800 * dawn, warm=300 * city_warm)
        else:
            # 5c: close Kairo, diam satu detik penuh — keheningan adalah jawaban
            chars["KAI"] = char(RX, 10.0, 0, rot=0, lean=4, head_tilt=-4,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 15.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            for _sx, _nm in ((-3, "SEN1"), (3, "SEN2")):
                chars[_nm] = sentinel_frozen(RX + _sx, 12, rot=0)
            chars_cam = cam(RX + 1.0, 6.0, 1.6, RX, 10.0, 1.5, 4.5, 52)
            li = lights(gate=300, rim=200, eva=600, fill=60, core=150,
                        dawn=800 * dawn, warm=300 * city_warm)
        for _p in ("SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8",
                   "RES1", "RES2", "CIV1", "CIV2"):
            chars[_p] = hidden()
    # ================= S6 MEREKA MEMILIH KE MANA (1056-1199) =================
    elif f < 1200:
        wall_collapse = 1.0
        dawn = 0.85
        city_warm = 0.6
        if f < 1120:
            # 6a: dolly-in ke Kairo — menoleh ke 213 pendahulunya
            t = seg_t(f, 1056, 1119)
            chars["KAI"] = char(RX, 10.0, 0, rot=0, lean=4,
                                head_turn=lerp(0, 30, smooth(t)),
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 15.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX + 0.5, lerp(4.0, 3.0, smooth(t)), 1.7,
                            RX, 10.0, 1.5, lerp(8.0, 6.0, smooth(t)), 52)
            li = lights(gate=300, rim=200, eva=600, fill=60, core=150,
                        dawn=800 * dawn, warm=300 * city_warm)
        else:
            # 6b: wide penyebaran — 213 Kairo MASING-MASING KE ARAH BERBEDA
            duplicates_scatter = smooth(seg_t(f, 1120, 1199))
            chars["KAI"] = char(RX, 10.0, 0, rot=0, lean=4, head_turn=30,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 15.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, -2.0, 3.0, RX, 16.0, 1.5, 20.0, 46)
            li = lights(gate=300, rim=200, eva=600, fill=60, core=150,
                        dawn=800 * dawn, warm=300 * city_warm)
        for _p in ("SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8",
                   "RES1", "RES2", "CIV1", "CIV2"):
            chars[_p] = hidden()
    # ================= S7 KOTA MENYALA (1200-1319) =================
    elif f < 1320:
        wall_collapse = 1.0
        dawn = 1.0
        city_warm = lerp(0.6, 1.0, smooth(seg_t(f, 1200, 1319)))
        scar_flow = smooth(seg_t(f, 1200, 1319))  # biru mengalir ke grid kota
        duplicates_scatter = 1.0  # mereka terus menyebar ke kota
        if f < 1260:
            # 7a: aerial lambat di atas kota fajar
            t = seg_t(f, 1200, 1259)
            chars["KAI"] = char(RX, 24.0, 0, rot=180, lean=5, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 23.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, lerp(28.0, 30.0, smooth(t)), lerp(22.0, 25.0, smooth(t)),
                            RX, 55.0, 2.0, 40.0, 40)
            li = lights(gate=250, rim=150, eva=500, fill=90, core=150,
                        dawn=900 * dawn, warm=500 * city_warm)
        else:
            # 7b: aerial lanjut, fajar makin terang, kota makin menyala
            chars["KAI"] = char(RX, 24.0, 0, rot=180, lean=5, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 23.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, 32.0, 28.0, RX, 60.0, 2.0, 45.0, 40)
            li = lights(gate=250, rim=150, eva=500, fill=100, core=150,
                        dawn=900 * dawn, warm=500 * city_warm)
        for _p in ("SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8",
                   "RES1", "RES2", "CIV1", "CIV2"):
            chars[_p] = hidden()
    # ================= S8 TWIST (1320-1439) =================
    else:
        wall_collapse = 1.0
        dawn = 1.0
        city_warm = 1.0
        scar_flow = 1.0
        duplicates_scatter = 1.0
        if f < 1380:
            # 8a: wide hero pull-back — 214 Kairo kecil di hadapan kota fajar;
            # di kejauhan gerbang putih MASIH TERBUKA — kecil, terang
            t = seg_t(f, 1320, 1379)
            chars["KAI"] = char(RX, 24.0, 0, rot=180, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 23.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, lerp(20.0, 16.0, smooth(t)), lerp(6.0, 8.0, smooth(t)),
                            RX, 55.0, 4.0, 45.0, lerp(44, 42, t))
            li = lights(gate=250, rim=150, eva=500, fill=100, core=150,
                        dawn=900 * dawn, warm=500 * city_warm)
        else:
            # 8b: pull-back lanjut -> hitam + end card (f1380-1439, ASS)
            t = seg_t(f, 1380, 1439)
            chars["KAI"] = char(RX, 24.0, 0, rot=180, lean=4, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars["EVA"] = char(RX + 2.0, 23.0, 0, rot=180, lean=2, head_tilt=0,
                                armL=5, armR=5, legL=0, legR=0)
            chars_cam = cam(RX, lerp(16.0, 12.0, smooth(t)), lerp(8.0, 10.0, smooth(t)),
                            RX, 55.0, 4.0, lerp(45.0, 48.0, smooth(t)), lerp(42, 40, t))
            # meredup menuju hitam (end card di atas hitam)
            dim = 1.0 - 0.92 * smooth(seg_t(f, 1400, 1439))
            li = lights(gate=250 * dim, rim=150 * dim, eva=500 * dim,
                        fill=100 * dim, core=150 * dim,
                        dawn=900 * dim, warm=500 * dim)
        for _p in ("SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8",
                   "RES1", "RES2", "CIV1", "CIV2"):
            chars[_p] = hidden()

    # pastikan SEMUA karakter ada di tiap baris (0 frame kosong)
    for _p in ALL_CHARS:
        if _p not in chars:
            chars[_p] = hidden()

    rows.append({"f": f, "t": round(f / 24.0, 4), "chars": chars, "lights": li,
                 "cam": chars_cam, "props": props, "flash_white": flash_white,
                 "gate_open": round(gate_open, 3),
                 "wall_collapse": round(wall_collapse, 3),
                 "duplicates_scatter": round(duplicates_scatter, 3),
                 "city_warm": round(city_warm, 3),
                 "scar_flow": round(scar_flow, 3),
                 "dawn": round(dawn, 3)})


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "plan.json")
    with open(out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"WROTE {out}: {len(rows)} rows")
    # self-checks
    assert len(rows) == N
    assert rows[0]["f"] == 0 and rows[-1]["f"] == N - 1
    flashes = [r["f"] for r in rows if r["flash_white"]]
    assert flashes == [], f"flash frames (harus kosong di Ep 4): {flashes}"
    empty_rows = [r["f"] for r in rows if not r["chars"]]
    assert not empty_rows, f"frame kosong: {empty_rows}"
    missing = [(r["f"], [p for p in ALL_CHARS if p not in r["chars"]])
               for r in rows if any(p not in r["chars"] for p in ALL_CHARS)]
    assert not missing, f"karakter hilang: {missing[:5]}"
    gate = [r["f"] for r in rows if r["gate_open"] > 0]
    assert gate == list(range(N)), f"gate_open harus 1.0 di semua frame"
    nexus = [r["f"] for r in rows if r["lights"]["nexus"] > 0]
    assert nexus == [], f"nexus light harus 0 selalu: {nexus[:5]}"
    eye = [r["f"] for r in rows if r["lights"]["eye"] > 0]
    assert eye == [], f"eye light harus 0 selalu: {eye[:5]}"
    face = [r["f"] for r in rows if r["props"]["nexus_face"]]
    assert face == [], f"nexus_face harus False selalu: {face[:5]}"
    scar = [r["f"] for r in rows if r["props"]["scar_glow"]]
    assert scar == list(range(N)), "scar_glow harus True di semua frame"
    eyes = [r["f"] for r in rows if r["props"]["kairo213_eyes"]]
    assert eyes == list(range(N)), "kairo213_eyes harus True di semua frame"
    wc = [(r["f"], r["wall_collapse"]) for r in rows if r["wall_collapse"] > 0]
    assert 600 <= wc[0][0] <= 605, f"wall_collapse mulai: {wc[0]}"
    assert rows[863]["wall_collapse"] == 1.0, "wall_collapse harus 1.0 di f863"
    assert rows[1439]["wall_collapse"] == 1.0
    sc = [(r["f"], r["duplicates_scatter"]) for r in rows if r["duplicates_scatter"] > 0]
    assert 1120 <= sc[0][0] <= 1125, f"duplicates_scatter mulai: {sc[0]}"
    assert rows[1199]["duplicates_scatter"] == 1.0, "scatter harus 1.0 di f1199"
    cw = [(r["f"], r["city_warm"]) for r in rows if r["city_warm"] > 0]
    assert 672 <= cw[0][0] <= 678, f"city_warm mulai: {cw[0]}"
    assert rows[1439]["city_warm"] == 1.0
    sf = [(r["f"], r["scar_flow"]) for r in rows if r["scar_flow"] > 0]
    assert 1200 <= sf[0][0] <= 1205, f"scar_flow mulai: {sf[0]}"
    assert rows[1439]["scar_flow"] == 1.0
    dw = [(r["f"], r["dawn"]) for r in rows if r["dawn"] > 0]
    assert 600 <= dw[0][0] <= 606, f"dawn mulai: {dw[0]}"
    assert rows[1439]["dawn"] == 1.0
    print(f"CHECK OK: 0 flash, semua {len(rows)} baris punya "
          f"{len(ALL_CHARS)} karakter, 0 frame kosong")
    print(f"  gate_open=1: semua {len(gate)} frame | nexus=0 eye=0 selalu")
    print(f"  scar_glow + kairo213_eyes: semua frame | nexus_face: tidak pernah")
    print(f"  wall_collapse naik: {wc[0][0]}-863 (1.0 sejak f863)")
    print(f"  duplicates_scatter naik: {sc[0][0]}-1199 (1.0 sejak f1199)")
    print(f"  city_warm naik: {cw[0][0]}-1319 (1.0 sejak f1319)")
    print(f"  scar_flow naik: {sf[0][0]}-1319 (1.0 sejak f1319)")
    print(f"  dawn naik: {dw[0][0]}-1319 (1.0 sejak f1319)")


if __name__ == "__main__":
    main()
