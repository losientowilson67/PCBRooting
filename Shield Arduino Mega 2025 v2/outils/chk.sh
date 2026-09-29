#!/bin/bash
# chk.sh : regenere le PCB, liste les chevauchements hors borniers empiles, rend l'image
cd "$(dirname "$0")" || exit 1
python3 gen_pcb.py /scratch/w/b.kicad_pcb >/dev/null || exit 1
kicad-cli pcb drc -o w/drc.rpt w/b.kicad_pcb >/dev/null
grep -A4 courtyards_overlap w/drc.rpt | grep -E '@' | paste - - | grep -v -E 'J(2|3|4|5|8|9|10|11)\b.*J(2|3|4|5|8|9|10|11)\b'
[ -n "$1" ] && python3 dumppads.py w/b.kicad_pcb "$1" | grep -v -E '^\s+\(|^$'
./render.sh w/b.kicad_pcb w/b.png
