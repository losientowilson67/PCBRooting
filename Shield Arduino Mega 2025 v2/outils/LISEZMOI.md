# Outils de génération – Shield Mega 2025 v2

Scripts qui produisent le schéma, le PCB et les fichiers de fabrication de
`../MachineJDG2025_MEGA2560_Shield_v2/`. Ils utilisent KiCad 9 (`kicad-cli` et l'API Python
`pcbnew`) et Freerouting 2.4 (Java 25). Toute modification de la carte se fait dans les scripts,
puis on relance la chaîne.

## Fichiers

| Fichier | Rôle |
|---|---|
| `design.py` | Source unique : composants, empreintes, valeurs, codes LCSC/MPN, nets |
| `place.py` | Position et rotation de chaque empreinte (connecteurs aux places du shield 2025) |
| `route.py` | Pistes et vias posés à la main (alimentations, bus moteurs, couloirs B.Cu), zones de puissance, sérigraphie |
| `gen_sch.py` | Génère le `.kicad_sch` depuis `design.py` |
| `gen_pcb.py` | Construit le PCB de départ (contour, empreintes, routage manuel, règles et classes de nets) |
| `route_stage.py` | Export DSN → Freerouting → import SES (les nets GND/VBAT restent aux plans) |
| `finish_stage.py` | Sérigraphie, zones de puissance, plans GND, vias de couture, origine de perçage |
| `rename_nets.py` | Nomme les nets comme le schéma (`/V12`…) |
| `add_nc_nets.py` | Donne aux broches NC les nets `unconnected-(…)` du schéma et relie les broches empilées du module |
| `jlc.py` | Convertit la BOM et les positions KiCad au format JLCPCB (CMS seulement) |
| `build.sh` | Chaîne PCB complète : `gen_pcb` → Freerouting → finition → DRC (résultat : `w/final.kicad_pcb`) |
| `multi.sh` | Plusieurs essais Freerouting, pour garder le meilleur |
| `fin.sh` | Refait seulement la finition depuis `w/routed_ok.kicad_pcb` |
| `sync.sh` | Copie `w/final.kicad_pcb` dans le projet, puis ERC et DRC avec parité schéma/PCB |
| `fab.sh` | Gerbers, perçages, positions, BOM, PDF, fichiers JLC → `fabrication/` |
| `render.sh`, `chk.sh`, `dumppads.py`, `sexp.py` | Utilitaires : rendu, contrôle de placement, liste des pastilles, lecteur S-expr |

## Utilisation

Variables facultatives : `KICAD9_SYMBOL_DIR`, `KICAD9_FOOTPRINT_DIR` (bibliothèques KiCad,
par défaut `/usr/share/kicad/...`) et `FREEROUTING_JAR`.

```bash
cd "Shield Arduino Mega 2025 v2/outils"
P=../MachineJDG2025_MEGA2560_Shield_v2
python3 gen_sch.py $P/MachineJDG2025_MEGA2560_Shield_v2.kicad_sch   # schéma
./build.sh 60            # PCB : 60 passes Freerouting (~10-25 min), fichiers de travail dans w/
./sync.sh                # copie dans le projet + ERC + DRC parité
./fab.sh $P              # sorties de fabrication
```

Freerouting n'est pas déterministe. Si `build.sh` annonce des signaux non connectés,
le relancer ou passer par `multi.sh`, puis copier le meilleur `w/routed_N.kicad_pcb`
vers `w/routed_ok.kicad_pcb` et lancer `fin.sh`.

## Résultat attendu

- ERC : 0 erreur, 0 avertissement.
- DRC : 0 erreur d'isolation, 0 connexion manquante.
  Restent 4 recouvrements de courtyard, entre borniers accolés comme sur le shield 2025.
- Parité : 6 avertissements, pour les broches ICSP du symbole du module qui n'ont pas de pastille.
