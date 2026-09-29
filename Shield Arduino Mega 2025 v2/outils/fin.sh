#!/bin/bash
# (chroot) finition seule a partir du PCB route : zones, couture, serigraphie, noms de nets, DRC
cd "$(dirname "$0")" || exit 1
python3 finish_stage.py w/routed_ok.kicad_pcb w/final0.kicad_pcb > w/fin.log 2>&1; grep -v -E 'swig/python|Debug' w/fin.log | tail -2
python3 rename_nets.py w/final0.kicad_pcb w/final.kicad_pcb
cp w/b.kicad_pro w/final.kicad_pro
kicad-cli pcb drc -o w/drc_f.rpt w/final.kicad_pcb >/dev/null
grep -E '^\[' w/drc_f.rpt | sed 's/\].*/]/' | sort | uniq -c
