# animate_nexus_ep4.py — mainkan plan.json NEXUS ZERO Episode 4 "WITHOUT YOU" di Blender.
# Pola: animate_nexus_ep3.py. Bangun scene dari build_scene_nexus_ep4.py (exec s.d.
# scene.render.filepath = OUT), kelompokkan bagian karakter ke rig empty, keyframe
# tiap frame dari plan.json (interpolasi LINEAR), lalu render per rentang frame.
# Usage:
#   blender -b --factory-startup -P animate_nexus_ep4.py -- <out_dir> --start N --end N \
#       --plan plan.json --res 540 960 --lensk 0.62 [--engine eevee|cycles]
#   9:16: --res 540 960 --lensk 0.62 ; 16:9: --res 960 540 --lensk 1.00
#   Frame Blender = f + 1 (plan f 0-based). --start/--end = nomor frame Blender.
#   Cycles: device GPU, samples 32, denoising OPENIMAGEDENOISE, CUDA only.
# Ep 4: gerbang TERBUKA PENUH (gate_open=1 konstan); scar glow TERANG + mata 213
# biru sejak frame 0 (lanjutan Ep 3); TIDAK ADA laser, TIDAK ADA wajah NEXUS,
# TIDAK ADA merah (sensor Sentinel PADAM, lampu nexus/eye = 0 selalu); dinding
# belakang RUNTUH S4 (panel NX_WallPanel jatuh); 213 Kairo MENYEBAR S6
# (masing-masing ke arah berbeda, golden-angle); langit FAJAR S4+ (world bg
# hangat); lampu kota hangat menyala S4/S7 (LampWarm); scar mengalir S7
# (ScarGlowM 6 -> 10).
import bpy
import json
import math
import os
import sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = args[0] if args else HERE + "/frames"
START = int(args[args.index("--start") + 1]) if "--start" in args else 1
END = int(args[args.index("--end") + 1]) if "--end" in args else 1440
PLAN = args[args.index("--plan") + 1] if "--plan" in args else HERE + "/plan.json"
LENSK = float(args[args.index("--lensk") + 1]) if "--lensk" in args else 0.62
ENGINE = args[args.index("--engine") + 1] if "--engine" in args else "eevee"
assert ENGINE in ("eevee", "cycles"), f"--engine harus eevee|cycles, dapat {ENGINE!r}"

# Build the scene without its still render (build_scene_nexus.py reads OUT and --res from sys.argv)
sys.argv = [sys.argv[0], "--", OUT_DIR + "/unused.png"] + (
    ["--res"] + args[args.index("--res") + 1:args.index("--res") + 3] if "--res" in args else [])
src = open(os.path.join(HERE, "build_scene_nexus_ep4.py"), encoding="utf-8").read().split(
    "scene.render.filepath = OUT")[0]
exec(src)

# ---------- engine switch (scene harus engine-agnostic) ----------
if ENGINE == "cycles":
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    _cprefs = bpy.context.preferences.addons["cycles"].preferences
    _cprefs.compute_device_type = "CUDA"
    _cprefs.get_devices()
    for _d in _cprefs.devices:
        _d.use = (_d.type == "CUDA")
    print("CYCLES DEVICES:", [(d.name, d.type, d.use) for d in _cprefs.devices], flush=True)
    print("CYCLES SETTINGS: device=%s samples=%s denoiser=%s" % (
        scene.cycles.device, scene.cycles.samples, scene.cycles.denoiser), flush=True)
else:
    print("EEVEE SETTINGS: samples=%s raytracing=%s vol_tile=%s" % (
        scene.eevee.taa_render_samples,
        getattr(scene.eevee, "use_raytracing", None),
        getattr(scene.eevee, "volumetric_tile_size", None)), flush=True)

plan = [json.loads(line) for line in open(PLAN, encoding="utf-8") if line.strip()]
objs = bpy.data.objects
bpy.context.view_layer.update()

# ---------- Ep 4 globals: panel dinding runtuh, lampu kota hangat, scar flow, langit fajar ----------
_wall_panels = sorted([o for o in objs if o.name.startswith("NX_WallPanel")],
                      key=lambda o: o.name)
