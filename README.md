# nexus-ep4-render-farm — NEXUS ZERO Episode 4 "WITHOUT YOU"

GitHub Actions render farm (Eevee) untuk Episode 4. Repo dibuat 21 Nov 2026
~14:30 WIB (publik, kosong). Pola mengikuti farm Ep 3, tapi SEMUA file baru
untuk Ep 4 — JANGAN pakai repo/workflow Ep 1/2/3.

## Struktur (yang akan di-push)

```
pipeline-nexus/                 <- isi ~/workspace/shorts/nexus-zero-ep4/pipeline/
  build_scene_nexus_ep4.py      scene: ruang inti GELAP tanpa wajah + kota fajar
  animate_nexus_ep4.py          keyframe plan.json (scatter S6, runtuh S4, fajar)
  plan_nexus_ep4.py             generator plan.json (1440 baris)
  plan.json                     plan jadi (sudah digenerate + self-check lolos)
  validate_build.py             validasi scene TANPA render (Blender)
  encode_nexus_ep4.sh           finalize 4 file (full + lite, 9:16 + 16:9)
  encode_nexus_ep4_cycles.sh    finalize varian Cycles 16:9
  merge_cycles_ep4.sh           gabung 4 job Kaggle -> 1440 frame
  qa_ep4.py / qa_ep4_cycles.py  QA akhir
.github/workflows/
  render-nexus-ep4-test.yml     [DITULIS + PUSH 21 Nov 2026 ~15:50 WIB — 4 job x 6 frame S4, Blender 625-648]
  render-nexus-ep4-full.yml     [DITULIS + PUSH 21 Nov 2026 ~15:50 WIB — 40 job x 72 frame = 2880]
```

PENTING: nama file pipeline memakai sufiks `_ep4` (bukan generik
`animate_nexus.py` seperti farm Ep 3). Workflow + script Kaggle HARUS
memakai nama `animate_nexus_ep4.py` / `build_scene_nexus_ep4.py`
(animate me-load build_scene via namanya sendiri). Script Kaggle sudah
diperbaiki ke nama ini (21 Nov ~15:45 WIB).

## Target render (pola Ep 3)

- Test: 4 job x 6 frame (S5c, 9:16 540x960 lensk 0.62).
- Full: 40 job x 72 frame = 2880 frame (9:16 540x960 lensk 0.62 +
  16:9 960x540 lensk 1.00; plan f 0-1439 -> frame Blender 1-1440).
- Blender 4.5.3, Eevee 6 samples, ray OFF, vol tile 16, DOF ON, MB ON,
  subsurf 1, bevel 0, AgX. Frame dinilai dari file yang ada (bukan exit code).
- Release baru: `nexus-ep4-full-run-<tanggal>` (frame zip per job).

## Status 21 Nov 2026 ~15:40 WIB

- Pipeline + plan.json + audio mix final + Kaggle scripts: SIAP (lokal).
  Kaggle job-a..d diperbaiki 21 Nov ~15:45 WIB (nama file `*_ep4.py`,
  rentang 1–360/361–720/721–1080/1081–1440).
- Repo: dibuat, KOSONG (belum ada push apa pun).
- **Workflow SELESAI:** `render-nexus-ep4-test.yml` + `render-nexus-ep4-full.yml`
  ditulis BARU (pola Ep 3 dibaca lewat `gh api`, bukan clone/copy) dan
  PUSH 21 Nov 2026 ~15:50 WIB atas go-ahead user ("Ya, tulis workflow-nya").
  TIDAK ADA workflow yang di-trigger/run — hanya tulis + push + verifikasi.
- JANGAN posting ke mana pun. Aturan posting NEXUS (diubah user 21 Nov
  14:36 WIB): episode dibalas ke episode SEBELUMNYA (Ep 4 -> balasan ke
  postingan Ep 3 https://x.com/dandelionz313/status/2124044778279203303).
