# build_scene_nexus_ep4.py — NEXUS ZERO Episode 4 "WITHOUT YOU" (vinyl-toy stylized).
# Copy build_scene_nexus_ep3.py, adaptasi Ep 4 (bukan dari nol).
# 2 set: ruang inti NEXUS GELAP (RX=80, 60x48 m, dinding 16 m, wajah NEXUS
# HILANG TOTAL — langit-langit KOSONG, 12 kolom GELAP tidak menyala, gerbang
# cahaya putih 5x6 m TERBUKA PENUH sejak S1 — gate_open=1 konstan) + KOTA
# FAJAR di balik dinding belakang (y 24..90, 12 menara + layar GELAP tanpa
# wajah + jendela/lampu hangat #FFC98A). Dinding belakang = 12 panel
# NX_WallPanel (runtuh S4, di-key di animate) — bukan dinding padat.
# 213 Kairo membeku sebagai instans collection DI DALAM ruang inti (grid
# 17x13, x RX-22.4..RX+22.4 step 2.8 + offset 1.4, y 10..22 step 1.0) —
# mereka sudah melangkah keluar gerbang; kilau scar + mata biru TERBUKA sejak
# frame 0 (lanjutan Ep 3 S6/S7).
# TIDAK ADA merah di Ep 4 — satu frame pun: sensor Sentinel PADAM, lampu
# nexus/eye = 0, core biru (bukan merah), kolom gelap, partikel biru.
# TIDAK ADA teks 3D judul di set (judul hanya ASS).
# 4 karakter lock DESIGN-v1.md: KAIRO (1.8 m, bekas luka alis kiri WAJIB,
# kilau biru TERANG, backpack tergeletak di lantai, data core di soket),
# NEXUS (TIDAK ADA — hanya suara kecil dari kegelapan), EVA (silver-white,
# mata biru), SENTINEL (logam hitam 2.2 m, sensor PADAM, MEMBEKU).
# Render setup B7: Eevee, samples env FS_SAMPLES default 6, ray OFF, volumetrics
# tile 16, DOF ON, motion blur ON, subsurf 1, bevel 0, AgX. World strength 0.45,
# kabut 0.02 ruang inti / 0.01 kota fajar.
# Run:
#   blender -b --factory-startup -P build_scene_nexus_ep4.py -- <out.png> [--res 540 960]
import bpy
import math
import os
import sys
from mathutils import Vector

argv = sys.argv
args = argv[argv.index("--") + 1:] if "--" in argv else []
OUT = args[0] if args else "//nexus_ep4_preview.png"
RES_X, RES_Y = (540, 960)
if "--res" in args:
    i = args.index("--res")
    RES_X, RES_Y = int(args[i + 1]), int(args[i + 2])

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- render setup B7 ----------
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "None"


def _set(obj, attr, value):
    if hasattr(obj, attr):
        setattr(obj, attr, value)


_set(scene.eevee, "use_raytracing", os.environ.get("FS_RAY", "0") == "1")
_set(scene.eevee, "use_shadows", True)
_set(scene.eevee, "volumetric_tile_size", os.environ.get("FS_VOLTILE", "16"))
_set(scene.eevee, "volumetric_end", 60.0)
scene.eevee.taa_render_samples = int(os.environ.get("FS_SAMPLES", "6"))
scene.render.use_motion_blur = os.environ.get("FS_MB", "1") == "1"
_set(scene.render, "motion_blur_shutter", 0.5)

world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.055, 0.059, 0.067, 1.0)  # langit malam #0E0F11
bg.inputs["Strength"].default_value = 0.45  # malam jauh lebih gelap


