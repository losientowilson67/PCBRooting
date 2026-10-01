# Shield JDG2025 v1.1 : protections et passage en CMS

Révision du schéma `MachineJDG2025_MEGA2560_Shield_VL_2024_12_19` (KiCad 10). Le mapping des moteurs, des servos S1–S4 et du SBUS ne change pas ; deux servos (S5, S6) sont ajoutés. **Le PCB n'a pas été modifié** : le `.kicad_pcb` de ce dossier est ton fichier `_bu` tel quel.

Les fichiers sont au format **KiCad 10** (comme tes fichiers d'origine) : KiCad 8 ne peut pas les ouvrir.

## Changements dans le schéma

| Bloc | Changement |
|---|---|
| Entrée 12 V | J1 devient un **XT60PW-M** (broche 1 = −, broche 2 = +), suivi de la **TVS D2 SMBJ14A** et de **C1 470 µF 35 V** sur le 12 V. Le fusible de 15 A est en ligne sur le fil de batterie, hors PCB. |
| Régulateurs | U2 et U3 sont des **modules buck 43 × 21 mm soudés à plat** sur le PCB (empreinte `JDG_Protection:XL4005_DC-DC`, celle de l'archive `KiCad-master`) : **XL4005 5 A** (DSN5000) ou **LM2596 3 A** (DSN2596), au choix. |
| Rail servos 6 V | **D3 SMBJ6.5A** et **C2 1000 µF 10 V** sur le 6 V, près de S1–S6. |
| Sortie 5V_AUX | **D4 SMBJ5.0A** et **C3 470 µF 10 V** sur le 5V_AUX, près de J7. |
| Inverseur SBUS | Q1 devient un **MMBT3904 SOT-23** (nouveau symbole, brochage 1 = B, 2 = E, 3 = C). R1 et R2 passent en **0805**. |
| Servos S5 et S6 | Deux embases **S5 (D44)** et **S6 (D45)**, identiques à S1–S4, sur le même rail 6 V. |
| Signaux servos | **R3–R6, R8, R9 330 Ω 0805** en série entre le Mega et S1–S6 (nouveaux nets `SRV_S1` à `SRV_S6`). |

| Servo | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| Broche Mega | D10 | D12 | D13 | D11 | D44 | D45 |

Jusqu'à 12 servos, la librairie `Servo` du Mega n'utilise que le Timer5, celui qui gère aussi le PWM de D44–D46. Ici D44 et D45 servent justement aux servos, et le PWM des moteurs (D2, D3, D5 sur le Timer3, D6 sur le Timer4) n'est pas touché.

Chaque pièce CMS a un champ `LCSC` rempli. J1, Q1, R1, R2, U2 et U3 gardent leur UUID, ce qui permet à la mise à jour du PCB de remplacer leurs empreintes au lieu de créer des doublons.

## Ce que font les protections

- **D2, D3, D4 (TVS)** absorbent les pics de tension : moteurs et servos qui freinent, branchements, décharges statiques. Elles ne conduisent pas en fonctionnement normal (12,6 V, 6 V et 5 V).
- **C1, C2, C3** gardent la tension stable quand les moteurs et les servos tirent des pointes de courant. C2 évite surtout que le 6 V s'effondre quand plusieurs servos démarrent.
- **Inversion de polarité** : le XT60 a un détrompeur. Si le fil de batterie est quand même soudé à l'envers sur son XT60, D2 conduit en direct et fait sauter le fusible de 15 A. D2 peut y rester : change-la après.
- **Surcharge et court-circuit** : les modules XL4005 et LM2596 ont une limite de courant interne, une protection contre les courts-circuits et un arrêt thermique.
- **Limite** : si un module tombe en panne et envoie le 12 V sur sa sortie, D3 ou D4 conduit et grille (elle se met en court-circuit). Le fusible de 15 A finit par sauter, mais un servo ou une charge sur 5V_AUX peut avoir le temps d'en souffrir.

## Fichiers

| Fichier | Rôle |
|---|---|
| `*.kicad_sch` | Schéma modifié |
| `*.kicad_pro` | Projet, avec 3 classes de nets ajoutées : `Puissance_12V` 2,5 mm, `Rail_6V` 2,5 mm, `Rail_5V_AUX` 1,5 mm |
| `*.kicad_pcb` | Ton PCB `_bu`, non modifié |
| `JDG_Protection.pretty/`, `fp-lib-table` | Empreinte du module XL4005 et déclaration de la librairie projet |
| `Schema_v1.1_Protection.pdf` | Schéma en PDF |
| `BOM_JLCPCB_CMS.csv` | Pièces CMS à faire assembler par JLCPCB |
| `Pieces_a_souder_main.csv` | Nouvelles pièces à souder toi-même |

Pour réutiliser ton propre dossier de projet, copie le `.kicad_sch` et `JDG_Protection.pretty/`. Ajoute ensuite la librairie : Préférences → Gérer les librairies d'empreintes → onglet Projet, nom `JDG_Protection`, chemin `${KIPRJMOD}/JDG_Protection.pretty`. Si tu as déjà un `fp-lib-table` dans ton projet, ne l'écrase pas : ajoute seulement cette ligne.

## Mettre à jour le PCB (à faire par toi)

1. **F8** (Mettre à jour le PCB depuis le schéma). Coche l'option qui remplace les empreintes par celles des symboles (*Replace footprints with those specified by symbols*). J1, Q1, R1, R2, U2 et U3 changent d'empreinte. U3 et J7 arrivent aussi, puisqu'ils manquaient dans le `_bu`, ainsi que S5 et S6.
2. **Vérifie ton module (XL4005 ou LM2596)** : il doit être la version 43 × 21 mm, avec IN+/IN− d'un côté, OUT+/OUT− de l'autre, **39,5 × 17,15 mm d'entraxe** et **2 trous M3 en diagonale** (comme sur l'empreinte `XL4005_DC-DC`). L'origine de cette empreinte est le coin bas-gauche du module, pas son centre, et son entraxe diffère d'environ 0,5 mm de ton ancienne empreinte LM2596 : après F8, replace U2 et reprends ses pistes.
3. **Agrandis la carte** juste ce qu'il faut pour U3 (43 × 21 mm, absent du `_bu`), S5/S6, le XT60 et les nouvelles pièces CMS.
4. **Placement** :
   - D2 et C1 juste après J1 ;
   - S5/S6 dans la rangée de S1–S4 ;
   - D3/C2 près de S1–S6, D4/C3 près de J7 ;
   - R3–R6, R8, R9 près du Mega ;
   - Q1/R1/R2 peuvent rester sous le Mega ;
   - aucun composant sous U2 et U3 (le module est à ~3 mm du PCB).
5. **Routage** :
   - 12 V de J1 jusqu'à l'embranchement : zone ou piste d'au moins 6 mm (≈10 A en pointe, 1 oz) ;
   - 6 V : au moins 3,5 mm ou une zone, jusqu'au bout de la rangée S1–S6 ;
   - 5V_AUX : au moins 1,5 mm ;
   - TVS et condos collés sur leur nœud, avec un GND court et plusieurs vias vers le plan ;
   - plan GND continu entre J1, les modules et les servos.
6. **DRC**, puis génère les Gerbers.

## Montage et réglage des modules

| | XL4005 | LM2596 |
|---|---|---|
| Courant max | ~5 A | ~3 A (≈2 A en continu sans dissipateur) |
| Tension d'entrée max | 32 V | 40 V |
| Conseillé pour | U2 (servos) et U3 | U3 seulement, si 5V_AUX reste sous ~2 A |

Les deux tiennent le 12 V (la TVS D2 limite les pics à 23 V). Un LM2596 ne va sur cette empreinte que s'il a la même carte (même entraxe, trous en diagonale) : vérifie au pied à coulisse.

La sérigraphie de l'empreinte d'origine indique « Input: DC 5V-38V », mais la puce XL4005 est donnée pour 32 V max. Ce n'est pas un problème ici (12,6 V max, pics limités à 23 V).

1. **Aligne le IN+ imprimé sur le module avec le IN+ de la sérigraphie du PCB.** L'ordre des pastilles n'est pas le même sur tous les clones, et un module branché à l'envers grille (le XL4005 n'a pas de protection contre l'inversion).
2. **Avant de souder**, alimente le module en 12 V sans charge et règle son pot au multimètre : **6,0 V** pour U2, **5,0 V** pour U3. Marque-les pour ne pas les inverser.
3. **Pattes** : l'empreinte est percée à 1,2 mm. Passe dans chaque pastille du **fil de cuivre rigide de 0,8 mm (20 AWG)**, ou de 1,0 mm (18 AWG) au maximum si ça entre dans les trous du module. Les broches de header standard (0,64 mm, ~3 A) sont trop minces pour 5 A, mais suffisent pour un LM2596.
4. Fixe le module avec **2 vis M3 en nylon et des entretoises de 3 mm** dans les trous en diagonale : ça règle la hauteur (~3 mm au-dessus du PCB) et tient le module contre les vibrations. Soude ensuite les 4 pattes des deux côtés et coupe l'excédent.
5. Revérifie la tension à vide sur le shield avant de brancher les servos. Le pot reste accessible par le dessus pour les retouches.

Avec 6 servos standard (~2,5 A chacun en blocage) et un XL4005 sur U2, le rail 6 V plafonne vers 5 A : si plus de 2 servos forcent en même temps, la tension baisse, sans rien griller.

## Commande JLCPCB

- **BOM** : `BOM_JLCPCB_CMS.csv` (10 lignes, 15 pièces).
- **CPL** : à générer depuis le PCB une fois le placement fait (Fichier → Fabrication → Fichier de position, en CSV, face avant). Le plugin Fabrication Toolkit lit aussi les champs `LCSC` du schéma.
- **Avant de commander** : vérifie le stock de chaque numéro LCSC. Les pièces « Extended » ajoutent des frais par référence. MMBT3904 (C20526) et les résistances UNI-ROYAL sont des pièces courantes.
- Les pièces traversantes (THT) sont à souder à la main : voir la liste ci-dessous.

## Pièces à souder à la main

**Nouvelles pièces :**

| Repère | Pièce | Qté |
|---|---|---|
| J1 | XT60PW-M (Amass), mâle, PCB horizontal | 1 |
| S5, S6 | Embase femelle 1×3 2,54 mm Samtec SSW-103-01-F-D (comme S1–S4) | 2 |
| U2, U3 | Modules XL4005 5 A, carte 43 × 21 mm type DSN5000 (+1 de rechange). Un LM2596 sur la même carte convient aussi pour U3 | 3 |
| — | Fil de cuivre étamé rigide 0,8 mm (20 AWG), 1,0 mm max, pour les pattes des modules | ~15 cm |
| — | Vis M3 × 8 nylon + entretoise nylon 3 mm + écrou (2 par module) | 4 + 4 + 4 |
| — | Porte-fusible mini-lame en ligne + fusible 15 A (fil batterie) | 1 |

**Pièces conservées :** J2–J5, J6, S1–S4, J7 et U1 (Mega).

**Pièces retirées :** bornier Würth de J1, R1/R2 axiales, 2N2222A, modules LM2596 sur U2 (remplacés par un XL4005, même format).

## ERC

Il ne reste que les avertissements déjà présents dans le schéma d'origine :

- broches du Mega non utilisées (étiquettes isolées) ;
- « power pin not driven », normal avec des alimentations externes ;
- un bout de fil de 1,27 mm près du GND du Mega.

Les avertissements de librairie disparaissent quand le projet est ouvert avec tes librairies installées.
