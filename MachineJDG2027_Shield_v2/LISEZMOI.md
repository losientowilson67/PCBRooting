# Machine JDG 2027 – Shield Mega 2560 PRO v2

Projet KiCad dérivé de `MachineJDG2025_MEGA2560_Shield_VL_2024_12_19`. Le mapping des E/S moteurs, servos S1–S4 et SBUS est inchangé.

## Contenu

| Fichier | Rôle |
|---|---|
| `MachineJDG2027_Shield_v2.kicad_pro/.kicad_sch/.kicad_pcb` | Projet, schéma et PCB |
| `JDG2027.kicad_sym`, `JDG2027.pretty/` | Librairie projet (module Mega, bornier Würth 691214110002) |
| `sym-lib-table`, `fp-lib-table` | Déclarent la librairie projet (chemin `${KIPRJMOD}`) |
| `BOM_JDG2027_v2.csv` | BOM groupée, pièces CMS pour JLC et pièces THT à souder à la main |

Les fichiers sont au format KiCad 7. KiCad 8 les ouvre directement et les convertit à la première sauvegarde.

## État

Le schéma est complet et vérifié (netlist exportée et comparée à la conception, aucune différence). Le PCB (100 × 89 mm, 2 couches) contient toutes les empreintes placées, les nets, les classes de nets et un plan GND plein en B.Cu. **Le routage reste à faire.** Côté placement, le DRC ne trouve aucun conflit sauf le chevauchement voulu des courtyards des headers servo (pas de 2,54 mm, comme un rail servo standard). Il reste des avertissements de sérigraphie (références de petites pièces qui se chevauchent) à nettoyer après le routage.

## Changements par rapport à la discussion

- **Régulateur 6 V.** Le LM22678TJ-5.0 (5 A, 42 V, TO-263-7) remplace le TPS56637. Son empreinte est dans la librairie standard de KiCad, il se soude à la main et il tient les pointes du bus 12 V. Pour 6 V, TI recommande la version -5.0 avec un diviseur externe (R11 = 182 Ω, R12 = 1 kΩ, donc 6,0 V).
- **Relais.** L'Omron G5NB-1A-E DC5V (LCSC C48746) est au même format mince que le HF46F, mais son empreinte KiCad est vérifiée.
- **5 V logique.** Le TPS54202H a un pull-down interne sur EN, d'où R26 (510 kΩ) vers VBAT, sinon le 5 V ne démarre pas.

## Affectation des broches

| Fonction | Broches |
|---|---|
| Moteurs PWM / DIR | M1 D5/D7, M2 D3/D49, M3 D6/D9, M4 D2/D8 (inchangé) |
| Servos | S1 D10, S2 D12, S3 D13, S4 D11 (inchangé), S5 D44, S6 D45 (nouveaux) |
| SBUS | D19 (RX1), via inverseur Q1 |
| Relais | K1 D22, K2 D23 (niveau haut = contact fermé) |
| UART ESP (J14) | TX2 D16 abaissé à 3,3 V par R21/R22, RX2 D17 via 1 kΩ |
| I2C (J15) | SDA D20, SCL D21 |
| Mesure batterie | A0 = VBAT / 4, donc `vbat = analogRead(A0) * 5.0 / 1023 * 4` |
| Extension J16 | A1–A7, D24–D32, 5V et GND |

## Règles de routage

- **Classes de nets** (déjà définies). VBAT* 2,5 mm, +6V 2,0 mm, SW6 1,5 mm, +5V* 0,8 mm, contacts relais 1,5 mm, signaux 0,3 mm. Le tronçon J1 → F1 → bus porte jusqu'à environ 8,5 A. Fais-le en zones d'au moins 6 mm sur une couche, ou 2,5 mm par couche sur les deux.
- **Boucle du buck 6 V.** C10/C11/C12 entre VIN et GND, D2 et L1 au plus court du pin SW, avec beaucoup de vias sous la languette de U2 vers le plan GND.
- **Rétroaction.** R11/R12 près du pin FB, avec la prise +6V sur C14/C15.
- **Sous le module Mega.** Seulement des pièces CMS de moins de 7 mm (embases femelles de 8,5 mm).
- **Contacts relais.** Garde RL1_A/B et RL2_A/B isolés du reste, avec au moins 3 mm si tu commutes plus que de la très basse tension.

## Avant de commander

1. Test moteur. Alimente un moteur avec le fil PWM en l'air. S'il tourne, pose R30–R33 (4,7 kΩ, DNP par défaut).
2. Vérifie le stock LCSC des pièces CMS au moment de la commande (U2 C527397, U3 C527684).
3. JLCPCB, 2 couches, 1,6 mm, 1 oz. Assemblage économique pour les CMS de la face avant. Les borniers, headers, relais, porte-fusible et embases sont à souder à la main.
4. Les headers servo sont maintenant mâles (les SSW de la v2025 étaient des embases femelles).
