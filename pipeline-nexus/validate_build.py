# Validasi build_scene Ep 4 TANPA render (hemat RAM): exec sumber build
# sampai sebelum still-render, lalu cek objek kunci ada di koordinat benar.
#   blender -b --factory-startup -P validate_build.py -- <dummy.png>
# Cek: ruang inti GELAP (60x48, dinding 16, TIDAK ADA wajah NEXUS, gerbang 5x6
# TERBUKA PENUH sejak S1, 12+1 panel dinding belakang), kota fajar (12 menara,
# layar GELAP tanpa wajah, lampu hangat #FFC98A), 213 instans Kairo DI DALAM
# ruang inti (grid 17x13, y 10..22) + 213 scar glow TERLIHAT, mata 213 biru
# TERBUKA (K213Eye 1.5), scar glow Kairo 6.0, TIDAK ADA merah (rim/nexus/eye/
# core biru, lampu nexus/eye = 0), TIDAK ADA laser, TIDAK ADA aula memori,
# TIDAK ADA teks 3D judul.
# JANGAN jalankan selama podcast 3D masih berjalan (aturan RAM) — tunggu
# podcast selesai.
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], "--", "/tmp/nx4_validate.png", "--res", "540", "960"]
src = open(os.path.join(HERE, "build_scene_nexus_ep4.py"),
           encoding="utf-8").read().split("scene.render.filepath = OUT")[0]
exec(src)

objs = bpy.data.objects
print("OBJECTS:", len(objs))
for name in ["NX_Gate", "NX_GateFrameL", "NX_GateFrameR", "NX_GateFrameT",
             "NX_WallPanel00", "NX_WallPanel05", "NX_WallPanel06",
             "NX_WallPanel11", "NX_WallPanelTop", "NX_WallL", "NX_WallR",
             "KAI_Scar", "KAI_ScarGlow", "EvaRimCore", "NX_Col11",
             "KAI_BackpackDropped", "CoreSocketed",
             "CT_Ground", "CT_Bldg0", "CT_Bldg11",
             "CT_Screen1", "CT_Screen2", "CT_LampHead0", "CT_LampHead3",
             "DawnLight", "WarmLight", "NexusLight", "RimRedCore",
             "K213_000", "K213_106", "K213_212",
             "K213_000_ScarGlow", "K213_212_ScarGlow"]:
    o = objs.get(name)
    print(("OK  " if o is not None else "MISS"), name,
          tuple(round(v, 2) for v in o.location) if o else "")
    assert o is not None, name

# --- TIDAK BOLEH ADA (Ep 4: wajah hilang, aula hilang, laser hilang, merah hilang) ---
for _gone in ["NX_FaceGlow", "NX_FaceHead", "NX_EyeL", "NX_EyeR",
              "NX_BrowL", "NX_Mouth", "NX_Scan0", "NX_Dot0", "NX_DotF0",
              "NX_WallBackL", "NX_WallBackR", "NX_WallBackT",
              "MH_Floor", "MH_Ceil", "MH_WallBack", "MH_Col0", "MH_Col7",
              "EvaLaser1", "EvaLaser2", "KaiLaser1", "KaiLaser2",
              "HallLight1", "HallLight2", "HallFill", "HallRedFlicker",
              "EvaRimHall", "NX_FaceSmall_Glow", "NX_FaceSmall_EyeL"]:
    assert objs.get(_gone) is None, f"{_gone} HARUS TIDAK ADA di Ep 4"
    print("GONE OK", _gone)
assert NX_FACE_SMALL_OBJS == [], "NX_FACE_SMALL_OBJS harus kosong di Ep 4"

# --- koordinat kunci ---
assert tuple(round(v, 2) for v in objs["NX_Gate"].scale) == (1.0, 1.0, 1.0), "gerbang harus skala penuh (terbuka)"
assert objs["NX_Gate"].hide_render is False, "gerbang TIDAK boleh hidden (terbuka sejak S1)"
# gerbang 5x6 m: plane scale (5,6) di lokasi (RX, 23.55, 3.0)
assert abs(objs["NX_Gate"].location.x - 80.0) < 0.01
assert abs(objs["NX_Gate"].location.y - 23.55) < 0.01
assert abs(objs["NX_Gate"].location.z - 3.0) < 0.01
# panel dinding belakang: panel 00 di (52.5, 23.8, 8.0), panel atas di (80, 23.8, 11.0)
assert abs(objs["NX_WallPanel00"].location.x - 52.5) < 0.01
assert abs(objs["NX_WallPanel00"].location.y - 23.8) < 0.01
assert abs(objs["NX_WallPanel00"].location.z - 8.0) < 0.01
assert abs(objs["NX_WallPanelTop"].location.x - 80.0) < 0.01
assert abs(objs["NX_WallPanelTop"].location.z - 11.0) < 0.01
# lantai ruang inti 60x48 + lantai kota 60x66 (block() meng-apply scale -> cek dimensions)
assert tuple(round(v, 2) for v in objs["NX_Floor"].dimensions) == (60.0, 48.0, 0.2)
assert tuple(round(v, 2) for v in objs["CT_Ground"].dimensions) == (60.0, 66.0, 0.2)
# backpack tetap di lantai ruang inti, TIDAK di kota
assert abs(objs["KAI_BackpackDropped"].location.x - 78.0) < 0.01
assert abs(objs["KAI_BackpackDropped"].location.y - (-1.5)) < 0.01
# data core tetap di soket (RX+2.5, -3.0)
assert abs(objs["CoreSocketed"].location.x - 82.5) < 0.01
assert abs(objs["CoreSocketed"].location.y - (-3.0)) < 0.01
# scar glow Kairo: emisi 6.0 (TERANG sejak frame 0, lanjutan Ep 3 S6)
_sg = bpy.data.materials["ScarGlowM"].node_tree.nodes["Principled BSDF"]
assert abs(_sg.inputs["Emission Strength"].default_value - 6.0) < 0.01, "ScarGlowM harus 6.0"
# 213 instans Kairo + 213 scar glow
k213 = [o for o in objs if o.name.startswith("K213_") and o.name[5:8].isdigit()
        and len(o.name) == 8]
