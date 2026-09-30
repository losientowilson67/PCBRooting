# Shield JDG2025 v1.1 : protections et passage en CMS

Révision du schéma `MachineJDG2025_MEGA2560_Shield_VL_2024_12_19` (KiCad 10). Le mapping des moteurs, des servos S1–S4 et du SBUS ne change pas ; deux servos (S5, S6) sont ajoutés. **Le PCB n'a pas été modifié** : le `.kicad_pcb` de ce dossier est ton fichier `_bu` tel quel.

## Changements dans le schéma

| Bloc | Changement |
|---|---|
| Entrée 12 V | J1 devient un **XT60PW-M** (broche 1 = −, broche 2 = +). Il est suivi de **Q2 AOD4185** (anti-inversion : D côté batterie, S côté 12V), de **D1 BZT52C15** + **R7 47k** sur la grille, de la **TVS D2 SMBJ14A** et de **C1 470 µF 35 V**. Le fusible de 15 A est en ligne sur le fil de batterie, hors PCB. |
| Régulateurs | U2 et U3 deviennent des **modules XL4005 5 A** (carte 43 × 21 mm type DSN5000, même format que le module LM2596), **soudés à plat** sur le PCB (empreinte `JDG_Protection:XL4005_Module_Flat`). Leurs sorties portent maintenant `6V_MOD` et `5V_AUX_MOD`. |
| Rail servos 6 V | U2 → **F1** (porte-fusible mini-lame, fusible de 7,5 A) → `6V`, avec **D3 SMBJ6.5A** et **C2 1000 µF 10 V**. |
| Sortie 5V_AUX | U3 → **F2** (fusible de 3 A) → `5V_AUX` → J7, avec **D4 SMBJ5.0A** et **C3 470 µF 10 V**. |
| Inverseur SBUS | Q1 devient un **MMBT3904 SOT-23** (nouveau symbole, brochage 1 = B, 2 = E, 3 = C). R1 et R2 passent en **0805**. |
| Servos S5 et S6 | Deux embases **S5 (D44)** et **S6 (D45)**, identiques à S1–S4, sur le rail 6 V protégé (même bus GND/6V). |
| Signaux servos | **R3–R6, R8, R9 330 Ω 0805** en série entre le Mega et S1–S6 (nouveaux nets `SRV_S1` à `SRV_S6`). |

| Servo | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| Broche Mega | D10 | D12 | D13 | D11 | D44 | D45 |

Jusqu'à 12 servos, la librairie `Servo` du Mega n'utilise que le Timer5, celui qui gère aussi le PWM de D44–D46. Ici D44 et D45 servent justement aux servos, et le PWM des moteurs (D2, D3, D5 sur le Timer3, D6 sur le Timer4) n'est pas touché.

Chaque pièce CMS a un champ `LCSC` rempli. J1, Q1, R1, R2, U2 et U3 gardent leur UUID, ce qui permet à la mise à jour du PCB de remplacer leurs empreintes au lieu de créer des doublons.

## Fichiers

| Fichier | Rôle |
|---|---|
| `*.kicad_sch` | Schéma modifié |
| `*.kicad_pro` | Projet, avec 3 classes de nets ajoutées : `Puissance_12V` (BAT+, 12V) 2,5 mm, `Rail_6V` 2,5 mm, `Rail_5V_AUX` 1,5 mm |
| `*.kicad_pcb` | Ton PCB `_bu`, non modifié |
| `JDG_Protection.pretty/`, `fp-lib-table` | Empreinte du module XL4005 et déclaration de la librairie projet |
| `Schema_v1.1_Protection.pdf` | Schéma en PDF |
| `BOM_JLCPCB_CMS.csv` | Pièces CMS à faire assembler par JLCPCB |
| `Pieces_a_souder_main.csv` | Nouvelles pièces à souder toi-même |

Pour réutiliser ton propre dossier de projet, copie le `.kicad_sch` et `JDG_Protection.pretty/`. Ajoute ensuite la librairie : Préférences → Gérer les librairies d'empreintes → onglet Projet, nom `JDG_Protection`, chemin `${KIPRJMOD}/JDG_Protection.pretty`. Si tu as déjà un `fp-lib-table` dans ton projet, ne l'écrase pas : ajoute seulement cette ligne.

## Mettre à jour le PCB (à faire par toi)

