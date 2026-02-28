# Gamepad Face Buttons: Arcade Driving Mappings (Notes)

Эта заметка нужна, чтобы обсуждать раскладку по *позициям* фейс-кнопок, а не по буквам, которые различаются между Xbox/PlayStation/Nintendo и иногда "переезжают" в драйверах/эмуляторах.

## Легенда (позиция -> как подписано)

Позиции фейс-кнопок (крестовина не входит сюда):

| Позиция | Xbox | PlayStation | Nintendo |
|---|---|---|---|
| South (нижняя) | A | Cross (X) | B |
| West (левая) | X | Square | Y |
| East (правая) | B | Circle | A |
| North (верхняя) | Y | Triangle | X |

## Таблица: примеры аркадных/ретро игр (позиция -> действие)

Важно: разные версии (PS1/PS2/PSP/N64) и разные режимы управления могли отличаться. Здесь цель не "историческая точность до патча", а паттерны распределения действий по позициям.

| Игра | Платформа | South | West | East | North | Источник |
|---|---|---|---|---|---|---|
| Ridge Racer Type 4 | PS1 | газ | тормоз | - | камера | https://psxdatacenter.com/games/J/R/SCPS-45354.html |
| Ridge Racer V | PS2 | газ | тормоз | - | камера | https://gamefaqs.gamespot.com/ps2/198478-ridge-racer-v/faqs/10952 |
| OutRun 2006: Coast 2 Coast | PS2 | газ | тормоз | (в меню) назад/отмена | камера | https://psxdatacenter.com/psx2/games2/SLUS-21274.html |
| Burnout Revenge | PS2 | газ | ручник/дрифт | тормоз/реверс | камера | https://gamefaqs.gamespot.com/ps2/927225-burnout-revenge/answers/25995-looking-for-controls-for-logitech-driving-force- |
| Need for Speed: Underground 2 | PS2 | газ | тормоз/реверс | оглянуться назад | камера | https://gamefaqs.gamespot.com/boards/920467-need-for-speed-underground-2/46790825 |
| Midnight Club 3: DUB Edition Remix | PS2 | газ | тормоз/реверс | фары/челлендж (не про вождение) | камера | https://gamefaqs.gamespot.com/ps2/931972-midnight-club-3-dub-edition-remix/faqs/36605 |
| Wipeout 3 Special Edition | PS1 | газ | выбросить оружие | использовать оружие | камера | https://www.psxdatacenter.com/games/P/W/SCES-02845.html |
| Wipeout Pure | PSP | газ | тормоз/реверс | выстрел | "абсорб" оружия | https://manuals.plus/asin/B00006FSLC |
| Mario Kart 64 | N64 | A: газ | - | B: тормоз/реверс | - | https://manuals.plus/el/m/c2cae59038e1218573487a4eff2ea117d0ab541a709280ddc4343df9c4fbc644 |
| Cruis'n World | N64 | A: газ | - | B: тормоз | - | https://www.world-of-nintendo.com/manuals/nintendo_64/cruis_n_world.shtml |
| F-Zero X | N64 | A: газ | - | B: буст (тормоз на C-Down) | - | https://manuals.plus/m/62283bef26fe248a69ab18fae12cccabf97423492dc08b9edab7ebdac97fdb0e |
| Rad Racer | NES | A: газ | B: тормоз | - | - | https://www.world-of-nintendo.com/manuals/nes/rad_racer.shtml |

## Выводы для Wyrdway (черновик)

Наблюдения, которые полезны для нашей проблемы "газ на UP неудобен":

- South (нижняя) очень часто используется как "газ" в аркадной традиции.
- West (левая) довольно часто занята "тормоз/реверс" или "дрифт/ручник" (в зависимости от игры).
- East (правая) нередко уходит на камеру/оглядку или вспомогательную функцию.
- Если ручник используется часто, его лучше размещать на фейс-кнопке, которую можно нажимать без конфликтов с рулем (D-pad left/right) и без необходимости отпускать газ надолго.

