# D-Day Weather: Evidence, Gaps and Time Progression

## What is currently supported

| Evidence | Place and time | Value or statement | Use in this project |
|---|---|---|---|
| Official U.S. campaign account | Omaha approach / transport area, early 6 June; no exact instrument timestamp | Northwest wind, 10–18 knots; transport-area waves about 3–4 ft, occasional 6 ft; beach breakers about 3–4 ft | Historical range for atmosphere and sea appearance; not a continuous sensor series |
| Contemporary synoptic chart | Regional, 6 June 1944 at 13 UTC | Scanned pressure/weather chart | Context; station symbols have not been transcribed into an Omaha time series |
| Sword report described by ECMWF | Sword Beach, 13 UTC on 6 June | Mainly sunny; northwesterly Force 4 | Nearby-beach context, explicitly not Omaha |
| ECMWF ERA-CLIM analysis | Regional reconstruction of June 1944 | Model cloud, wind and waves compared with reports/photos | Modern reconstruction, not direct measurement |
| Met Office daily statistic | Thorney Island, England, 6 June | Maximum temperature 17.8°C | Excluded from Omaha temperature field |
| Omaha air temperature | Exact location/time not established | **Unknown** | Keep null; no numeric historical claim |
| Omaha relative humidity | Exact location/time not established | **Unknown** | Keep null; never infer from wet sand or cloud alone |

Sources: [Omaha Beachhead, chapter 3](https://www.ibiblio.org/hyperwar/USA/USA-A-Omaha/USA-A-Omaha-3.html), [Met Office factsheet](archive/metoffice_dday_factsheet.pdf), [13 UTC chart](archive/metoffice_19440606_1300utc.pdf), [ECMWF comparison](https://www.ecmwf.int/en/research/projects/era-clim/d-day-analyses).

Ten to eighteen knots converts to approximately **5.14–9.26 m/s**. This conversion does not add measurement precision. Force 4 represents a range (11–16 knots in the Met Office scale), not an exact 13-knot observation. [Beaufort scale](https://weather.metoffice.gov.uk/guides/coast-and-sea/beaufort-scale)

The campaign account is retrospective; its wind and sea ranges should not be labeled raw observations. Conditions can differ between offshore ships, different beaches, and inland sites. Any disagreement is retained with its location and time, not averaged away.

## Historical time is not demo playback time

Store source times in their original basis. A 13 UTC chart is unambiguous. Operational times such as 0630 or photograph captions such as 0730 require verification of the source's time convention before conversion. The evidence CSV leaves UTC fields blank where this has not been resolved.

A five-minute gameplay sequence should normally advance only five minutes of historical time. Showing morning-to-afternoon change during a short demonstration requires an explicit **time-compressed review mode**, with the simulated time displayed. Do not silently turn a single assault into an entire day's weather cycle.

## Weather extension suitable for this project

The base level uses a stable, historically informed morning preset. A later extension provides a clock and carefully authored weather keys, showing which settings are documentary and which are artistic interpolation. Begin with wind direction, cloud appearance and lighting. Rain, humidity and air temperature are independent fields; a wet beach does not imply rain, and relative humidity alone does not determine fog.

Keep tide/wetness separate from atmospheric humidity. Tidal timing and height need a datum and location-specific reconstruction before driving collision or traversability. For now, the wet/dry sand mask can be a documented visual approximation without claiming an exact tide simulation.

## Pressure and further evidence

Focus Features' **Pressure (2026)** dramatizes the forecasting decision. It is useful thematic context, but its color grade, rain, dialogue or props do not establish measured weather. [Official film page](https://www.focusfeatures.com/pressure)

Next archival targets are ship logs with known offshore positions and UTC conventions, beach meteorological reports, and station sheets containing simultaneous dry-bulb/dew-point or wet-bulb readings. A regional hindcast may fill an optional reconstruction track, but cannot fill the observation track. No exact Omaha hourly temperature/humidity series has been established in this collection.

Use [weather_evidence.csv](data/weather_evidence.csv) as the evidence ledger and [weather_keyframe_template.csv](data/weather_keyframe_template.csv) as the future authoring schema. Neither is a ready-to-import Unreal DataTable until its corresponding Blueprint struct and validation rules exist.
