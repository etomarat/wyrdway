# Release Checklist

Короткий чеклист для ручного релиза без авто-bump.

## 1) Поднять версию (вручную)

1. Обновить `GAME_VERSION` в `tic80/python/core/version.py`.
2. Обновить метаданные `# version:` в `tic80/python/main.py`.

## 2) Подготовить changelog

1. Перенести готовые пункты из `Unreleased` в новый блок версии в `CHANGELOG.md`.
2. (Опционально) собрать черновик из git:
   - `git log --pretty=format:"- %s (%h)" <prev_tag>..HEAD`

## 3) Сборка и проверка

1. `run_tic80_python.bat build`
2. `run_tic80_python.bat dist`
3. Быстро проверить стартовый экран: версия отображается и совпадает с release tag.

## 4) Тег релиза

1. `git tag -a vX.Y.Z -m "Wyrdway vX.Y.Z <stage>"`
2. `git push origin main`
3. `git push origin vX.Y.Z`

## 5) Публикация

1. Подготовить itch devlog и короткие посты по шаблону:
   - `docs/40_marketing/release_post_template.md`
2. Опубликовать devlog + кросспост в соцсети.