# ---------- materials ----------
def mat(name, rgb, rough=0.45, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def emissive(name, rgb, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Strength"].default_value = strength
    return m


def halo_mat(name, rgb, strength, alpha_center):
    """Emissive transparan dengan falloff radial (alpha penuh di tengah,
    memudar -> 0 di tepi) — hologram tanpa tepi persegi yang keras."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Roughness"].default_value = 1.0
    tex = nt.nodes.new("ShaderNodeTexCoord")
    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = "RADIAL"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    # Jarak radial di koordinat Generated: tepi tengah panel ~0.5, sudut ~0.7.
    # Fade HARUS selesai di 0.45 supaya tidak ada tepi persegi yang tersisa
    # (stop 0.55/0.85 sebelumnya membuat tepi panel tetap alpha penuh).
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (alpha_center, alpha_center, alpha_center, 1.0)
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
    mid = ramp.color_ramp.elements.new(0.20)
    mid.color = (alpha_center, alpha_center, alpha_center, 1.0)
    nt.links.new(tex.outputs["Generated"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Alpha"])
    m.blend_method = "BLEND"
    return m


# --- Kairo ---
SKIN_KAI = mat("SkinKairo", (0.79, 0.63, 0.51), 0.5)          # #C9A186
HAIR_KAI = mat("HairKairo", (0.05, 0.05, 0.06), 0.6)
JACKET = mat("JacketKairo", (0.12, 0.13, 0.15), 0.6)          # #1E2126
JACKET2 = mat("JacketRes1", (0.16, 0.14, 0.12), 0.6)
JACKET3 = mat("JacketRes2", (0.10, 0.13, 0.16), 0.6)
SHIRT = mat("ShirtKairo", (0.16, 0.16, 0.18), 0.6)
PANTS_K = mat("PantsKairo", (0.08, 0.09, 0.10), 0.6)          # #14161A
BOOTS = mat("BootsKairo", (0.16, 0.13, 0.09), 0.55)           # #2A2118
BACKPACK_M = mat("Backpack", (0.14, 0.15, 0.17), 0.6)         # #23262B
STRIP_BLUE = emissive("StripBlue", (0.18, 0.42, 1.0), 0.6)    # #2E6BFF lemah
EYE_DARK = mat("EyeDark", (0.05, 0.03, 0.02), 0.2)            # mata cokelat gelap Kairo
# --- EVA ---
SKIN_EVA = mat("SkinEva", (0.85, 0.87, 0.89), 0.25, metal=0.6)  # silver-white #D8DDE3
SUIT_EVA = mat("SuitEva", (0.88, 0.89, 0.91), 0.3, metal=0.4)
EYE_BLUE = emissive("EyeBlue", (0.30, 0.65, 1.0), 1.2)       # #4DA6FF — satu-satunya biru
CIRCUIT_BLUE = emissive("CircuitBlue", (0.30, 0.65, 1.0), 0.5)
# --- Sentinel ---
METAL_SEN = mat("MetalSentinel", (0.05, 0.06, 0.06), 0.35, metal=0.9)  # #0D0E10
METAL_SEN2 = mat("MetalSentinel2", (0.10, 0.11, 0.12), 0.3, metal=0.9)
SENSOR_OFF = mat("SensorOff", (0.08, 0.02, 0.02), 0.3)
SENSOR_RED = emissive("SensorRed", (1.0, 0.0, 0.0), 0.9)     # AgX: merah hanya di luminansi rendah (1.2 masih salmon)
# --- NEXUS ---
NEXUS_RED = emissive("NexusRed", (1.0, 0.10, 0.10), 0.8)     # #FF1A1A wajah hologram (1.2 masih pucat di AgX)
NEXUS_EYE = emissive("NexusEye", (1.0, 0.05, 0.05), 0.9)
NEXUS_GLOW = emissive("NexusGlow", (0.55, 0.02, 0.02), 0.5)
NEXUS_HEAD = mat("NexusHead", (0.12, 0.02, 0.02), 0.5)       # siluet kepala gelap (fitur di depannya)
NEXUS_HEAD.use_nodes = True
_nb = NEXUS_HEAD.node_tree.nodes["Principled BSDF"]
_nb.inputs["Emission Color"].default_value = (0.55, 0.02, 0.02, 1.0)
_nb.inputs["Emission Strength"].default_value = 0.3
NEXUS_DOT = emissive("NexusDot", (1.0, 0.12, 0.12), 1.0)     # partikel wajah
NEXUS_DOT_DIM = emissive("NexusDotDim", (1.0, 0.12, 0.12), 0.45)  # partikel redup (variasi awan)
# wajah BESAR ruang inti (bukan layar kota): mata pekat + halo transparan.
# NEXUS_EYE_BIG: base diffuse GELAP supaya emisi dominan — mata tetap merah
# pekat di AgX, tidak tercuci jadi pink pucat oleh cahaya sekitar.
NEXUS_EYE_BIG = emissive("NexusEyeBig", (1.0, 0.0, 0.0), 0.7)
_nb2 = NEXUS_EYE_BIG.node_tree.nodes["Principled BSDF"]
_nb2.inputs["Base Color"].default_value = (0.30, 0.0, 0.0, 1.0)
# bola mata besar kena specular dari area light depan (CoreFill) -> kilau
# putih menutupi merahnya (mata Sentinel kecil di f_0032 tidak kena ini).
# Matikan specular: mata harus merah pekat, bukan pink pucat.
_nb2.inputs["Roughness"].default_value = 1.0
if "Specular IOR Level" in _nb2.inputs:
    _nb2.inputs["Specular IOR Level"].default_value = 0.0
NEXUS_HALO = halo_mat("NexusHalo", (1.0, 0.08, 0.08), 0.55, 0.4)      # panel wajah: transparan, tepi memudar
NEXUS_EYE_GLOW = halo_mat("NexusEyeGlow", (1.0, 0.06, 0.06), 0.5, 0.4)  # glow samar di belakang mata
SCAN_M = emissive("ScanLine", (1.0, 0.12, 0.12), 0.55)       # garis scanline tipis di wajah
SCAN_M.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.5
SCAN_M.blend_method = "BLEND"
CIRCUIT_RED = emissive("CircuitRed", (1.0, 0.08, 0.08), 0.9)
# --- set ---
GROUND = mat("Ground", (0.090, 0.094, 0.102), 0.9)
WET_GROUND = mat("WetGround", (0.05, 0.06, 0.08), 0.15)      # jalan basah reflektif
WALL = mat("Wall", (0.141, 0.149, 0.165), 0.85)
BUILDING = mat("Building", (0.11, 0.12, 0.14), 0.9)
BUILDING2 = mat("Building2", (0.13, 0.11, 0.11), 0.9)
WIN_WARM = emissive("WinWarm", (1.0, 0.72, 0.38), 1.2)
WIN_DARK = mat("WinDark", (0.05, 0.06, 0.09), 0.4)
WIN_RED = emissive("WinRed", (1.0, 0.10, 0.10), 1.0)
LAMP_GLOW = emissive("LampGlow", (1.0, 0.85, 0.55), 6.0)
SIREN_GLOW = emissive("SirenGlow", (0.827, 0.282, 0.235), 6.0)
POLE = mat("Pole", (0.15, 0.15, 0.16), 0.5, metal=0.6)
NEON_RED = emissive("NeonRed", (1.0, 0.08, 0.08), 2.0)
NEON_BLUE = emissive("NeonBlue", (0.18, 0.42, 1.0), 1.2)
SCREEN_M = mat("ScreenDark", (0.03, 0.03, 0.04), 0.4)
PAPER = mat("Paper", (0.92, 0.90, 0.84), 0.7)
INK = mat("Ink", (0.05, 0.05, 0.08), 0.5)
WOOD = mat("Wood", (0.35, 0.22, 0.12), 0.7)
CABLE_M = mat("Cable", (0.08, 0.08, 0.09), 0.6)
CORE_BODY = mat("CoreBody", (0.04, 0.04, 0.05), 0.3, metal=0.7)
CORE_LINE = emissive("CoreLine", (0.30, 0.65, 1.0), 1.4)     # Ep 4: garis data core BIRU (bukan merah — NEXUS mati)
GATE_M = emissive("GateLight", (1.0, 1.0, 0.95), 1.2)  # FIX R1: gerbang harus lebih terang dari dinding         # gerbang cahaya putih (disembunyikan s.d. S8; 1.5 lalu 0.9 masih blown-out putih murni)
# --- aula memori (Ep 3): putih terang tapi BUKAN putih murni blown-out ---
HALL_FLOOR = mat("HallFloor", (0.92, 0.92, 0.90), 0.15)   # lantai reflektif putih
HALL_WALL = mat("HallWall", (0.88, 0.88, 0.86), 0.85)     # dinding/kolom putih lembut
HALL_COL = mat("HallCol", (0.85, 0.85, 0.83), 0.6)
# FIX R1: dinding/kolom aula tidak kena cahaya langsung (semua lampu aula
# mengarah sumbu Y) — beri emisi putih lembut 0.25 supaya aula terbaca PUTIH,
# bukan hitam di paruh atas frame. Lantai sudah terang, tidak perlu emisi.
for _hw, _hc in ((HALL_WALL, (0.88, 0.88, 0.86)), (HALL_COL, (0.85, 0.85, 0.83))):
    _hw.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (*_hc, 1.0)
    _hw.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.25
# mata 213 Kairo: TERBUKA (biru 1.5) sejak frame 0 — lanjutan Ep 3 S7.
K213_EYE_M = emissive("K213Eye", (0.30, 0.65, 1.0), 1.5)
_KB = K213_EYE_M.node_tree.nodes["Principled BSDF"]
_KB.inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1.0)
# kilau bekas luka 213 instans (TERLIHAT sejak frame 0 di Ep 4): biru terang,
# sama seperti Kairo.
SCAR213_M = emissive("ScarGlow213", (0.10, 0.30, 0.90), 2.0)
# lampu kota fajar #FFC98A (1.0, 0.79, 0.54) — emisi di-key 0 -> 6 di animate
# (city_warm S4/S7). Nama material "LampWarm" dipakai animate_nexus_ep4.py.
LAMP_WARM = emissive("LampWarm", (1.0, 0.79, 0.54), 0.0)
RAIN_M = mat("Rain", (0.75, 0.82, 0.9), 0.1)
RAIN_M.blend_method = "BLEND"
RAIN_M.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.35
DRONE_M = mat("Drone", (0.10, 0.10, 0.11), 0.4, metal=0.7)
DRONE_LIGHT = emissive("DroneLight", (1.0, 0.05, 0.05), 2.0)
BARRICADE_M = mat("Barricade", (0.35, 0.30, 0.10), 0.7)
SOCKET_M = mat("Socket", (0.12, 0.12, 0.14), 0.4, metal=0.8)


def smooth(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_smooth()
    o.select_set(False)


def block(name, loc, size, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    smooth(o)
    return o


def ball(name, loc, size, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=loc, segments=32, ring_count=16)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    smooth(o)
    return o


def cylinder(name, loc, radius, depth, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot, vertices=32)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    smooth(o)
    return o


def dot(name, loc, size, m):
    """Titik partikel hemat: icosphere subdiv 1 (bukan UV sphere 32x16)."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (size, size, size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    smooth(o)
    return o


def plane(name, loc, size, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0], size[1], 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    return o


def text_obj(name, body, loc, size, m, rot=(math.radians(90), 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object
    t.name = name
    t.data.body = body
    t.data.extrude = 0.015
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.resolution_u = 16
    try:
        t.data.font = bpy.data.fonts.load("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    except Exception:
        pass
    t.data.materials.append(m)
    return t


def nexus_mini_face(prefix, loc, w, h, eye_mat=NEXUS_EYE):
    """Wajah NEXUS kecil di layar kota: glow plane + 2 mata + mulut."""
    cx, cy, cz = loc
    plane(f"{prefix}_Glow", (cx, cy, cz), (w, h), NEXUS_GLOW, rot=(math.radians(90), 0, 0))
    ball(f"{prefix}_EyeL", (cx - w * 0.22, cy - 0.06, cz + h * 0.12),
         (w * 0.09, 0.05, h * 0.05), eye_mat)
    ball(f"{prefix}_EyeR", (cx + w * 0.22, cy - 0.06, cz + h * 0.12),
         (w * 0.09, 0.05, h * 0.05), eye_mat)
    block(f"{prefix}_Mouth", (cx, cy - 0.06, cz - h * 0.22), (w * 0.3, 0.04, h * 0.03), eye_mat)


# ---------- SET 3: ruang inti NEXUS (RX=80, hitam raksasa) ----------
RX = 80.0
block("NX_Floor", (RX, 0, -0.1), (60, 48, 0.2), WET_GROUND)  # EPIC: lantai reflektif 60x48 m
# Ep 4: dinding belakang = PANEL (bukan dinding padat) — runtuh S4
# (di-key di animate dari wall_collapse). 12 panel samping + 1 panel atas:
# panel penuh 5 m menutup x RX-30..RX-5 dan RX+5..RX+30; strip 2.2 m menutup
# celah gerbang (x RX-5..RX-2.8 dan RX+2.8..RX+5); panel atas 5.6 m menutup
# z 6..16 di atas gerbang. Gerbang 5x6 m (x RX-2.5..RX+2.5, z 0..6) tetap
# terbuka di bawahnya.
for _i in range(5):
    block(f"NX_WallPanel{_i:02d}", (RX - 27.5 + _i * 5.0, 23.8, 8.0), (5.0, 0.4, 16.0), WALL)
    block(f"NX_WallPanel{_i + 7:02d}", (RX + 7.5 + _i * 5.0, 23.8, 8.0), (5.0, 0.4, 16.0), WALL)
block("NX_WallPanel05", (RX - 3.9, 23.8, 8.0), (2.2, 0.4, 16.0), WALL)
block("NX_WallPanel06", (RX + 3.9, 23.8, 8.0), (2.2, 0.4, 16.0), WALL)
block("NX_WallPanelTop", (RX, 23.8, 11.0), (5.6, 0.4, 10.0), WALL)
block("NX_WallL", (RX - 29.8, 0, 8.0), (0.4, 48, 16.0), WALL)
block("NX_WallR", (RX + 29.8, 0, 8.0), (0.4, 48, 16.0), WALL)
block("NX_WallFront", (RX, -23.8, 8.0), (60, 0.4, 16.0), WALL)
# Ep 4: TIDAK ADA wajah NEXUS — langit-langit KOSONG (wajah hologram, mata,
# alis, hidung, mulut, scanline, dan partikel wajah Ep 2/3 DIHAPUS total).
# Yang tersisa di dinding belakang atas: kekosongan + panel gelap.
# partikel digital melayang di ruangan (BIRU — bukan merah; debu cahaya bekas luka)
for i in range(40):
    px = RX + _random2.uniform(-25, 25)
    py = _random2.uniform(-20, 20)
    pz = _random2.uniform(0.5, 14.0)
    _s = _random2.uniform(0.04, 0.10)
    ball(f"NX_Float{i}", (px, py, pz), (_s, _s, _s), CIRCUIT_BLUE)
# kolom GELAP (tidak menyala — NEXUS mati, tidak ada merah di Ep 4)
# EPIC: 12 kolom 14 m — baris luar + baris dalam (depth depan-tengah-belakang).
for i, (ccx, ccy) in enumerate(((-20, -12), (-20, 12), (20, -12), (20, 12),
                                (-10, -6), (-10, 6), (10, -6), (10, 6),
                                (-5, 15), (5, 15), (-5, -18), (5, -18))):
    block(f"NX_Col{i}", (RX + ccx, ccy, 7.0), (1.2, 1.2, 14.0), WALL)
    block(f"NX_ColLight{i}", (RX + ccx, ccy - 0.65 if ccy < 0 else ccy + 0.65, 7.0),
          (0.15, 0.15, 13.6), WALL)
    for _k in range(3):
        block(f"NX_ColStrip{i}_{_k}", (RX + ccx, ccy, 2.4 + _k * 4.0),
              (1.25, 1.25, 0.12), WALL)
# soket core di tengah ruangan (S6: Kairo memasang core) — KECIL + RENDAH +
# GESER ke samping (RX+0.6, -0.6): soket 1.0 m di tengah (RX,0) menutupi badan
# Kairo di shot hero S8 (f1422 v2) dan Kairo menembusnya saat jalan ke gerbang.
cylinder("NX_SocketBase", (RX + 2.5, -3.0, 0.175), 0.32, 0.35, SOCKET_M)
cylinder("NX_SocketTop", (RX + 2.5, -3.0, 0.40), 0.22, 0.10, METAL_SEN2)
block("NX_SocketSlot", (RX + 2.5, -3.0, 0.46), (0.14, 0.14, 0.05), CORE_LINE)
# gerbang cahaya putih di dinding belakang bawah (di bawah langit-langit kosong)
# Ep 4: gerbang TERBUKA PENUH sejak S1 (gate_open=1 konstan, skala X di-key di animate)
_gate_plane = plane("NX_Gate", (RX, 23.55, 3.0), (5.0, 6.0), GATE_M, rot=(math.radians(90), 0, 0))  # EPIC: gerbang 5x6 m
_gate_plane.hide_render = False
block("NX_GateFrameL", (RX - 2.6, 23.5, 3.0), (0.4, 0.5, 6.0), WALL)
block("NX_GateFrameR", (RX + 2.6, 23.5, 3.0), (0.4, 0.5, 6.0), WALL)
block("NX_GateFrameT", (RX, 23.5, 6.1), (5.6, 0.5, 0.4), WALL)

# ---------- kabut (volume) ----------
def haze(name, loc, scale, density):
    m = bpy.data.materials.new(name + "M")
    m.use_nodes = True
    nt = m.node_tree.nodes
    nt.remove(nt["Principled BSDF"])
    vol = nt.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = density
    vol.inputs["Color"].default_value = (0.85, 0.88, 0.95, 1.0)
    m.node_tree.links.new(vol.outputs["Volume"], nt["Material Output"].inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    h = bpy.context.object
    h.name = name
    h.scale = scale
    h.data.materials.append(m)
    return h


if os.environ.get("FS_VOL", "1") == "1":
    haze("NX_Haze", (RX, 0, 6.0), (30, 24, 8), 0.02)  # ruang inti (EPIC: volume 60x48x16)
    haze("CT_Haze", (RX, 55, 6.0), (30, 32, 8), 0.01)  # kota fajar: kabut tipis di balik dinding runtuh

# ---------- karakter vinyl-toy ----------
# Kepala ~40% tinggi (KAIRO 1.8 unit). Karakter menghadap -Y (ke arah kamera default).
# Rig empty dibuat di animate_nexus.py.
CHARS = {}


def make_character(prefix, kind, scale, base, jacket_mat, skin_mat, eye_mat,
                   eye_red_mat=None):
    """kind: kairo | eva | sentinel | res | civ. base=(x,y,z)."""
    s = scale
    bx, by, bz = base
    hip_z = 0.48 * s
    sho_z = 1.12 * s
    sho_x = 0.38 * s * (1.35 if kind == "sentinel" else 1.0)
    head_z = 1.45 * s
    head_r = 0.275 * s * (1.1 if kind == "sentinel" else 1.0)
    head_mat = skin_mat
    # sentinel: mata sensor merah yang bisa dinyalakan via eye_red
    _red = kind == "sentinel"
    eye_r = 0.065 * s if _red else 0.055 * s  # sentinel 0.065 (0.075 terlalu besar/kartun)

    def P(x, y, z):
        return (bx + x, by + y, bz + z)

    body, head, armL, armR, legL, legR = [], [], [], [], [], []
    for side, sx in (("L", -1), ("R", 1)):
        _leg = block(f"{prefix}_Leg{side}", P(0.14 * sx * s, 0, 0.24 * s),
                     (0.17 * s, 0.2 * s, 0.42 * s), PANTS_K if kind in ("kairo", "res") else
                     (SUIT_EVA if kind == "eva" else (METAL_SEN if kind == "sentinel" else JACKET3)))
        _shoe = block(f"{prefix}_Shoe{side}", P(0.14 * sx * s, -0.04 * s, 0.07 * s),
                      (0.2 * s, 0.3 * s, 0.12 * s),
                      BOOTS if kind in ("kairo", "res") else METAL_SEN)
        (legL if side == "L" else legR).extend([_leg, _shoe])
    # torso + detail
    body.append(block(f"{prefix}_Torso", P(0, 0, 0.78 * s), (0.62 * s, 0.5 * s, 0.6 * s), jacket_mat))
    if kind == "kairo":
        # saku dada taktis (kotak pipih — JANGAN kena subsurf, biar tetap crisp)
        for side, sx in (("L", -1), ("R", 1)):
            body.append(block(f"{prefix}_Pocket{side}", P(0.15 * sx * s, -0.26 * s, 0.88 * s),
                              (0.2 * s, 0.03 * s, 0.14 * s), SHIRT))
        # bantalan bahu taktis
        for side, sx in (("L", -1), ("R", 1)):
            body.append(block(f"{prefix}_Pad{side}", P(0.32 * sx * s, 0, 1.08 * s),
                              (0.22 * s, 0.3 * s, 0.1 * s), JACKET))
    if kind == "sentinel":
        for side, sx in (("L", -1), ("R", 1)):
            body.append(block(f"{prefix}_Pad{side}", P(0.52 * sx * s, 0, 1.15 * s),
                              (0.42 * s, 0.36 * s, 0.22 * s), METAL_SEN2))
        # piston sendi bahu
        for side, sx in (("L", -1), ("R", 1)):
            body.append(cylinder(f"{prefix}_Piston{side}", P(sho_x * sx, 0.1 * s, sho_z),
                                 0.05 * s, 0.3 * s, METAL_SEN2, rot=(0, math.radians(90), 0)))
    # lengan (pivot di bahu)
    for side, sx in (("L", -1), ("R", 1)):
        lst = armL if side == "L" else armR
        lst.append(block(f"{prefix}_Arm{side}", P(sho_x * sx, 0, sho_z - 0.28 * s),
                         (0.16 * s, 0.18 * s, 0.5 * s), jacket_mat))
        lst.append(ball(f"{prefix}_Hand{side}", P(sho_x * sx, 0, sho_z - 0.56 * s),
                        (0.09 * s,) * 3, head_mat))
    # kepala + wajah
    head.append(ball(f"{prefix}_Head", P(0, 0, head_z), (head_r, head_r * 0.92, head_r), head_mat))
    if kind == "kairo":
        # rambut hitam pendek (mesh pendek, bukan particle hair)
        head.append(ball(f"{prefix}_Hair", P(0, 0.06 * s, head_z + 0.10 * s),
                         (head_r * 1.02, head_r * 0.95, head_r * 0.75), HAIR_KAI))
        # kerah tinggi jaket
        head.append(block(f"{prefix}_Collar", P(0, 0.05 * s, head_z - 0.24 * s),
                          (0.4 * s, 0.3 * s, 0.14 * s), JACKET))
    if kind == "sentinel":
        # helm / pelat kepala logam + visor
        head.append(ball(f"{prefix}_Helm", P(0, 0.05 * s, head_z + 0.08 * s),
                         (head_r * 1.08, head_r * 1.0, head_r * 0.7), METAL_SEN2))
        head.append(block(f"{prefix}_Visor", P(0, -0.22 * s, head_z + 0.05 * s),
                          (0.34 * s, 0.04 * s, 0.07 * s), SENSOR_OFF))
    eyes_black, eyes_red = [], []
    for side, sx in (("L", -1), ("R", 1)):
        eyes_black.append(ball(f"{prefix}_EyeB{side}", P(0.11 * sx * s, -0.235 * s, head_z + 0.03 * s),
                               (0.055 * s, 0.03 * s, 0.07 * s), eye_mat))
        if eye_red_mat is not None:
            eyes_red.append(ball(f"{prefix}_EyeR{side}", P(0.11 * sx * s, -0.24 * s, head_z + 0.03 * s),
                                 (eye_r, 0.032 * s, eye_r * 1.25), eye_red_mat))
    head.extend(eyes_black)
    head.extend(eyes_red)
    mouth = block(f"{prefix}_Mouth", P(0, -0.25 * s, head_z - 0.13 * s),
                  (0.12 * s, 0.03 * s, 0.03 * s), mat(f"{prefix}_MouthM", (0.10, 0.02, 0.03), 0.3))
    head.append(mouth)
    if kind in ("kairo", "res", "civ"):
        for side, sx in (("L", -1), ("R", 1)):
            head.append(block(f"{prefix}_Brow{side}", P(0.11 * sx * s, -0.25 * s, head_z + 0.13 * s),
                              (0.12 * s, 0.03 * s, 0.03 * s), HAIR_KAI, rot=(0, 0, math.radians(-10 * sx))))
    if kind == "eva":
        # garis circuitry biru di pelipis + "rambut energi" tipis
        for side, sx in (("L", -1), ("R", 1)):
            head.append(block(f"{prefix}_Circuit{side}", P(0.24 * sx * s, -0.1 * s, head_z + 0.1 * s),
                              (0.03 * s, 0.03 * s, 0.16 * s), CIRCUIT_BLUE))
    info = {
        "base": Vector(base), "scale": s, "kind": kind,
        "hip_z": hip_z, "sho_z": sho_z, "sho_x": sho_x, "head_z": head_z,
        "head_pivot_z": 1.18 * s,
        "body": body, "head": head, "armL": armL, "armR": armR,
        "legL": legL, "legR": legR,
        "eyes_black": eyes_black, "eyes_red": eyes_red, "mouth": mouth,
    }
    CHARS[prefix] = info
    return info


make_character("KAI", "kairo", 1.0, (0, 0, 0), JACKET, SKIN_KAI, EYE_DARK)
make_character("EVA", "eva", 1.0, (0, 0, 0), SUIT_EVA, SKIN_EVA, EYE_BLUE)
for _i in range(1, 9):
    make_character(f"SEN{_i}", "sentinel", 1.22, (0, 0, 0), METAL_SEN, METAL_SEN,
                   SENSOR_OFF, SENSOR_RED)
make_character("RES1", "res", 1.0, (0, 0, 0), JACKET2, SKIN_KAI, EYE_DARK)
make_character("RES2", "res", 1.0, (0, 0, 0), JACKET3, SKIN_KAI, EYE_DARK)
make_character("CIV1", "civ", 1.0, (0, 0, 0), JACKET3, SKIN_KAI, EYE_DARK)
make_character("CIV2", "civ", 1.0, (0, 0, 0), JACKET2, SKIN_KAI, EYE_DARK)

# --- bekas luka alis kiri KAIRO (WAJIB terbaca di close-up) ---
# Alis kiri = sisi +X (karakter menghadap -Y: kiri anatomis = +X; konvensi L
# builder zombie (-X) justru sisi kanan). RONDE FIX 1: garis TIPIS warna
# kulit sedikit lebih terang #D8B49A (bukan putih), TANPA emissive — versi
# lama (0.12 x 0.022, emissive 0.15) terbaca seperti plester putih tebal.
SCAR_M = mat("Scar", (0.65, 0.50, 0.40), 0.7)  # FIX R2: lebih gelap lagi
# y=-0.22 (bukan -0.28): permukaan dahi di titik ini y~-0.19 — luka lama
# mengambang ~9 cm di depan kulit sehingga terbaca seperti strip terpisah.
# Kini menempel di kulit (0.04 di depan permukaan), tetap terbaca sebagai garis.
scar = block("KAI_Scar", (0.11, -0.22, 1.60), (0.06, 0.008, 0.006), SCAR_M,  # FIX R2: garis tipis
             rot=(0, 0, math.radians(-25)))
CHARS["KAI"]["head"].append(scar)
CHARS["KAI"]["scar"] = scar
# EPIC Ep 2 — kilau biru bekas luka (S4 ECU saja, SANGAT lemah): glow tipis
# di depan garis luka, di-key via prop scar_glow di animate.
# Ep 4: TERANG sejak frame 0 (lanjutan Ep 3 S6); nama material "ScarGlowM"
# dipakai animate_nexus_ep4.py (scar_flow S7: 6 -> 10).
SCAR_GLOW_M = emissive("ScarGlowM", (0.10, 0.30, 0.90), 6.0)
scar_glow = block("KAI_ScarGlow", (0.11, -0.235, 1.60), (0.07, 0.006, 0.008),
                  SCAR_GLOW_M, rot=(0, 0, math.radians(-25)))
scar_glow.hide_render = True
CHARS["KAI"]["head"].append(scar_glow)
CHARS["KAI"]["scar_glow"] = scar_glow
# Ep 4: TIDAK ADA laser (tidak ada titik merah di tubuh siapa pun).

# --- backpack KAIRO (objek terpisah — dilepas di S6-S8, di-key via props) ---
bp_box = block("KAI_Backpack", (0, 0.32, 0.95), (0.42, 0.2, 0.5), BACKPACK_M)
bp_flap = block("KAI_BackpackFlap", (0, 0.42, 1.12), (0.44, 0.06, 0.16), JACKET)
bp_strip1 = block("KAI_BPStrip1", (0.12, 0.43, 0.95), (0.05, 0.02, 0.34), STRIP_BLUE)
bp_strip2 = block("KAI_BPStrip2", (-0.12, 0.43, 0.95), (0.05, 0.02, 0.34), STRIP_BLUE)
bp_ant = cylinder("KAI_BPAntenna", (0.18, 0.32, 1.35), 0.012, 0.35, POLE)
BACKPACK_OBJS = [bp_box, bp_flap, bp_strip1, bp_strip2, bp_ant]
for _o in BACKPACK_OBJS:
    _o.hide_render = True
# backpack tergeletak di lantai ruang inti (S6-S8)
bp_drop = block("KAI_BackpackDropped", (RX - 2.0, -1.5, 0.18), (0.42, 0.5, 0.2), BACKPACK_M,
                rot=(0, 0, math.radians(15)))
bp_drop.hide_render = True

# --- data core (kubus 12 cm, garis merah berdenyut) — di tangan kanan KAIRO ---
core = block("CoreCube", (0.38, -0.05, 0.56), (0.12, 0.12, 0.12), CORE_BODY)
core_line1 = block("CoreLine1", (0.38, -0.05, 0.56), (0.13, 0.13, 0.02), CORE_LINE)
core_line2 = block("CoreLine2", (0.38, -0.05, 0.56), (0.02, 0.13, 0.13), CORE_LINE)
CORE_OBJS = [core, core_line1, core_line2]
for _o in CORE_OBJS:
    _o.hide_render = True
# core terpasang di soket ruang inti (S6+) — ikut posisi soket geser
core_sock = block("CoreSocketed", (RX + 2.5, -3.0, 0.48), (0.12, 0.12, 0.12), CORE_BODY)
core_sock_l = block("CoreSocketedLine", (RX + 2.5, -3.0, 0.48), (0.13, 0.13, 0.02), CORE_LINE)
CORE_SOCKET_OBJS = [core_sock, core_sock_l]
for _o in CORE_SOCKET_OBJS:
    _o.hide_render = True

# ---------- SET 4: kota fajar (di balik dinding belakang, y 24..90) — set BARU Ep 4 ----------
# Kota di balik dinding runtuh (pusat y~55): jalan sepanjang sumbu X,
# 12 menara (baris depan y=48 + baris belakang y=62, tinggi 5-11 m),
# layar GELAP tanpa wajah (SCREEN_M — tidak ada lagi wajah NEXUS di mana pun),
# jendela hangat (WIN_WARM) + tiang lampu hangat #FFC98A (LampWarm, emisi
# di-key 0 -> 6 di animate dari city_warm S4/S7). Grade hangat, bukan merah.
CT = 55.0  # pusat kota (sumbu Y)
block("CT_Ground", (RX, 57, -0.1), (60, 66, 0.2), WET_GROUND)  # y 24..90 (tidak tumpang tindih lantai ruang inti)
block("CT_Sidewalk", (RX, 40.0, 0.03), (60, 3.0, 0.06), WALL)
# EPIC: 12 menara — baris depan (y=48) + baris belakang menjulang (y=62,
# tinggi 7-11 m) supaya aerial S7 terasa PADAT dan DRAMATIS.
_buildings = [(-13, 48, 5.5, 5), (-7, 48, 7.0, 6), (-1, 48, 6.0, 5),
              (5, 48, 8.0, 6), (11, 48, 6.0, 5), (16, 48, 7.5, 6),
              (-15, 62, 4.0, 8), (-9, 62, 5.0, 10), (-3, 62, 4.5, 7),
              (3, 62, 5.0, 11), (9, 62, 4.5, 8), (15, 62, 5.0, 9)]
for i, (bx, by, bw, bh) in enumerate(_buildings):
    block(f"CT_Bldg{i}", (RX + bx, by, bh / 2), (bw, 3.0, bh), BUILDING if i % 2 == 0 else BUILDING2)
    for wy in range(3):
        for wx in range(int(bw) - 1):
            warm = ((i + wx + wy) % 3) != 0
            plane(f"CT_Win{i}_{wx}_{wy}", (RX + bx - bw / 2 + 0.9 + wx * 1.1, by - 1.52, 1.6 + wy * 2.0),
                  (0.55, 0.8), WIN_WARM if warm else WIN_DARK, rot=(math.radians(90), 0, 0))
# gedung samping (menutup ujung jalan)
block("CT_BldgL", (RX - 29.5, 55, 3.0), (3.0, 60, 6.0), BUILDING2)
block("CT_BldgR", (RX + 29.5, 55, 3.0), (3.0, 60, 6.0), BUILDING)
# layar raksasa GELAP di fasad gedung (S4/S7) — TANPA wajah (Ep 4: wajah hilang)
plane("CT_Screen1", (RX - 7, 46.45, 4.2), (4.5, 3.0), SCREEN_M, rot=(math.radians(90), 0, 0))
plane("CT_Screen2", (RX + 8, 46.45, 4.5), (3.6, 2.4), SCREEN_M, rot=(math.radians(90), 0, 0))
# tiang lampu jalan hangat (x=RX-9,-3,3,9 ; y=40) — kepala LAMP_WARM
for i, lx in enumerate((-9, -3, 3, 9)):
    cylinder(f"CT_LampPole{i}", (RX + lx, 40.0, 1.6), 0.07, 3.2, POLE)
    ball(f"CT_LampHead{i}", (RX + lx, 39.75, 3.25), (0.16, 0.16, 0.12), LAMP_WARM)
# --- 213 Kairo membeku: SATU model beku (collection) di-instans 213x ---
# Instans = linked duplicates model Kairo yang sama (tanpa rig baru, tanpa
# lip-sync, tanpa dialog): pose beku di tengah langkah. Ep 4: mereka SUDAH
# melangkah keluar gerbang — grid DI DALAM ruang inti (x RX-21.0..RX+23.8
# step 2.8 + offset 1.4 supaya tidak ada kolom tepat di jalur Kairo x=RX,
# y 10..22 step 1.0, 213 pertama dari 221 slot). Mata biru TERBUKA + kilau
# scar TERLIHAT sejak frame 0 (lanjutan Ep 3 S6/S7). Penyebaran S6
# (masing-masing ke arah berbeda) di-key di animate dari duplicates_scatter.
KF_COLL = bpy.data.collections.new("KairoFrozen")
bpy.context.scene.collection.children.link(KF_COLL)
_KF = []
_KF.append(block("KF_Torso", (0, 0, 0.78), (0.62, 0.5, 0.6), JACKET))
_KF.append(ball("KF_Head", (0, 0, 1.45), (0.275, 0.253, 0.275), SKIN_KAI))
_KF.append(ball("KF_Hair", (0, 0.06, 1.55), (0.28, 0.26, 0.21), HAIR_KAI))
_KF.append(block("KF_Scar", (0.11, -0.22, 1.60), (0.06, 0.008, 0.006), SCAR_M,
                 rot=(0, 0, math.radians(-25))))
for _sx in (-1, 1):
    _side = "L" if _sx < 0 else "R"
    _KF.append(ball(f"KF_Eye{_side}", (0.11 * _sx, -0.235, 1.48),
                    (0.055, 0.03, 0.07), K213_EYE_M))
    _KF.append(block(f"KF_Arm{_side}", (0.38 * _sx, 0.10 * _sx, 0.84),
                    (0.16, 0.18, 0.5), JACKET))
    _KF.append(block(f"KF_Leg{_side}", (0.14 * _sx, -0.15 if _sx < 0 else 0.12, 0.24),
                    (0.17, 0.2, 0.42), PANTS_K))
    _KF.append(block(f"KF_Shoe{_side}", (0.14 * _sx, -0.19 if _sx < 0 else 0.16, 0.07),
                    (0.2, 0.3, 0.12), BOOTS))
for _o in _KF:
    bpy.context.scene.collection.objects.unlink(_o)
    KF_COLL.objects.link(_o)
K213_BASE = {}
K213_SCAR_GLOW = []
for _idx in range(213):
    _row, _col = divmod(_idx, 17)
    _x = RX - 22.4 + _col * 2.8 + 1.4
    _y = 10.0 + _row * 1.0
    _e = bpy.data.objects.new(f"K213_{_idx:03d}", None)
    bpy.context.scene.collection.objects.link(_e)
    _e.instance_type = "COLLECTION"
    _e.instance_collection = KF_COLL
    _e.location = (_x, _y, 0.0)
    K213_BASE[_e.name] = (_x, _y, 0.0)
    # kilau bekas luka per instans (TERLIHAT sejak frame 0 di Ep 4)
    _sg = dot(f"K213_{_idx:03d}_ScarGlow", (_x + 0.11, _y - 0.24, 1.60), 0.045, SCAR213_M)
    _sg.hide_render = False
    K213_SCAR_GLOW.append(_sg)
assert len(K213_BASE) == 213 and len(K213_SCAR_GLOW) == 213
# --- wajah NEXUS kecil: TIDAK ADA di Ep 4 (daftar kosong, animate tidak key apa-apa) ---
NX_FACE_SMALL_OBJS = []

# ---------- lampu ----------
def point_light(name, loc, color, energy, shadow=False):
    bpy.ops.object.light_add(type="POINT", location=loc)
    o = bpy.context.object
    o.name = name
    o.data.color = color
    o.data.energy = energy
    o.data.shadow_soft_size = 0.5
    o.data.use_shadow = shadow
    return o


def area_light(name, loc, color, energy, size, rot, shadow=False):
    bpy.ops.object.light_add(type="AREA", location=loc)
    o = bpy.context.object
    o.name = name
    o.data.color = color
    o.data.energy = energy
    o.data.size = size
    o.data.use_shadow = shadow
    o.rotation_euler = rot
    return o


# --- ruang inti GELAP (Ep 4: tanpa merah — rim BIRU, nexus/eye = 0) ---
area_light("CoreFill", (RX, -16, 8), (0.62, 0.72, 1.0), 90.0, 16, (math.radians(55), 0, 0))
point_light("RimRedCore", (RX, 10.0, 3.0), (0.30, 0.65, 1.0), 500.0)  # Ep 4: rim BIRU (nama objek warisan Ep 2/3)
point_light("EvaRimCore", (RX + 4, -6, 2.5), (0.30, 0.65, 1.0), 0.0)
point_light("NexusLight", (RX, 16.0, 10.0), (0.30, 0.65, 1.0), 0.0)  # Ep 4: 0 SELALU (wajah hilang)
area_light("GateLight", (RX, 22.5, 3.5), (1.0, 1.0, 0.95), 0.0, 12, (math.radians(90), 0, 0))
# --- kota fajar: cahaya hangat #FFC98A (0 = malam, di-key di animate dari dawn/warm) ---
area_light("DawnLight", (RX, 45, 12), (1.0, 0.79, 0.54), 0.0, 30, (math.radians(120), 0, 0))
point_light("WarmLight", (RX, 55, 6), (1.0, 0.79, 0.54), 0.0)
# glow mata Sentinel (PADAM di Ep 4 — sensor mati) — ikut rig kepala SEN1 di animate
bpy.ops.object.light_add(type="POINT", location=(0, -0.3, 1.8))
eye_glow = bpy.context.object
eye_glow.name = "EyeGlow"
eye_glow.data.color = (0.30, 0.65, 1.0)
eye_glow.data.energy = 0.0
# cahaya data core di soket (BIRU — bukan merah) — ikut lengan kanan KAIRO di animate
bpy.ops.object.light_add(type="POINT", location=(0.38, -0.1, 0.56))
core_light = bpy.context.object
core_light.name = "CoreLight"
core_light.data.color = (0.30, 0.65, 1.0)
core_light.data.energy = 0.0

# ---------- quality pass B7: subsurf 1 di semua bagian karakter, bevel 0 ----------
# Detail pipih (saku, bekas luka, circuitry, visor) TIDAK kena subsurf — kalau
# kena, kotak pipih menggembung jadi bantal (pelajaran still S3 f421: "Shirt"
# jadi heksagon di dada Kairo).
SUB = int(os.environ.get("FS_SUB", "1"))
_NOSUB = ("Pocket", "Scar", "Circuit", "Visor")
for _info in CHARS.values():
    for _part in (_info["body"] + _info["head"] + _info["armL"] + _info["armR"]
                  + _info["legL"] + _info["legR"]):
        if _part.type == "MESH" and SUB > 0 and not any(_k in _part.name for _k in _NOSUB):
            _s = _part.modifiers.new("Subdiv", "SUBSURF")
            _s.levels = 0
            _s.render_levels = SUB
# vinyl: clear-coat ringan
for _m, _coat in ((SKIN_KAI, 0.5), (JACKET, 0.3), (BACKPACK_M, 0.2), (SKIN_EVA, 0.6)):
    _b = _m.node_tree.nodes["Principled BSDF"]
    if "Coat Weight" in _b.inputs:
        _b.inputs["Coat Weight"].default_value = _coat
        _b.inputs["Coat Roughness"].default_value = 0.15

# ---------- kamera default (plan yang menggerakkan per frame) ----------
bpy.ops.object.camera_add(location=(0, -6.5, 1.7))
cam = bpy.context.object
cam.data.lens = 40
look = Vector((0, 0, 1.3)) - cam.location
cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = os.environ.get("FS_DOF", "1") == "1"
cam.data.dof.focus_distance = 6.5
cam.data.dof.aperture_fstop = 2.0
scene.camera = cam

scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
