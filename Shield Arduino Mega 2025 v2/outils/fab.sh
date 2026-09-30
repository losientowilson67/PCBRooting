#!/bin/bash
# Exports de fabrication (dans le chroot) : Gerbers, percage, positions, BOM JLC, PDF schema, rendus.
# Usage : fab.sh <dossier projet>
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
P="$1"
N=MachineJDG2025_MEGA2560_Shield_v2
cd "$P"
OUT=fabrication
rm -rf "$OUT"; mkdir -p "$OUT/gerbers"
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --use-drill-file-origin -o "$OUT/gerbers/" $N.kicad_pcb >/dev/null
kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 \
  -o "$OUT/gerbers/" $N.kicad_pcb >/dev/null
(cd "$OUT/gerbers" && rm -f ../${N}_gerbers_JLCPCB.zip && python3 -m zipfile -c ../${N}_gerbers_JLCPCB.zip *)
kicad-cli pcb export pos --side front --format csv --units mm --exclude-dnp --use-drill-file-origin -o "$OUT/positions_raw.csv" $N.kicad_pcb >/dev/null
kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},LCSC,MPN,Montage' \
  --labels 'Designator,Comment,Footprint,Quantity,LCSC Part #,MPN,Montage' --group-by 'Value,Footprint,LCSC,MPN' \
  --exclude-dnp -o "$OUT/bom_raw.csv" $N.kicad_sch >/dev/null
kicad-cli sch export pdf -o "$OUT/${N}_schema.pdf" $N.kicad_sch >/dev/null
kicad-cli pcb export pdf --layers F.Cu,F.Silkscreen,F.Fab,Edge.Cuts --mode-single -o "$OUT/${N}_dessus.pdf" $N.kicad_pcb >/dev/null || true
python3 "$HERE/jlc.py" "$OUT"
echo fab ok