_wall_panel_base = {o.name: tuple(o.location) for o in _wall_panels}
_lamp_warm_bsdfs = []
if "LampWarm" in bpy.data.materials:
    _lamp_warm_bsdfs = [bpy.data.materials["LampWarm"].node_tree.nodes["Principled BSDF"]]
_scar_glow_bsdfs = []
if "ScarGlowM" in bpy.data.materials:
    _scar_glow_bsdfs = [bpy.data.materials["ScarGlowM"].node_tree.nodes["Principled BSDF"]]
_world_bg = None
try:
    _world_bg = bpy.data.worlds["World"].node_tree.nodes["Background"]
except Exception:
    _world_bg = None


def _lerp(a, b, t):
    return a + (b - a) * t


def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(e)
    e.location = loc
    if parent is not None:
        e.parent = parent
        e.location = Vector(loc) - parent.location
    bpy.context.view_layer.update()
    return e


def attach(obj, rig):
    m = obj.matrix_world.copy()
    obj.parent = rig
    obj.matrix_world = m


# ---------- rig per karakter: RootRig + HeadRig + ArmRigL/R + LegRigL/R ----------
RIGS = {}
for prefix, info in CHARS.items():
    base = info["base"]
    root = empty(f"{prefix}_RootRig", (base.x, base.y, base.z))
    head_rig = empty(f"{prefix}_HeadRig", (base.x, base.y, base.z + info["head_pivot_z"]), root)
    arm_r = empty(f"{prefix}_ArmRigR", (base.x + info["sho_x"], base.y, base.z + info["sho_z"]), root)
    arm_l = empty(f"{prefix}_ArmRigL", (base.x - info["sho_x"], base.y, base.z + info["sho_z"]), root)
    leg_r = empty(f"{prefix}_LegRigR", (base.x + 0.14 * info["scale"], base.y, base.z + info["hip_z"]), root)
    leg_l = empty(f"{prefix}_LegRigL", (base.x - 0.14 * info["scale"], base.y, base.z + info["hip_z"]), root)
    for o in info["body"]:
        attach(o, root)
    for o in info["head"]:
        attach(o, head_rig)
    for o in info["armR"]:
        attach(o, arm_r)
    for o in info["armL"]:
        attach(o, arm_l)
    for o in info["legR"]:
        attach(o, leg_r)
    for o in info["legL"]:
        attach(o, leg_l)
    RIGS[prefix] = {"root": root, "head": head_rig, "armR": arm_r, "armL": arm_l,
                    "legR": leg_r, "legL": leg_l, "info": info,
                    "parts": (info["body"] + info["head"] + info["armR"] + info["armL"]
                              + info["legR"] + info["legL"])}

# EyeGlow (mata Sentinel ECU) ikut kepala SEN1; CoreLight ikut lengan kanan KAIRO
attach(objs["EyeGlow"], RIGS["SEN1"]["head"])
attach(objs["CoreLight"], RIGS["KAI"]["armR"])
# Backpack KAIRO ikut root rig (bukan bagian body — di-key via props)
for _o in BACKPACK_OBJS:
    attach(_o, RIGS["KAI"]["root"])
# Data core di tangan kanan KAIRO (ikut ArmRigR)
for _o in CORE_OBJS:
    attach(_o, RIGS["KAI"]["armR"])
eye_glow = objs["EyeGlow"]
core_light = objs["CoreLight"]
core_socket_objs = CORE_SOCKET_OBJS
backpack_dropped = objs["KAI_BackpackDropped"]

# drift partikel NEXUS (noise pelan, DESIGN: wajah TIDAK pernah diam): driver
# sin per titik pada NX_Dot*/NX_Float* — tanpa keyframe, dievaluasi dari nomor
# frame absolut, jadi aman untuk farm per-chunk (tidak ada key yang terpotong).
import random as _rnd
_rnd.seed(99)
for _o in list(objs):
    if _o.name.startswith("NX_Dot") or _o.name.startswith("NX_Float"):
        _base = tuple(_o.location)
        for _axis in range(3):
            _amp = _rnd.uniform(0.04, 0.12)
            _fr = _rnd.uniform(0.015, 0.04)
            _ph = _rnd.uniform(0.0, 6.283)
            _drv = _o.driver_add("location", _axis).driver
            _drv.type = "SCRIPTED"
            _drv.expression = f"{_base[_axis]:.4f} + {_amp:.4f}*sin(frame*{_fr:.4f} + {_ph:.4f})"

