# Uniforms, Ranks and Visible Identity

## U.S. Omaha infantry: starter model sheet

Use the M1941 field-jacket family, M1 helmet and contemporary web equipment as the starting reference set. Check trousers, leggings, footwear and carried load against the selected unit's landing photographs. The survey includes later M1943 clothing and M1944/M1945 equipment: those pages are comparison material, not a universal D-Day outfit. [U.S. Army survey, PDF pp. 83–98](archive/us_uniform_survey.pdf)

Local visual references: [field jackets](images/uniforms/us_field_jackets.png), [helmet and specialist clothing](images/uniforms/us_helmet_and_specialist_clothing.png), [equipment](images/uniforms/us_web_equipment.png), [rank chart](images/ranks/us_wwii_rank_chart.png). Do not infer exact cloth color from monochrome photography or faded scans. Final color values are rendering decisions checked against multiple references.

### U.S. enlisted and NCO distinctions

| Rank | Visible rank pattern | Encounter use |
|---|---|---|
| Private | No rank chevron | Ordinary rifleman |
| Private First Class | One chevron | Ordinary rifleman |
| Corporal | Two chevrons | Junior leader if appropriate |
| Sergeant | Three chevrons | Candidate squad leader |
| Staff Sergeant | Three chevrons and one rocker | Leader variant if scenario supports it |
| Technical Sergeant | Three chevrons and two rockers | Reference only for initial small encounter |
| Master Sergeant | Three chevrons and three rockers | Reference only |
| First Sergeant | Three chevrons, three rockers and central diamond | Company role; do not scatter throughout squads |
| Technician 5th / 4th / 3rd Grade | Corresponding corporal / sergeant / staff-sergeant pattern with T | Technical grade does not automatically confer an NCO command role |

Use the period chart as the texture reference; do not copy a modern Sergeant First Class or Specialist badge. Divisional patches and rank insignia serve different purposes. [S02](SOURCES.md)

### U.S. commissioned officers

Use the [1943 U.S. Army officer recognition chart](images/ranks/us_officer_rank_chart_1943.jpg), preserving the distinction between its Army and Navy rows. [S24](SOURCES.md)

| Army rank | Insignia form |
|---|---|
| Second Lieutenant | One gold bar |
| First Lieutenant | One silver bar |
| Captain | Two silver bars |
| Major | Gold oak leaf |
| Lieutenant Colonel | Silver oak leaf |
| Colonel | Silver eagle |
| Brigadier / Major / Lieutenant General / General | One / two / three / four silver stars |

The initial encounter does not require a general model. Five-star General of the Army promotions began in December 1944 and must not appear in a D-Day scene. [U.S. Army CMH](https://history.army.mil/Research/Reference-Topics/5-Star/Gen-George-C-Marshall/)

## German Heer: distinguish rank from branch and appointment

The 1945 handbook supplies field-uniform and rank plates, but includes later-war developments. Use **Heer infantry** as the initial reference family. Its service, field, fatigue, mountain and armored-crew clothing are not interchangeable. Black armored-crew clothing or an SS collar patch does not identify an ordinary Heer beach defender. [TM-E 30-451, Chapter IX](https://www.ibiblio.org/hyperwar/Germany/HB/HB-9.html)

| Group | German rank names for reference | Visual review anchor |
|---|---|---|
| Enlisted | Grenadier/Schuetze (designation depends on unit); Gefreiter; Obergefreiter; Stabsgefreiter | [Plate V: sleeve distinctions](images/ranks/heer_enlisted_ranks.png); do not treat Gefreiter as automatically equivalent to a U.S. corporal's leadership role |
| Junior NCOs | Unteroffizier; Unterfeldwebel | Collar braid and shoulder-board differences in [Plate IV](images/ranks/heer_officer_nco_ranks.png) |
| Senior NCOs | Feldwebel; Oberfeldwebel; Stabsfeldwebel | Shoulder-board pips/braid; preserve German title rather than the manual's approximate U.S. translation |
| Company officers | Leutnant; Oberleutnant; Hauptmann | Officer shoulder boards and pips; field uniform remains a combat uniform |
| Field officers | Major; Oberstleutnant; Oberst | Braided officer boards; no need to model for the initial encounter |
| General officers | Generalmajor; Generalleutnant; General der [branch]; Generaloberst; Generalfeldmarschall | Context only; use German hierarchy, not literal English labels in Allied recognition plates |

**Hauptfeldwebel is an appointment, not a separate rank.** The period U.S. recognition plate places it in a row alongside ranks; keep `Rank` and `Appointment` separate in project data. Exact enlisted service distinctions and appointment braid must be read from the plate, not improvised.

Branch piping is a separate field. The [branch-color plate](images/ranks/heer_branch_colors.png) distinguishes infantry, artillery, armor and other branches. Its scan is monochrome: use the printed color names, not sampled pixels. Verify the exact garment and unit before applying piping everywhere.

## British and Canadian references: separate from the Omaha force

The [1944 British recognition sheet](images/uniforms/british_1944_recognition.jpg) is German-produced intelligence artwork. It supplies a period comparison, not an authoritative color calibration. Cross-check with [Captain Alfred Rowe's battledress in the National Army Museum](https://www.nam.ac.uk/explore/normandy-campaign). His jacket is a British officer reference, not clothing for the U.S. player.

British rank families include Private, Lance Corporal, Corporal, Sergeant, Staff/Colour Sergeant, Warrant Officer and commissioned officers. Regiment-specific titles and insignia require a dated object sheet. [National Army Museum rank guide](https://www.nam.ac.uk/explore/british-army-ranks)

The [1943 British Empire officer plate](images/ranks/british_officer_rank_chart_1943.jpg) provides the commissioned-rank comparison, including shoulder insignia. Do not substitute the U.S. bars/eagle pattern or modern crown artwork. This is an official U.S. Army recognition guide for Allied officers, not a British unit roster. [S25](SOURCES.md)

Canadian units require their own formation signs and national identifiers; British-style clothing does not mean identical unit markings. The [Royal Winnipeg Rifles lineage](https://www.canada.ca/en/department-national-defence/services/military-history/history-heritage/official-military-history-lineages/lineages/infantry-regiments/royal-winnipeg-rifles.html) provides one official D-Day unit anchor. A complete Canadian rank/clothing atlas is outside this first Omaha-focused collection and remains required if Canadian characters are added.

## Asset review fields

`Nation`, `ServiceBranch`, `Unit`, `RankOriginal`, `Appointment`, `CombatRole`, `GarmentPattern`, `HelmetPattern`, `InsigniaLocations`, `ReferenceIDs`, `ValidDateRange`, `ReviewStatus`.

Rank must not be inferred solely from the weapon. A leader need not carry a pistol in hand, and not every German carries an MP40. Keep camouflage, insignia wear and field modifications tied to evidence rather than random cosmetic generation.