assert len(k213) == 213, f"K213 instances: {len(k213)} (harus 213)"
k213_sg = [o for o in objs if o.name.endswith("_ScarGlow") and o.name.startswith("K213_")]
assert len(k213_sg) == 213, f"K213 scar glows: {len(k213_sg)} (harus 213)"
# grid DI DALAM ruang inti: 13 baris y 10..22, 17 kolom x 59.0..103.8
_ys = sorted({round(o.location.y, 1) for o in k213})
_xs = sorted({round(o.location.x, 1) for o in k213})
assert len(_ys) == 13 and _ys[0] == 10.0 and _ys[-1] == 22.0, f"baris y: {_ys}"
assert len(_xs) == 17 and _xs[0] == 59.0 and _xs[-1] == 103.8, f"kolom x: {_xs}"
assert abs(objs["K213_000"].location.x - 59.0) < 0.01
assert abs(objs["K213_000"].location.y - 10.0) < 0.01
assert abs(objs["K213_212"].location.x - 81.4) < 0.01
assert abs(objs["K213_212"].location.y - 22.0) < 0.01
# kilau scar 213 TERLIHAT sejak frame 0 (hide_render False semua)
assert all(o.hide_render is False for o in k213_sg), "semua K213 scar glow harus TERLIHAT di Ep 4"
# mata 213 TERBUKA (biru 1.5) sejak frame 0 — lanjutan Ep 3 S7
_ke = bpy.data.materials["K213Eye"].node_tree.nodes["Principled BSDF"]
assert abs(_ke.inputs["Emission Strength"].default_value - 1.5) < 0.01, "K213Eye harus 1.5 (terbuka)"
# lampu kota hangat mati di awal (di-key 0 -> 6 di animate)
_lw = bpy.data.materials["LampWarm"].node_tree.nodes["Principled BSDF"]
assert abs(_lw.inputs["Emission Strength"].default_value) < 0.01, "LampWarm harus 0 di awal"
# lampu nexus/eye/dawn/warm = 0 di awal (di-key di animate)
assert abs(objs["NexusLight"].data.energy) < 0.01, "NexusLight harus 0 (wajah hilang)"
assert abs(objs["EyeGlow"].data.energy) < 0.01, "EyeGlow harus 0 (sensor padam)"
assert abs(objs["DawnLight"].data.energy) < 0.01, "DawnLight harus 0 di awal"
assert abs(objs["WarmLight"].data.energy) < 0.01, "WarmLight harus 0 di awal"
# TIDAK ADA merah: rim/nexus/eye/core HARUS biru (0.30, 0.65, 1.0)
for _ln in ("RimRedCore", "NexusLight", "EyeGlow", "CoreLight"):
    _c = tuple(round(v, 2) for v in objs[_ln].data.color)
    assert _c == (0.30, 0.65, 1.0), f"{_ln} harus biru, dapat {_c}"
# TIDAK ADA teks 3D judul
assert not [o for o in objs if o.type == "FONT"], "teks 3D judul TIDAK boleh ada (judul hanya ASS)"
print("CHARS:", sorted(CHARS.keys()))
print("K213 rows:", len(_ys), "cols:", len(_xs), "| K213_BASE:", len(K213_BASE))
print("GATE scale:", tuple(objs["NX_Gate"].scale),
      "| gate hidden:", objs["NX_Gate"].hide_render)
print("WALL PANELS:", len([o for o in objs if o.name.startswith("NX_WallPanel")]))
print("CITY BLDGS:", len([o for o in objs if o.name.startswith("CT_Bldg") and o.name[7:].isdigit()]))
print("VALIDATE_BUILD_OK")
