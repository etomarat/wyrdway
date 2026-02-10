# M1.6: Drift Readability Log

Назначение: короткий журнал решений и результатов по каждой экспериментальной ветке.

## Формат записи

| Variant | Branch | Commit | Verdict | Notes | Next |
|---|---|---|---|---|---|
| prep-v0 | `drift/prep-v0-readability-baseline` | done locally | keep | Создана база M1.6: план+лог, индекс docs обновлен, sync по sprite layout/константам, turn-sprites помечены как legacy | branch for visual experiment |
| vis-v1 | `drift/vis-v1-ttri-tilt` | done locally | reject | ttri сам по себе работает, но с камерой по heading управление и восприятие оказались хуже; визуальный tilt конфликтовал с текущей камерой | перейти к camera-first эксперименту |
| cam-v1 | `drift/cam-v1-velocity-frame` | done locally | keep (iterate) | Читаемость траектории заметно выросла; связка velocity-frame + heading-only ttri дает понятный угол между носом и движением; остается резкое дерганье камеры на низкой скорости | сделать cam-v2 сглаживание (hysteresis/spring) |
| fx-v1 | `drift/fx-v1-worldspace-coherence` | TBD | pending | align skid/particles with new camera frame | verify FX coherence |
| cam-v2 | `drift/cam-v2-spring` | done locally | iterate | заметно сгладили камеру, но остались скачки в момент резкого торможения в повороте и ощущение "ватности" | перейти к непрерывному blend |
| cam-v3 | `drift/cam-v3-spring-blend` | TBD | keep (minor iterate) | стало значительно лучше; остаточный редкий jerk в кейсе "дрифт -> почти стоп -> отпускание ручника" | сделать микрофикс `cam-v3.1` |
| cam-v3.1 | `drift/cam-v3-spring-blend` | TBD | in_progress | low-speed anti-jerk: ограничить резкий разворот цели камеры около нулевой скорости | validate that control feel stays responsive |
| cam-v4 | `drift/cam-v4-speed-framing` | TBD | pending | speed-based forward framing (show more road at high speed) | run only after cam-v3 verdict |

## Fill-in Rules (after each playtest)

1. `Commit`: указывать короткий SHA или `SHA1, SHA2`.
2. `Verdict`: `keep` / `reject` / `iterate`.
3. `Notes`: 2-5 коротких наблюдений по ощущениям.
4. `Next`: конкретный следующий шаг (ветка/изменение).

## Current Takeaways

1. `camera by velocity` действительно повышает читаемость дрифта.
2. `ttri` полезен как носитель угла машины, но в отрыве от новой камеры легко ухудшает UX.
3. Основной оставшийся риск после cam-v1: низкоскоростной jitter из-за перехода между `heading` и `velocity` направлением камеры.
4. `cam-v3` признан рабочим базовым вариантом для M1.6 (keep), но с небольшим остаточным low-speed jerk.
5. Следующий практический шаг: `cam-v3.1` микрофикс, после него перейти к `cam-v4-speed-framing`.
