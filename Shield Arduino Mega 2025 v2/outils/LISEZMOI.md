# Outils de generation (travail en cours)

Scripts utilises pour generer le schema et le PCB du Shield Mega 2025 v2
avec KiCad 9 (API Python `pcbnew`) et Freerouting.

| Fichier | Role |
|---|---|
| `design.py` | Liste des composants, empreintes et nets (source unique) |
| `gen_sch.py` | Genere le `.kicad_sch` a partir de `design.py` |
| `place.py` | Positions des empreintes (memes connecteurs que le shield 2025) |
| `route.py` | Routage manuel des alimentations, vias de masse, zones, keepouts |
| `gen_pcb.py` | Construit le `.kicad_pcb` (placement + routage manuel) |
| `route_stage.py` | Export DSN, Freerouting, import SES, plans de masse, vias de couture |
| `fab.sh` | Exports Gerbers / percage / BOM / positions |
| `sexp.py`, `dumppads.py`, `render.sh`, `chk.sh` | Utilitaires |

Etat : schema genere et verifie (ERC, netlist), placement fait,
routage des signaux et verification DRC a terminer.