# lampu: satu key plan bisa menggerakkan beberapa objek (rim/fill/nexus per set)
# Ep 4: nexus/gate/rim/eye/core/eva/fill (ruang inti) + dawn (cahaya fajar
# hangat) + warm (lampu kota hangat). nexus/eye = 0 SELALU (wajah hilang,
# sensor padam). rim = rim BIRU (objek RimRedCore diwarnai ulang biru di
# build_scene Ep 4). TIDAK ADA hall/hallred/laser.
LIGHT_KEYS = {"nexus": ["NexusLight"], "gate": ["GateLight"],
              "rim": ["RimRedCore"], "eye": ["EyeGlow"],
              "core": ["CoreLight"], "eva": ["EvaRimCore"],
              "fill": ["CoreFill"],
              "dawn": ["DawnLight"], "warm": ["WarmLight"]}

# Pre-key di frame START: skala gerbang + state 213 Kairo + panel dinding +
# langit fajar — chunk farm yang mulai di tengah tidak menggantung di state
# yang salah.
_gate0 = objs["NX_Gate"]
_row_start = next((r for r in plan if r["f"] + 1 == START), plan[0])
_gate0.scale = (max(_row_start.get("gate_open", 0.0), 0.0), 1.0, 1.0)
_gate0.keyframe_insert("scale", frame=START)
# mata 213 Kairo: emisi material K213Eye (0 = tertutup, 1.5 = terbuka biru) —
# Ep 4: TERBUKA sejak frame 0 (lanjutan Ep 3 S7).
_eye_bsdf = bpy.data.materials["K213Eye"].node_tree.nodes["Principled BSDF"]
_eye_bsdf.inputs["Emission Strength"].default_value = (
    1.5 if _row_start["props"].get("kairo213_eyes") else 0.0)
_eye_bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=START)
_last_eyes = bool(_row_start["props"].get("kairo213_eyes"))
# Ep 4: posisi 213 Kairo di START = posisi dasar (scatter=0); scatter di-key
# per frame di loop (S6).
for _nm, (_bx, _by, _bz) in K213_BASE.items():
    _o = objs[_nm]
    _o.location = (_bx, _by, _bz)
    _o.keyframe_insert("location", frame=START)
# Ep 4: kilau scar 213 Kairo TERLIHAT sejak frame 0 (lanjutan Ep 3 S6) —
# tidak ada gelombang lagi.
for _o in K213_SCAR_GLOW:
    _o.hide_render = False
    _o.keyframe_insert("hide_render", frame=START)
# Ep 4: panel dinding belakang di START = tegak di posisi dasar (runtuh S4
# di-key per frame di loop).
for _p in _wall_panels:
    _bx, _by, _bz = _wall_panel_base[_p.name]
    _p.location = (_bx, _by, _bz)
    _p.rotation_euler = (0.0, 0.0, 0.0)
    _p.keyframe_insert("location", frame=START)
    _p.keyframe_insert("rotation_euler", frame=START)
# Ep 4: langit fajar di START = malam (dawn=0); lampu kota hangat mati (0);
# scar glow 6.0 (naik ke 10 saat scar_flow S7).
if _world_bg is not None:
    _world_bg.inputs["Color"].default_value = (0.055, 0.059, 0.067, 1.0)
    _world_bg.inputs["Strength"].default_value = 0.45
    _world_bg.inputs["Color"].keyframe_insert("default_value", frame=START)
    _world_bg.inputs["Strength"].keyframe_insert("default_value", frame=START)
for _bsdf in _lamp_warm_bsdfs:
    _bsdf.inputs["Emission Strength"].default_value = 0.0
    _bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=START)
