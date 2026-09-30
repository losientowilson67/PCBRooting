#!/bin/bash
# chaine complete : placement + routage manuel -> autoroutage -> finition -> DRC
cd "$(dirname "$0")" || exit 1
mkdir -p w; [ -e w/JDG2025.pretty ] || cp -r ../MachineJDG2025_MEGA2560_Shield_v2/JDG2025.pretty w/
python3 gen_pcb.py w/b.kicad_pcb | tail -1 || exit 1
timeout 1500 python3 route_stage.py w/b.kicad_pcb ${1:-60} bko2 2>&1 | grep -v -E 'swig|Debug' | tail -1
cp w/b.kicad_pro w/routed.kicad_pro
kicad-cli pcb drc -o w/drc_r.rpt w/routed.kicad_pcb >/dev/null
echo "signaux non connectes : $(awk '/^\[unconnected_items\]/{f=1;next} f&&/^\[/{f=0} f' w/drc_r.rpt | grep '@' | grep -v -E '\[(GND|VBAT|VBAT_IN)\]' | wc -l)"
cp w/routed.kicad_pcb w/routed_ok.kicad_pcb; cp w/b.kicad_pro w/routed_ok.kicad_pro
python3 finish_stage.py w/routed_ok.kicad_pcb w/final0.kicad_pcb > w/fin.log 2>&1; grep -v -E 'swig/python|Debug' w/fin.log | tail -2
python3 rename_nets.py w/final0.kicad_pcb w/final.kicad_pcb
cp w/b.kicad_pro w/final.kicad_pro
kicad-cli pcb drc -o w/drc_f.rpt w/final.kicad_pcb >/dev/null
grep -E '^\[' w/drc_f.rpt | sed 's/\].*/]/' | sort | uniq -c
