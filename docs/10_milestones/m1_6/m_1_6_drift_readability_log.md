# M1.6: Drift Readability Log

Назначение: короткий журнал решений и результатов по каждой экспериментальной ветке.

## Формат записи

| Variant | Branch | Commit | Verdict | Notes | Next |
|---|---|---|---|---|---|
| prep-v0 | `drift/prep-v0-readability-baseline` | done locally | keep | Создана база M1.6: план+лог, индекс docs обновлен, sync по sprite layout/константам, turn-sprites помечены как legacy | branch for visual experiment |
| vis-v1 | `drift/vis-v1-ttri-tilt` | done locally | reject | ttri сам по себе работает, но с камерой по heading управление и восприятие оказались хуже; визуальный tilt конфликтовал с текущей камерой | перейти к camera-first эксперименту |
| cam-v1 | `drift/cam-v1-velocity-frame` | done locally | keep (iterate) | Читаемость траектории заметно выросла; связка velocity-frame + heading-only ttri дает понятный угол между носом и движением; остается резкое дерганье камеры на низкой скорости | сделать cam-v2 сглаживание (hysteresis/spring) |
| fx-v1 | `drift/fx-v1-worldspace-coherence` | `74be487`, `dc22d81` | keep (iterate) | Убрали speed-framing из baseline, world-space FX привязаны к текущей оси камеры, выхлоп/пыль лучше согласованы с ориентацией машины; переходные sparks пробовались и откатили как лишние для текущего baseline | при необходимости отдельной веткой сделать только micro-tune точек спавна/плотности FX |
| cam-v2 | `drift/cam-v2-spring` | done locally | iterate | заметно сгладили камеру, но остались скачки в момент резкого торможения в повороте и ощущение "ватности" | перейти к непрерывному blend |
| cam-v3 | `drift/cam-v3-spring-blend` | TBD | keep (minor iterate) | стало значительно лучше; остаточный редкий jerk в кейсе "дрифт -> почти стоп -> отпускание ручника" | сделать микрофикс `cam-v3.1` |
| cam-v3.1 | `drift/cam-v3-spring-blend` | done locally | keep | low-speed anti-jerk yaw cap улучшил стабильность; остаются редкие микрорезкости, но комфортно для игры | использовать как рабочую базу |
| cam-v4 | `drift/cam-v4-speed-framing` | done locally | reject | forward framing дал неприятное "плавание" кадра; reverse framing оказался забавным, но ухудшает читаемость трассы | не использовать в текущем baseline |

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
5. `cam-v4` (forward + reverse) протестирован и отклонен для текущей цели читаемости/комфорта.
6. Текущая рабочая база M1.6: `cam-v3.1` + `fx-v1-worldspace-coherence` (без speed-framing и без spark-burst).
