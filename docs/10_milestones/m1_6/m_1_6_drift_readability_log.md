# M1.6: Drift Readability Log

Назначение: короткий журнал решений и результатов по каждой экспериментальной ветке.

## Формат записи

| Variant | Branch | Commit | Verdict | Notes | Next |
|---|---|---|---|---|---|
| prep-v0 | `drift/prep-v0-readability-baseline` | TBD | in_progress | baseline cleanup, docs sync, no turn-sprites | start `vis-v1-ttri-tilt` |
| vis-v1 | `drift/vis-v1-ttri-tilt` | TBD | pending | ttri quad + arbitrary rotation test | gather artifact feedback |
| cam-v1 | `drift/cam-v1-velocity-frame` | TBD | in_progress | camera orientation by smoothed velocity + heading-only ttri car | evaluate trajectory readability |
| fx-v1 | `drift/fx-v1-worldspace-coherence` | TBD | pending | align skid/particles with new camera frame | verify FX coherence |
| cam-v2 | `drift/cam-v2-lookahead` | TBD | pending | velocity look-ahead with smoothing | evaluate control/readability tradeoff |
| cam-v3 | `drift/cam-v3-spring` | TBD | conditional | optional spring/lag follow | do only if V2 feels harsh |

## Fill-in Rules (after each playtest)

1. `Commit`: указывать короткий SHA или `SHA1, SHA2`.
2. `Verdict`: `keep` / `reject` / `iterate`.
3. `Notes`: 2-5 коротких наблюдений по ощущениям.
4. `Next`: конкретный следующий шаг (ветка/изменение).
