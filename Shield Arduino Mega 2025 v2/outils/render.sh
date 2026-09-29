#!/bin/bash
# render.sh board.kicad_pcb out.png [layers]
L=${3:-F.Cu,F.Fab,F.Courtyard,Edge.Cuts,F.Silkscreen}
kicad-cli pcb export svg --mode-single --fit-page-to-board --exclude-drawing-sheet --layers "$L" -o /tmp/r.svg "$1" >/dev/null 2>&1 && rsvg-convert -z ${4:-3} -b white /tmp/r.svg -o "$2"