for _bsdf in _scar_glow_bsdfs:
    _bsdf.inputs["Emission Strength"].default_value = 6.0
    _bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=START)
# wajah NEXUS kecil: TIDAK ADA di Ep 4 (nexus_face = False selalu) — daftar
# kosong, loop tidak melakukan apa-apa.
_last_face_vis = bool(_row_start["props"].get("nexus_face"))
for _o in NX_FACE_SMALL_OBJS:
    _o.hide_render = not _last_face_vis
    _o.keyframe_insert("hide_render", frame=START)

# ---------- key every frame in range ----------
_last_vis = {}   # (prefix) -> bool, key hide_render hanya saat berubah
_last_eye = {}   # (prefix) -> eye_red bool
_last_prop = {}  # (prop name) -> bool
for row in plan:
    fr = row["f"] + 1
    if fr < START or fr > END:
        continue
    for prefix, rig in RIGS.items():
        c = row["chars"][prefix]
        root = rig["root"]
        # visibilitas: key hide_render semua bagian hanya saat berubah (hemat fcurve)
        if _last_vis.get(prefix) != c["vis"]:
            for o in rig["parts"]:
                o.hide_render = not c["vis"]
                o.keyframe_insert("hide_render", frame=fr)
            _last_vis[prefix] = c["vis"]
            # saat muncul kembali, key ulang state mata (kalau tidak, mata hitam
            # + merah bisa sama-sama terlihat karena toggle hanya key saat berubah)
            if c["vis"]:
                for o in rig["info"]["eyes_black"]:
                    o.hide_render = c["eye_red"]
                    o.keyframe_insert("hide_render", frame=fr)
                for o in rig["info"]["eyes_red"]:
                    o.hide_render = not c["eye_red"]
                    o.keyframe_insert("hide_render", frame=fr)
                _last_eye[prefix] = c["eye_red"]
        if not c["vis"]:
            continue
        info = rig["info"]
        # root: posisi + lean/pitch (rotasi X) + rotasi Z + squash + crouch
        root.location = (c["x"], c["y"], c["z"] - 0.30 * c["crouch"] * info["scale"])
        root.rotation_euler = (math.radians(c["lean"] + c["pitch"]), 0.0, math.radians(c["rot"]))
        root.scale = (1.0 / math.sqrt(c["squash"]), 1.0 / math.sqrt(c["squash"]), c["squash"])
        for prop in ("location", "rotation_euler", "scale"):
            root.keyframe_insert(prop, frame=fr)
        rig["head"].rotation_euler = (math.radians(c["head_tilt"]), 0.0, math.radians(c["head_turn"]))
        rig["head"].keyframe_insert("rotation_euler", frame=fr)
        # lengan/kaki: sudut plan positif = ayun ke depan (-Y); rotasi X negatif
        rig["armR"].rotation_euler = (math.radians(-c["armR"]), 0.0, 0.0)
        rig["armL"].rotation_euler = (math.radians(-c["armL"]), 0.0, 0.0)
        rig["legR"].rotation_euler = (math.radians(-c["legR"]), 0.0, 0.0)
        rig["legL"].rotation_euler = (math.radians(-c["legL"]), 0.0, 0.0)
        for r in (rig["armR"], rig["armL"], rig["legR"], rig["legL"]):
            r.keyframe_insert("rotation_euler", frame=fr)
        # mata: hitam <-> merah (key hanya saat berubah)
        if _last_eye.get(prefix) != c["eye_red"]:
            for o in info["eyes_black"]:
                o.hide_render = c["eye_red"]
                o.keyframe_insert("hide_render", frame=fr)
            for o in info["eyes_red"]:
                o.hide_render = not c["eye_red"]
                o.keyframe_insert("hide_render", frame=fr)
            _last_eye[prefix] = c["eye_red"]
        # mulut: senyum (S8) via skala
        m = info["mouth"]
        m.scale = (c["mouthW"], 1.0, c["mouthH"])
        m.keyframe_insert("scale", frame=fr)
    # lampu: energi per frame
    for key, objnames in LIGHT_KEYS.items():
        for objname in objnames:
            o = objs.get(objname)
            if o is None:
                continue
            o.data.energy = row["lights"][key]
            o.data.keyframe_insert("energy", frame=fr)
    # props
    p = row["props"]

    def _key_prop(name, value, obj_list):
        if _last_prop.get(name) != value:
            for _o in obj_list:
                _o.hide_render = not value
                _o.keyframe_insert("hide_render", frame=fr)
            _last_prop[name] = value

    _key_prop("core_in_hand", p.get("core_in_hand", False), CORE_OBJS)
    _key_prop("core_socket", p.get("core_socket", False), core_socket_objs)
    _key_prop("backpack", p.get("backpack", False), BACKPACK_OBJS)
    _key_prop("backpack_dropped", p.get("backpack_dropped", False), [backpack_dropped])
    # Ep 4: kilau biru bekas luka Kairo TERANG sejak frame 0 (lanjutan Ep 3 S6).
    # TIDAK ADA laser di Ep 4.
    _key_prop("scar_glow", p.get("scar_glow", False), [objs["KAI_ScarGlow"]])
    # Ep 4: mata 213 Kairo TERBUKA sejak frame 0 (emisi 1.5 konstan) — blok
    # ini hanya meng-key kalau props berubah (tidak pernah di Ep 4).
    _eyes_now = bool(p.get("kairo213_eyes", False))
    if _eyes_now != _last_eyes:
        _eye_bsdf.inputs["Emission Strength"].default_value = 1.5 if _eyes_now else 0.0
        _eye_bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=fr)
        _last_eyes = _eyes_now
    # Ep 4: gerbang TERBUKA PENUH sejak S1 (gate_open = 1 konstan) — skala X
    # tetap di-key per frame dari plan supaya chunk farm konsisten.
    _go = row.get("gate_open", 0.0)
    _gate = objs["NX_Gate"]
    _gate.scale = (max(_go, 0.0), 1.0, 1.0)
    _gate.keyframe_insert("scale", frame=fr)
    # Ep 4: penyebaran 213 Kairo S6 — di-key PER FRAME (chunk farm aman):
    # tiap instans ke arah berbeda (golden-angle spiral + bias ke gerbang/
    # kota), jarak 0.5..2.5 m * duplicates_scatter.
    _sc = row.get("duplicates_scatter", 0.0) or 0.0
    for _idx, (_nm, (_bx, _by, _bz)) in enumerate(K213_BASE.items()):
        _o = objs[_nm]
        _ang = _idx * 2.399963
        _rr = 0.5 + (_idx % 5) * 0.5
        _o.location = (_bx + math.cos(_ang) * _rr * _sc,
                       _by + (math.sin(_ang) * _rr + _rr * 0.4) * _sc, _bz)
        _o.keyframe_insert("location", frame=fr)
    # Ep 4: dinding belakang RUNTUH S4 — panel jatuh ke depan (+Y) sambil
    # tenggelam, di-key per frame dari wall_collapse.
    _wc = row.get("wall_collapse", 0.0) or 0.0
    for _p in _wall_panels:
        _bx, _by, _bz = _wall_panel_base[_p.name]
        _p.location = (_bx, _by + 3.0 * _wc, _bz - 6.0 * _wc)
        _p.rotation_euler = (1.1 * _wc, 0.0, 0.0)
        _p.keyframe_insert("location", frame=fr)
        _p.keyframe_insert("rotation_euler", frame=fr)
    # Ep 4: langit FAJAR S4+ — world background malam -> hangat.
    _dw = row.get("dawn", 0.0) or 0.0
    if _world_bg is not None:
        _world_bg.inputs["Color"].default_value = (
            _lerp(0.055, 0.45, _dw), _lerp(0.059, 0.30, _dw),
            _lerp(0.067, 0.18, _dw), 1.0)
        _world_bg.inputs["Strength"].default_value = _lerp(0.45, 0.9, _dw)
        _world_bg.inputs["Color"].keyframe_insert("default_value", frame=fr)
        _world_bg.inputs["Strength"].keyframe_insert("default_value", frame=fr)
    # Ep 4: lampu kota hangat menyala S4/S7 (LampWarm 0 -> 6).
    _cw = row.get("city_warm", 0.0) or 0.0
    for _bsdf in _lamp_warm_bsdfs:
        _bsdf.inputs["Emission Strength"].default_value = 6.0 * _cw
        _bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=fr)
    # Ep 4: scar mengalir ke grid S7 (ScarGlowM 6 -> 10).
    _sf = row.get("scar_flow", 0.0) or 0.0
    for _bsdf in _scar_glow_bsdfs:
        _bsdf.inputs["Emission Strength"].default_value = 6.0 + 4.0 * _sf
        _bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=fr)
    # Ep 4: wajah NEXUS kecil TIDAK ADA (nexus_face = False selalu, daftar
    # NX_FACE_SMALL_OBJS kosong) — blok ini tidak melakukan apa-apa.
    _face_now = bool(p.get("nexus_face", False)) and (fr // 4) % 2 == 0
    if _face_now != _last_face_vis:
        _last_face_vis = _face_now
        for _o in NX_FACE_SMALL_OBJS:
            _o.hide_render = not _face_now
            _o.keyframe_insert("hide_render", frame=fr)
    # kamera dari plan: posisi, bidik target, fokus, lens, roll (Dutch)
    cm = row["cam"]
    cam.location = (cm["x"], cm["y"], cm["z"])
    _q = (Vector((cm["tx"], cm["ty"], cm["tz"])) - cam.location).to_track_quat("-Z", "Y")
    _roll = math.radians(cm.get("roll", 0.0))
    if _roll:
        from mathutils import Quaternion
        _q = _q @ Quaternion((0.0, 0.0, 1.0), _roll)
    cam.rotation_euler = _q.to_euler()
    cam.data.dof.focus_distance = cm["focus"]
    cam.data.lens = cm["lens"] * LENSK
    cam.keyframe_insert("location", frame=fr)
    cam.keyframe_insert("rotation_euler", frame=fr)
    cam.data.keyframe_insert("dof.focus_distance", frame=fr)
    cam.data.keyframe_insert("lens", frame=fr)

# baked per frame: tanpa easing antar key
for ob in bpy.data.objects:
    ad = ob.animation_data
    if ad and ad.action:
        for fc in getattr(ad.action, "fcurves", []):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
# data lampu (energy) juga LINEAR
for ob in list(objs):
    ad = getattr(ob, "animation_data", None)
    if ad and ad.action:
        for fc in getattr(ad.action, "fcurves", []):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
for ob in [o.data for o in objs if o.type == "LIGHT"]:
    ad = getattr(ob, "animation_data", None)
    if ad and ad.action:
        for fc in getattr(ad.action, "fcurves", []):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"

# material K213Eye / LampWarm / ScarGlowM + world background (langit fajar):
# interpolasi LINEAR juga (mata terbuka SEKETIKA, bukan merayap naik lewat
# easing Bezier)
for _mname in ("K213Eye", "LampWarm", "ScarGlowM"):
    _m = bpy.data.materials.get(_mname)
    if _m is None:
        continue
    _ad = getattr(_m, "animation_data", None)
    if _ad and _ad.action:
        for _fc in getattr(_ad.action, "fcurves", []):
            for _kp in _fc.keyframe_points:
                _kp.interpolation = "LINEAR"
_w = bpy.data.worlds.get("World")
if _w is not None:
    _ad = getattr(_w.node_tree, "animation_data", None)
    if _ad and _ad.action:
        for _fc in getattr(_ad.action, "fcurves", []):
            for _kp in _fc.keyframe_points:
                _kp.interpolation = "LINEAR"

scene.frame_start = START
scene.frame_end = END
scene.render.fps = 24
scene.render.fps_base = 1.0
scene.render.filepath = OUT_DIR + "/f_"
scene.render.image_settings.file_format = "PNG"
print("RENDER", ENGINE, START, END, "->", OUT_DIR)
bpy.ops.render.render(animation=True)
print("DONE_ANIM")
