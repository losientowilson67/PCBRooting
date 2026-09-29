#!/bin/bash
# plusieurs essais Freerouting, on garde le meilleur (moins de liaisons signal manquantes)
cd "$(dirname "$0")" || exit 1
for n in 1 2 3 4 5; do
  timeout 1500 python3 route_stage.py w/b.kicad_pcb 60 bko2 >/dev/null 2>&1
  kicad-cli pcb drc -o w/drc_$n.rpt w/routed.kicad_pcb >/dev/null 2>&1
  u=$(awk '/^\[unconnected_items\]/{f=1;next} f&&/^\[/{f=0} f' w/drc_$n.rpt | grep "@" | grep -v -E "\[(GND|VBAT|VBAT_IN)\]" | wc -l)
  cp w/routed.kicad_pcb w/routed_$n.kicad_pcb
  echo "essai $n : $u extremites non connectees"
done
