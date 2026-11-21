#!/bin/bash
# Merge + verifikasi frame Cycles Ep 4 dari 4 job Kaggle.
# Sumber: kaggle/out-cycles-full/out/full_{a,b,c,d}/f_*.png (penomoran GLOBAL:
# a=f_0001..0360, b=f_0361..0720, c=f_0721..1080, d=f_1081..1440).
# Tujuan: kaggle/frames-cycles-16x9/f_0001..f_1440.png (salin, tanpa rename).
# Keluar non-zero bila ada yang kurang / tidak kontigu / PNG rusak.
set -e
NX=~/workspace/shorts/nexus-zero-ep4
SRC=$NX/kaggle/out-cycles-full/out
DST=$NX/kaggle/frames-cycles-16x9
mkdir -p "$DST"
log() { echo "[$(date +%H:%M:%S)] $*"; }
for t in a b c d; do
  n=$(ls "$SRC/full_$t"/f_*.png 2>/dev/null | wc -l)
  log "full_$t: $n/360 frame"
  [ "$n" -eq 360 ] || { log "GAGAL: full_$t kurang frame"; exit 1; }
done
cp "$SRC/full_a"/f_*.png "$SRC/full_b"/f_*.png "$SRC/full_c"/f_*.png "$SRC/full_d"/f_*.png "$DST/"
total=$(ls "$DST"/f_*.png | wc -l)
log "total di $DST: $total/1440"
[ "$total" -eq 1440 ] || { log "GAGAL: total bukan 1440"; exit 1; }
# Kontiguitas f_0001..f_1440
missing=0
for i in $(seq -w 1 1440); do
  [ -f "$DST/f_$i.png" ] || { log "HILANG: f_$i.png"; missing=$((missing+1)); }
done
[ "$missing" -eq 0 ] || { log "GAGAL: $missing frame hilang"; exit 1; }
# PNG valid (header + ukuran > 0)
bad=$(python3 -c "
import glob, os, struct
bad=0
for f in sorted(glob.glob('$DST/f_*.png')):
    try:
        with open(f,'rb') as fh:
            h=fh.read(8)
        if h != b'\x89PNG\r\n\x1a\n' or os.path.getsize(f) < 1000:
            bad+=1; print('RUSAK:', f)
    except Exception as e:
        bad+=1; print('RUSAK:', f, e)
print('bad =', bad)
" | tail -1)
log "cek PNG: $bad"
[ "$bad" = "bad = 0" ] || { log "GAGAL: ada PNG rusak"; exit 1; }
log "MERGE LOLOS — 1440/1440 frame, kontigu, PNG valid"
du -sh "$DST"
