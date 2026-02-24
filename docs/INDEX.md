# Docs Index

Этот файл — «точка входа» в документацию проекта. Если ты новичок в репозитории,
начинай отсюда.

## Структура `docs/`

```
docs/
  00_spec/              # "0_* - 7_*" (источник правды по системе)
  10_milestones/        # планы/отчёты по M1, M1.5, и т.д.
  20_tech/              # pocketpy/tic80, лимиты, пайплайн
  30_style/             # визуальный стиль, UI, палитры, FX, гайды
  40_marketing/         # тексты для itch.io/соцсетей/скриншотов
  90_archive/           # устаревшее, но не удаляем
  INDEX.md              # оглавление (куда смотреть новичку)
```

## Куда смотреть в первую очередь

1) **Текущий этап / планы**
- `10_milestones/m1/m1_plan.md`
- `10_milestones/m1/m1_report.md`
- `10_milestones/m1_5/m_1_5_plan.md`
- `10_milestones/m1_5/m_1_5_drive_physics_tuning_plan.md` — план улучшения управления/физики DRIVE.
- `10_milestones/m1_6/m_1_6_drift_readability_plan.md` — план экспериментов по читаемости дрифта.
- `10_milestones/m1_6/m_1_6_drift_readability_log.md` — журнал решений и результатов по веткам `drift/*`.
- `10_milestones/m1_7/m_1_7_playable_loop_v_0_plan.md` — минимальная петля с route/return.
- `10_milestones/m1_8/m_1_8_pursuer_chase_v_0_plan.md` — погоня на return, варианты сущности, текущий HUD/FX.
- Если при запуске сразу попадаешь в `DRIVE_PRESET`, проверь `IS_DRIVE_PLAYTEST` в `tic80/python/main.py`.

2) **Спека (источник правды по системам)**
- `00_spec/0_gdd_v0.md` — GDD v0 (общая картина).
- `00_spec/2_architecture.md` — сцены/поток/правила владения кадром.
- `00_spec/3_runstate.md` — контракт данных (Profile/Run и т.п.).
- `00_spec/8_drive_physics.md` — DRIVE (m1.5): world-space физика и связь с дорогой.
- `00_spec/9_drive_playtest_camera.md` — DRIVE (m1.6): плейтест, камера и читаемость заноса.
- `00_spec/5_tuning.md` — принципы TUNING (что вносить в тюнинг и как).
- `00_spec/6_save_load.md` — политика сейвов/лоада и версионирование.

3) **Тех‑справка**
- `20_tech/pocketpy_runtime.md` — особенности PocketPy/TIC-80 Python.
- `20_tech/tic80_api_reference.md` — короткая справка по TIC-80 API.
- `20_tech/TIC-80.wiki/` — полный оффлайн‑клон wiki TIC-80 (очень много файлов).

4) **Стиль/арт‑гайд**
- `30_style/0_style_car.md` (если нужен быстрый ориентир по визуалу).
- `30_style/1_sprite_sheet_layout.md` — раскладка спрайтов/адреса/размеры (источник правды для ассетов).
- `30_style/2_vehicle_niva.md` — спецификация “Нивы” (идентичность/силуэт/правила).

5) **Лор (черновики)**
- `80_misc/lore_notes.md` — поток мыслей и зацепки для развития лора/концовки.

6) **Маркетинг / соцсети**
- `40_marketing/INDEX.md` — itch.io + посты + заметки по скриншотам и тегам.

## Правила поддержки документации

- **`00_spec/` — источник правды.** Если меняется поведение системы — обновляем
  соответствующую спеку.
- **`10_milestones/` — рабочие артефакты разработки.** Здесь лежат планы,
  чеклисты, отчёты и заметки плейтеста.
- **`20_tech/` — всё про рантайм/ограничения/пайплайн.** Если выяснили ограничение
  PocketPy или TIC-80 — фиксируем здесь.
- **`30_style/` — визуальные правила и примеры.** Можно класть палитры, UI‑гайд,
  примеры FX.
- **`90_archive/` — не удаляем, но не используем как источник правды.**

## Полезные ссылки, на будущее
## Libraries
- [TICuare](https://github.com/Crutiatix/TICuare): A simple and customisable UI library based on Uare.
- [pico2tic](https://github.com/musurca/pico2tic): PICO-8 API Wrapper.
- [PSLIB](http://tic.computer/play?cart=85): An advenced particle system.
- [bump demo](https://itch.io/t/72354/collision-detection-library-bump-and-simple-demo-for-tic-80): Lua collision-detection library for axis-aligned rectangles.
- [Make Gradient](https://pastebin.com/kiVBG8HD): Useful for effects such as changing color on scanline or palette animation, all in just over 1600 bytes. 
- [LZW Image Compression](https://github.com/deck-dev/LZW-image-compression-for-TIC): Compress image and store it as string. Decompress in Lua.
- [FC-RLE: RLE Image Compression](https://github.com/josefnpat/fc-rle): Compress an image and store it as a string in run-length encoding. Decompress it in game with a few small helper functions.
- [LZW compression js](https://tic.computer/play?cart=135): Javascript implementation of LZW compress and decompress algorithm.


## Tools
- [TicMcTile](https://github.com/PhilSwiss/ticmctile): Commandline tool to convert images to tiles, sprites or charsets for the TIC-80.
- [TiledMapEditor-TIC-80](https://github.com/AlRado/TiledMapEditor-TIC-80): A simple commandline converter between Tiled tilemaps and TIC-80 tilemaps.
- [Fantasy Console Map Tool](https://monstersgoboom.itch.io/fcmt): This tool fills a gap between desktop 2d tilemap editing programs and fantasy consoles.
- [Color palette editor](https://aaronsnoswell.github.io/blog/tic-80-color-palette-tool): A tool that allows you to pick 16 colors and then it generates a color string to use in your game.
- [Visual-Code-TIC-80](https://github.com/AlRado/Visual-Code-TIC-80): Visual Studio Code settings.
- [Sublime-TIC-80](https://github.com/AlRado/Sublime-TIC-80): A package for Sublime Text 3.
- [tic80tileswap](https://github.com/borbware/tic80tileswap): Swap around tiles in a TIC-80 .lua file (requires TIC-80 pro).
- [tic80downloader](https://github.com/msx80/tic80downloader): Cart downloader and helper.
- [tic80-draw-image](https://github.com/cxong/tic80-draw-image): Demo of how to draw an arbitrary image.
- [Textri](https://tic.computer/play?cart=554): Simple tool to help visualize / explain UV's for textri.
- [Compression Sandbox](https://tic.computer/play?cart=313): Tiny viewer for packed resources, that supports chained grouping and packing with RLE/LZ77/Huffman code.
- [Font Editor](https://tic.computer/play?cart=263): Simple editor for 5x5 fonts with samples in Cyrillic, Latin, Greek, Hebrew and even some Japanese writings.
- [SFX Wave Maker](https://tic.computer/play?cart=682): Create complex SFX waves.

### Miscellaneous
- [fennel-tic80-game](https://github.com/stefandevai/fennel-tic80-game): Boilerplate code for game using Fennel lisp.
- [not-cool](https://github.com/whichxjy/not-cool): Pathfinding algorithms.
- [Code examples and snippets](https://github.com/nesbox/TIC-80/wiki/code-examples-and-snippets)