1. **F8** (Mettre à jour le PCB depuis le schéma). Coche l'option qui remplace les empreintes par celles des symboles (*Replace footprints with those specified by symbols*). J1, Q1, R1, R2, U2 et U3 changent d'empreinte. U3 et J7 arrivent aussi, puisqu'ils manquaient dans le `_bu`, ainsi que S5 et S6.
2. **Vérifie ton module XL4005** : il doit être la version 43 × 21 mm, avec des pastilles IN+/IN− d'un côté et OUT+/OUT− de l'autre, à **40 × 17,5 mm d'entraxe** (comme ton LM2596). L'empreinte reprend exactement l'origine et les pastilles de ton ancienne empreinte LM2596 : U2 retombe donc sur ses pastilles actuelles.
3. **Agrandis la carte** juste ce qu'il faut pour U3 (43 × 21 mm, absent du `_bu`), le bloc de protection 12 V, F1/F2, S5/S6 et le XT60.
4. **Placement** :
   - J1 → Q2 → D2/C1 au plus court ;
   - S5/S6 dans la rangée de S1–S4 ;
   - F1/D3/C2 près de S1–S6, F2/D4/C3 près de J7 ;
   - R3–R6, R8, R9 près du Mega ;
   - Q1/R1/R2 peuvent rester sous le Mega ;
   - aucun composant sous U2 et U3 (le module est à ~3 mm du PCB).
5. **Routage** :
   - 12 V de J1 jusqu'à l'embranchement : zone ou piste d’au moins 6 mm (≈10 A en pointe, 1 oz) ;
   - 6 V : au moins 3,5 mm ou une zone, jusqu'au bout de la rangée S1–S6 ;
   - 5V_AUX : au moins 1,5 mm ;
   - grande surface de cuivre sous la languette de Q2 ;
   - TVS et condos collés sur leur nœud, avec un GND court et plusieurs vias vers le plan ;
   - plan GND continu entre J1, les modules et les servos.
6. **DRC**, puis génère les Gerbers.

## Montage et réglage des XL4005

1. **Avant de souder**, alimente le module en 12 V sans charge et règle son pot au multimètre : **6,0 V** pour U2, **5,0 V** pour U3. Marque-les pour ne pas les inverser.
2. **Pattes** : passe un bout de **fil de cuivre rigide de 1,0 mm (18 AWG)** dans chaque pastille du module et du PCB. Les broches de header standard (0,64 mm, ~3 A) sont trop minces pour 5 A.
3. Garde le module à **~3 mm au-dessus du PCB** (une cale de 3 mm pendant la soudure), soude les 4 pattes des deux côtés et coupe l'excédent.
4. Revérifie la tension à vide sur le shield avant de brancher les servos. Le pot reste accessible par le dessus pour les retouches.

Le XL4005 n'a pas de réglage de limite de courant : il a une limite interne, une protection contre les courts-circuits et un arrêt thermique. Avec 6 servos standard (~2,5 A chacun en blocage), le rail 6 V plafonne vers 5 A : si plus de 2 servos forcent en même temps, la tension baisse. F1 (7,5 A, fusible lent) laisse passer les pointes normales et sert surtout à couper si le module lâche et envoie le 12 V sur le rail (la TVS D3 conduit et F1 saute). Sur 5V_AUX, F2 (3 A) saute aussi sur un court-circuit franc prolongé : garde les charges sous ~2,3 A en continu.

## Commande JLCPCB

- **BOM** : `BOM_JLCPCB_CMS.csv` (13 lignes, 18 pièces).
- **CPL** : à générer depuis le PCB une fois le placement fait (Fichier → Fabrication → Fichier de position, en CSV, face avant). Le plugin Fabrication Toolkit lit aussi les champs `LCSC` du schéma.
- **Avant de commander** : vérifie le stock de chaque numéro LCSC. Les pièces « Extended » ajoutent des frais par référence. MMBT3904 (C20526) et les résistances UNI-ROYAL sont des pièces courantes.
- Les pièces traversantes (THT) sont à souder à la main : voir la liste ci-dessous.

## Pièces à souder à la main

**Nouvelles pièces :**

| Repère | Pièce | Qté |
|---|---|---|
| J1 | XT60PW-M (Amass), mâle, PCB horizontal | 1 |
| F1, F2 | Porte-fusible mini-lame Keystone 3568 | 2 |
| S5, S6 | Embase femelle 1×3 2,54 mm Samtec SSW-103-01-F-D (comme S1–S4) | 2 |
| — | Fusibles mini-lame 7,5 A (F1) et 3 A (F2), avec rechanges | 2 + 2 |
| U2, U3 | Modules XL4005 5 A, carte 43 × 21 mm type DSN5000 (+1 de rechange) | 3 |
| — | Fil de cuivre étamé rigide 1,0 mm (18 AWG) pour les pattes des modules | ~15 cm |
| — | Porte-fusible mini-lame en ligne + fusible 15 A (fil batterie) | 1 |

**Pièces conservées :** J2–J5, J6, S1–S4, J7 et U1 (Mega).

**Pièces retirées :** bornier Würth de J1, R1/R2 axiales, 2N2222A, modules LM2596 (remplacés par les XL4005, même format).

## ERC

Il ne reste que les avertissements déjà présents dans le schéma d'origine :

- broches du Mega non utilisées (étiquettes isolées) ;
- « power pin not driven », normal avec des alimentations externes ;
- un bout de fil de 1,27 mm près du GND du Mega.

Les avertissements de librairie disparaissent quand le projet est ouvert avec tes librairies installées.
