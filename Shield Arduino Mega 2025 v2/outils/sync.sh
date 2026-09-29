#!/bin/bash
# Copie le PCB final (w/final.kicad_pcb) dans le projet, donne aux broches NC les nets
# "unconnected-(...)" du schema, puis ERC + DRC avec parite schema/PCB.
# Le schema est genere avant : python3 gen_sch.py <projet>/MachineJDG2025_MEGA2560_Shield_v2.kicad_sch
HERE="$(cd "$(dirname "$0")" && pwd)"
P="${PROJET:-$HERE/../MachineJDG2025_MEGA2560_Shield_v2}"; N=MachineJDG2025_MEGA2560_Shield_v2
cd "$P" || exit 1
kicad-cli sch export netlist -o "$HERE/w/sch.net" $N.kicad_sch >/dev/null
python3 "$HERE/add_nc_nets.py" "$HERE/w/sch.net" "$HERE/w/final.kicad_pcb" $N.kicad_pcb 2>&1 | grep -v -i 'swig\|debug'
cp "$HERE/w/b.kicad_pro" $N.kicad_pro
kicad-cli sch erc -o "$HERE/w/erc_p.rpt" $N.kicad_sch | tail -1
kicad-cli pcb drc --schematic-parity -o "$HERE/w/drc_p.rpt" $N.kicad_pcb | tail -3
grep -E '^\[' "$HERE/w/drc_p.rpt" | sed 's/\].*/]/' | sort | uniq -c
