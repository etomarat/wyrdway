from typing import Callable


def btn(id: int) -> bool:
    """Эта функция позволяет читать состояние одной из кнопок, подключенных к TIC.
    Функция возвращает true, если клавиша с указанным id сейчас нажата.
    Она остается true, пока клавиша удерживается.
    Если нужно проверить, что клавиша была только что нажата, используйте `btnp()` вместо этого.

    This function allows you to read the status of one of the buttons attached to TIC.
    The function returns true if the key with the supplied id is currently in the pressed state.
    It remains true for as long as the key is held down.
    If you want to test if a key was just pressed, use `btnp()` instead."""
    ...


def btnp(id: int, hold: int = -1, period: int = -1) -> bool:
    """Эта функция позволяет читать состояние одной из кнопок TIC.
    Она возвращает true только если клавиша была нажата с момента последнего кадра.
    Также можно использовать необязательные параметры hold и period, которые позволяют проверять, удерживается ли кнопка.
    После того как пройдет время, заданное hold, btnp будет возвращать true каждый раз, когда пройдет период, если клавиша все еще нажата.
    Например, чтобы повторно проверить состояние кнопки `0` через 2 секунды и затем продолжать проверять ее состояние каждые 1/10 секунды, используйте btnp(0, 120, 6).
    Поскольку время выражается в тиках и TIC работает на 60 кадрах в секунду, мы используем значение 120 для ожидания 2 секунд и 6 тиков (то есть 60/10) как интервал повторной проверки.

    This function allows you to read the status of one of TIC's buttons.
    It returns true only if the key has been pressed since the last frame.
    You can also use the optional hold and period parameters which allow you to check if a button is being held down.
    After the time specified by hold has elapsed, btnp will return true each time period is passed if the key is still down.
    For example, to re-examine the state of button `0` after 2 seconds and continue to check its state every 1/10th of a second, you would use btnp(0, 120, 6).
    Since time is expressed in ticks and TIC runs at 60 frames per second, we use the value of 120 to wait 2 seconds and 6 ticks (ie 60/10) as the interval for re-checking.
    """
    ...


def circ(x: int, y: int, radius: int, color: int) -> None:
    """Эта функция рисует заполненный круг нужного радиуса и цвета с центром в x, y.
    Использует алгоритм Брезенхэма.

    This function draws a filled circle of the desired radius and color with its center at x, y.
    It uses the Bresenham algorithm."""
    ...


def circb(x: int, y: int, radius: int, color: int) -> None:
    """Рисует окружность с центром в x, y, используя заданные радиус и цвет.
    Использует алгоритм Брезенхэма.

    Draws the circumference of a circle with its center at x, y using the radius and color requested.
    It uses the Bresenham algorithm."""
    ...


def clip(x: int, y: int, width: int, height: int) -> None:
    """Эта функция ограничивает рисование областью отсечения или `viewport`, заданной x,y,w,h.
    Все, что рисуется за пределами этой области, не будет видно.
    Вызов clip() без параметров сбросит область рисования на весь экран.

    This function limits drawing to a clipping region or `viewport` defined by x,y,w,h.
    Things drawn outside of this area will not be visible.
    Calling clip() with no parameters will reset the drawing area to the entire screen.
    """
    ...


def cls(color: int = 0) -> None:
    """Очистить экран.
    При вызове эта функция очищает весь экран цветом, переданным в аргументе.
    Если параметр не передан, используется первый цвет (0).

    Clear the screen.
    When called this function clear all the screen using the color passed as argument.
    If no parameter is passed first color (0) is used."""
    ...


def elli(x: int, y: int, a: int, b: int, color: int) -> None:
    """Эта функция рисует заполненный эллипс с нужными радиусами a, b и цветом с центром в x, y.
    Использует алгоритм Брезенхэма.

    This function draws a filled ellipse of the desired a, b radiuses and color with its center at x, y.
    It uses the Bresenham algorithm."""
    ...


def ellib(x: int, y: int, a: int, b: int, color: int) -> None:
    """Эта функция рисует контур эллипса с нужными радиусами a, b и цветом с центром в x, y.
    Использует алгоритм Брезенхэма.

    This function draws an ellipse border with the desired radiuses a b and color with its center at x, y.
    It uses the Bresenham algorithm."""
    ...


def exit() -> None:
    """Прерывает выполнение программы и возвращает в консоль, когда функция TIC заканчивается.

    Interrupts program execution and returns to the console when the TIC function ends."""
    ...


def fget(sprite_id: int, flag: int) -> bool:
    """Возвращает true, если указанный флаг спрайта установлен. Подробнее см. `fset()`.

    Returns true if the specified flag of the sprite is set. See `fset()` for more details."""
    ...


def font(
    text: str,
    x: int,
    y: int,
    chromakey: int,
    char_width: int = 8,
    char_height: int = 8,
    fixed: bool = False,
    scale: int = 1,
    alt: bool = False,
) -> int:
    """Печатает строку шрифтом, заданным в спрайтах переднего плана.
    Чтобы просто печатать на экран, см. `print()`.
    Чтобы печатать в консоль, см. `trace()`.

    Print string with font defined in foreground sprites.
    To simply print to the screen, check out `print()`.
    To print to the console, check out `trace()`."""
    ...


def fset(sprite_id: int, flag: int, b: bool) -> None:
    """Каждый спрайт имеет восемь флагов, которые можно использовать для хранения информации или сигнализации разных условий.
    Например, флаг 0 может указывать, что спрайт невидим, флаг 6 может указывать, что спрайт нужно рисовать масштабированным и т. п.
    См. также `fget()`.

    Each sprite has eight flags which can be used to store information or signal different conditions.
    For example, flag 0 might be used to indicate that the sprite is invisible, flag 6 might indicate that the flag should be draw scaled etc.
    See also `fget()`."""
    ...


def key(code: int = -1) -> bool:
    """Функция возвращает true, если клавиша, обозначенная keycode, нажата.

    The function returns true if the key denoted by keycode is pressed."""
    ...


def keyp(code: int = -1, hold: int = -1, period: int = -17) -> int:
    """Эта функция возвращает true, если указанная клавиша нажата, но в предыдущем кадре не была нажата.
    Подробности о параметрах hold и period см. в `btnp()`.

    This function returns true if the given key is pressed but wasn't pressed in the previous frame.
    Refer to `btnp()` for an explanation of the optional hold and period parameters."""
    ...


def line(x0: int, y0: int, x1: int, y1: int, color: int) -> None:
    """Рисует прямую линию из точки (x0,y0) в точку (x1,y1) указанным цветом.

    Draws a straight line from point (x0,y0) to point (x1,y1) in the specified color."""
    ...


def map(
    x: int = 0,
    y: int = 0,
    w: int = 30,
    h: int = 17,
    sx: int = 0,
    sy: int = 0,
    colorkey: int = -1,
    scale: int = 1,
    remap: Callable[[int, int, int], tuple[int, int, int]] | None = None,
) -> None:
    """Карта состоит из ячеек 8x8 пикселей, каждая из которых может быть заполнена спрайтом с помощью редактора карты.
    Карта может быть до 240 ячеек в ширину и 136 в высоту.
    Эта функция рисует выбранную область карты в заданную позицию экрана.
    Например, map(5,5,12,10,0,0) нарисует участок 12x10, начиная с координат карты (5,5) в позицию экрана (0,0).
    Последний параметр функции map — это мощный callback, позволяющий менять то, как рисуются ячейки карты (спрайты) при вызове map.
    Его можно использовать для поворота, отражения и замены спрайтов во время игры.
    В отличие от mset, который сохраняет изменения в карте, эту специальную функцию можно использовать для создания анимированных тайлов или полной замены.
    Некоторые примеры: менять спрайты на открытые двери, скрывать спрайты, используемые для спавна объектов в игре, и даже порождать сами объекты.
    Тайлмап расположен последовательно в RAM — запись 1 в 0x08000 приведет к появлению тайла (спрайта) #1 в левом верхнем углу при вызове map().
    Чтобы установить тайл непосредственно ниже, нужно записать в 0x08000 + 240, то есть 0x080F0.

    The map consists of cells of 8x8 pixels, each of which can be filled with a sprite using the map editor.
    The map can be up to 240 cells wide by 136 deep.
    This function will draw the desired area of the map to a specified screen position.
    For example, map(5,5,12,10,0,0) will draw a 12x10 section of the map, starting from map coordinates (5,5) to screen position (0,0).
    The map function's last parameter is a powerful callback function for changing how map cells (sprites) are drawn when map is called.
    It can be used to rotate, flip and replace sprites while the game is running.
    Unlike mset, which saves changes to the map, this special function can be used to create animated tiles or replace them completely.
    Some examples include changing sprites to open doorways, hiding sprites used to spawn objects in your game and even to emit the objects themselves.
    The tilemap is laid out sequentially in RAM - writing 1 to 0x08000 will cause tile(sprite) #1 to appear at top left when map() is called.
    To set the tile immediately below this we need to write to 0x08000 + 240, ie 0x080F0.
    """
    ...


def memcpy(dest: int, source: int, size: int) -> None:
    """Эта функция позволяет копировать непрерывный блок 96К RAM TIC с одного адреса на другой.
    Адреса указываются в шестнадцатеричном формате, значения — в десятичном.

    This function allows you to copy a continuous block of TIC's 96K RAM from one address to another.
    Addresses are specified are in hexadecimal format, values are decimal."""
    ...


def memset(dest: int, value: int, size: int) -> None:
    """Эта функция позволяет заполнить непрерывный блок любой части RAM TIC одним и тем же значением.
    Адрес указывается в шестнадцатеричном формате, значение — в десятичном.

    This function allows you to set a continuous block of any part of TIC's RAM to the same value.
    The address is specified in hexadecimal format, the value in decimal."""
    ...


def mget(x: int, y: int) -> int:
    """Возвращает id спрайта в заданных координатах карты x и y.

    Gets the sprite id at the given x and y map coordinate."""
    ...


def mouse() -> tuple[int, int, bool, bool, bool, int, int]:
    """Эта функция возвращает координаты мыши и булево значение для состояния каждой кнопки мыши; true означает, что кнопка нажата.

    This function returns the mouse coordinates and a boolean value for the state of each mouse button, with true indicating that a button is pressed."""
    ...


def mset(x: int, y: int, tile_id: int) -> None:
    """Эта функция изменяет тайл в указанных координатах карты.
    По умолчанию изменения сохраняются только пока запущена текущая игра.
    Чтобы сделать изменения постоянными в карте, см. `sync()`.
    Связанные: `map()` `mget()` `sync()`.

    This function will change the tile at the specified map coordinates.
    By default, changes made are only kept while the current game is running.
    To make permanent changes to the map, see `sync()`.
    Related: `map()` `mget()` `sync()`."""
    ...


def music(
    track: int = -1,
    frame: int = -1,
    row: int = -1,
    loop: bool = True,
    sustain: bool = False,
    tempo: int = -1,
    speed: int = -1,
):
    """Эта функция запускает воспроизведение трека, созданного в музыкальном редакторе.
    Вызов без аргументов остановит музыку.

    This function starts playing a track created in the Music Editor.
    Call without arguments to stop the music."""
    ...


def peek(addr: int, bits: int = 8) -> int:
    """Эта функция позволяет читать память TIC.
    Это полезно для доступа к ресурсам, созданным встроенными инструментами, например спрайтам, картам, звукам, данным картриджа?
    Никогда не мечтали озвучить спрайт?
    Адреса указываются в шестнадцатеричном формате, значения — в десятичном.
    Чтобы записать по адресу памяти, используйте `poke()`.
    `bits` может быть 1,2,4,8.

    This function allows to read the memory from TIC.
    It's useful to access resources created with the integrated tools like sprite, maps, sounds, cartridges data?
    Never dream to sound a sprite?
    Address are in hexadecimal format but values are decimal.
    To write to a memory address, use `poke()`.
    `bits` allowed to be 1,2,4,8."""
    ...


def peek1(addr: int) -> int:
    """Эта функция позволяет читать значения одного бита из RAM TIC.
    Адрес обычно указывается в шестнадцатеричном формате.

    This function enables you to read single bit values from TIC's RAM.
    The address is often specified in hexadecimal format."""
    ...


def peek2(addr: int) -> int:
    """Эта функция позволяет читать значения двух бит из RAM TIC.
    Адрес обычно указывается в шестнадцатеричном формате.

    This function enables you to read two bits values from TIC's RAM.
    The address is often specified in hexadecimal format."""
    ...


def peek4(addr: int) -> int:
    """Эта функция позволяет читать значения из RAM TIC.
    Адрес обычно указывается в шестнадцатеричном формате.
    См. `poke4()` для подробной информации о том, как ниббловая адресация соотносится с байтовой.

    This function enables you to read values from TIC's RAM.
    The address is often specified in hexadecimal format.
    See 'poke4()' for detailed information on how nibble addressing compares with byte addressing.
    """
    ...


def pix(x: int, y: int, color: int | None = None) -> int | None:
    """Эта функция может читать или записывать значения цвета пикселей.
    При вызове с параметром color пиксель в указанных координатах устанавливается в этот цвет.
    Вызов функции без параметра color возвращает цвет пикселя в указанной позиции.

    This function can read or write pixel color values.
    When called with a color parameter, the pixel at the specified coordinates is set to that color.
    Calling the function without a color parameter returns the color of the pixel at the specified position.
    """
    ...


def pmem(index: int, value: int | None = None) -> int:
    """Эта функция позволяет сохранять и получать данные в одном из 256 отдельных 32-битных слотов, доступных в постоянной памяти картриджа.
    Это полезно для сохранения рекордов, прогресса уровней или достижений.
    Данные хранятся как беззнаковые 32-битные целые (от 0 до 4294967295).

    Советы:
    - pmem зависит от хэша картриджа (md5), поэтому не меняйте ваш lua-скрипт, если хотите сохранить данные.
    - Используйте `saveid:` с персонализированной строкой в метаданных заголовка, чтобы переопределить стандартный расчет MD5.
    Это позволяет пользователю обновлять картридж, не теряя сохраненные данные.

    This function allows you to save and retrieve data in one of the 256 individual 32-bit slots available in the cartridge's persistent memory.
    This is useful for saving high-scores, level advancement or achievements.
    The data is stored as unsigned 32-bit integers (from 0 to 4294967295).

    Tips:
    - pmem depends on the cartridge hash (md5), so don't change your lua script if you want to keep the data.
    - Use `saveid:` with a personalized string in the header metadata to override the default MD5 calculation.
    This allows the user to update a cart without losing their saved data."""
    ...


def poke(addr: int, value: int, bits: int = 8) -> None:
    """Эта функция позволяет записывать один байт по любому адресу в RAM TIC.
    Адрес должен быть указан в шестнадцатеричном формате, значение — в десятичном.
    `bits` может быть 1,2,4,8.

    This function allows you to write a single byte to any address in TIC's RAM.
    The address should be specified in hexadecimal format, the value in decimal.
    `bits` allowed to be 1,2,4,8."""
    ...


def poke1(addr: int, value: int) -> None:
    """Эта функция позволяет напрямую записывать значения одного бита в RAM.
    Адрес обычно указывается в шестнадцатеричном формате.

    This function allows you to write single bit values directly to RAM.
    The address is often specified in hexadecimal format."""
    ...


def poke2(addr: int, value: int) -> None:
    """Эта функция позволяет напрямую записывать значения двух бит в RAM.
    Адрес обычно указывается в шестнадцатеричном формате.

    This function allows you to write two bits values directly to RAM.
    The address is often specified in hexadecimal format."""
    ...


def poke4(addr: int, value: int) -> None:
    """Эта функция позволяет напрямую записывать в RAM.
    Адрес обычно указывается в шестнадцатеричном формате.
    Для peek4 и poke4 RAM адресуется сегментами по 4 бита (нибблами).
    Поэтому, чтобы получить доступ к RAM по байтовому адресу 0x4000,
    нужно обращаться к адресам нибблов 0x8000 и 0x8001.

    This function allows you to write directly to RAM.
    The address is often specified in hexadecimal format.
    For both peek4 and poke4 RAM is addressed in 4 bit segments (nibbles).
    Therefore, to access the the RAM at byte address 0x4000
    you would need to access both the 0x8000 and 0x8001 nibble addresses."""
    ...


def print(
    text: str,
    x: int = 0,
    y: int = 0,
    color: int = 15,
    fixed: bool = False,
    scale: int = 1,
    alt: bool = False,
) -> None:
    """Это просто выводит текст на экран с использованием шрифта, заданного в config.
    Когда fixed установлен в true, опция фиксированной ширины гарантирует, что каждый символ будет напечатан в `box` одинакового размера, поэтому, например, символ `i` будет занимать ту же ширину, что и символ `w`.
    Когда fixed равен false, между каждым символом будет один пробел.

    Советы:
    - Чтобы использовать пользовательский растровый шрифт, см. `font()`.
    - Чтобы печатать в консоль, см. `trace()`.

    This will simply print text to the screen using the font defined in config.
    When set to true, the fixed width option ensures that each character will be printed in a `box` of the same size, so the character `i` will occupy the same width as the character `w` for example.
    When fixed width is false, there will be a single space between each character.

    Tips:
    - To use a custom rastered font, check out `font()`.
    - To print to the console, check out `trace()`."""
    ...


def rect(x: int, y: int, w: int, h: int, color: int) -> None:
    """Эта функция рисует заполненный прямоугольник нужного размера и цвета в указанной позиции.
    Если нужно рисовать только границу или контур прямоугольника (то есть не заполненный), см. `rectb()`.

    This function draws a filled rectangle of the desired size and color at the specified position.
    If you only need to draw the the border or outline of a rectangle (ie not filled) see `rectb()`.
    """
    ...


def rectb(x: int, y: int, w: int, h: int, color: int) -> None:
    """Эта функция рисует границу прямоугольника толщиной в один пиксель в указанной позиции.
    Если нужно заполнить прямоугольник цветом, см. `rect()`.

    This function draws a one pixel thick rectangle border at the position requested.
    If you need to fill the rectangle with a color, see `rect()` instead."""
    ...


def reset() -> None:
    """Сбрасывает картридж. Чтобы вернуться в консоль, см. `exit()`.

    Resets the cartridge. To return to the console, see the `exit()`."""
    ...


def sfx(
    id: int,
    note: int = -1,
    duration: int = -1,
    channel: int = 0,
    volume: int = 15,
    speed: int = 0,
) -> None:
    """Эта функция воспроизводит звук с `id`, созданный в редакторе sfx.
    Вызов функции с id, равным -1, остановит воспроизведение канала.
    Ноту можно задать целым числом от 0 до 95 (представляет 8 октав по 12 нот каждая) или строкой с названием ноты и октавой.
    Например, значение ноты `14` воспроизведет ноту `D` во второй октаве.
    Ту же ноту можно задать строкой `D-2`.
    Названия нот состоят из двух символов: сама нота (в верхнем регистре), затем `-` для натуральной ноты или `#` для диеза.
    Обозначений для бемолей нет.
    Доступные названия нот: C-, C#, D-, D#, E-, F-, F#, G-, G#, A-, A#, B-.
    `octave` задается одной цифрой в диапазоне от 0 до 8.
    `duration` задает, сколько тиков воспроизводить звук; поскольку TIC-80 работает на 60 кадрах в секунду, значение 30 соответствует половине секунды.
    Значение -1 будет воспроизводить звук непрерывно.
    Параметр `channel` указывает, какой из четырех каналов использовать. Допустимые значения — от 0 до 3.
    `volume` может быть от 0 до 15.
    `speed` в диапазоне от -4 до 3 задает, сколько `ticks+1` воспроизводить каждый шаг, так что speed==0 означает 1 тик на шаг.

    This function will play the sound with `id` created in the sfx editor.
    Calling the function with id set to -1 will stop playing the channel.
    The note can be supplied as an integer between 0 and 95 (representing 8 octaves of 12 notes each) or as a string giving the note name and octave.
    For example, a note value of `14` will play the note `D` in the second octave.
    The same note could be specified by the string `D-2`.
    Note names consist of two characters, the note itself (in upper case) followed by `-` to represent the natural note or `#` to represent a sharp.
    There is no option to indicate flat values.
    The available note names are therefore: C-, C#, D-, D#, E-, F-, F#, G-, G#, A-, A#, B-.
    The `octave` is specified using a single digit in the range 0 to 8.
    The `duration` specifies how many ticks to play the sound for since TIC-80 runs at 60 frames per second, a value of 30 represents half a second.
    A value of -1 will play the sound continuously.
    The `channel` parameter indicates which of the four channels to use. Allowed values are 0 to 3.
    The `volume` can be between 0 and 15.
    The `speed` in the range -4 to 3 can be specified and means how many `ticks+1` to play each step, so speed==0 means 1 tick per step.
    """
    ...


def spr(
    id: int,
    x: int,
    y: int,
    colorkey: int = -1,
    scale: int = 1,
    flip: int = 0,
    rotate: int = 0,
    w: int = 1,
    h: int = 1,
) -> None:
    """Рисует спрайт с номером index в координатах x и y.
    Можно указать colorkey в палитре, который будет использоваться как прозрачный цвет, или использовать значение -1 для непрозрачного спрайта.
    Спрайт можно масштабировать на нужный коэффициент. Например, коэффициент 2 означает, что спрайт 8x8 пикселей рисуется в области 16x16 на экране.
    Можно отражать спрайт, где:
    - 0 = нет отражения
    - 1 = отражение по горизонтали
    - 2 = отражение по вертикали
    - 3 = отражение по вертикали и горизонтали
    При повороте спрайта он вращается по часовой стрелке шагами по 90:
    - 0 = без поворота
    - 1 = поворот на 90
    - 2 = поворот на 180
    - 3 = поворот на 270
    Можно рисовать составной спрайт (состоящий из прямоугольной области спрайтов из таблицы спрайтов), задав параметры `w` и `h` (по умолчанию 1).

    Draws the sprite number index at the x and y coordinate.
    You can specify a colorkey in the palette which will be used as the transparent color or use a value of -1 for an opaque sprite.
    The sprite can be scaled up by a desired factor. For example, a scale factor of 2 means an 8x8 pixel sprite is drawn to a 16x16 area of the screen.
    You can flip the sprite where:
    - 0 = No Flip
    - 1 = Flip horizontally
    - 2 = Flip vertically
    - 3 = Flip both vertically and horizontally
    When you rotate the sprite, it's rotated clockwise in 90 steps:
    - 0 = No rotation
    - 1 = 90 rotation
    - 2 = 180 rotation
    - 3 = 270 rotation
    You can draw a composite sprite (consisting of a rectangular region of sprites from the sprite sheet) by specifying the `w` and `h` parameters (which default to 1).
    """
    ...


def sync(mask: int = 0, bank: int = 0, tocart: bool = False) -> None:
    """Pro-версия TIC-80 содержит 8 банков памяти.
    Чтобы переключаться между этими банками, sync можно использовать для загрузки содержимого банка в рантайм или для сохранения содержимого активного рантайма в банк.
    Функцию можно вызывать только один раз за кадр. Если вы изменяли память рантайма (например, используя mset), вы можете сбросить активное состояние, вызвав sync(0,0,false).
    Это сбрасывает всю память рантайма к содержимому банка 0. Обратите внимание, что sync не используется для загрузки кода из банков; это происходит автоматически.

    The pro version of TIC-80 contains 8 memory banks.
    To switch between these banks, sync can be used to either load contents from a memory bank to runtime, or save contents from the active runtime to a bank.
    The function can only be called once per frame. If you have manipulated the runtime memory (e.g. by using mset), you can reset the active state by calling sync(0,0,false).
    This resets the whole runtime memory to the contents of bank 0. Note that sync is not used to load code from banks; this is done automatically.
    """
    ...


def ttri(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    x3: float,
    y3: float,
    u1: float,
    v1: float,
    u2: float,
    v2: float,
    u3: float,
    v3: float,
    texsrc: int = 0,
    chromakey: int = -1,
    z1: float = 0.0,
    z2: float = 0.0,
    z3: float = 0.0,
) -> None:
    """Рендерит треугольник, заполненный текстурой из image ram, map ram или vbank.
    Используется в 3D-графике.
    В частности, если вершины треугольника имеют разную 3D-глубину, можно увидеть искажение.
    Это можно представить как окно внутри image ram (таблицы спрайтов), map ram или другого vbank.
    Обратите внимание, что таблица спрайтов или карта в этом случае рассматриваются как единое большое изображение, а адресация U и V обращается непосредственно к пикселям, а не по ID спрайта.
    Так, например, левый верхний угол спрайта #2 будет находиться в u=16, v=0.

    It renders a triangle filled with texture from image ram, map ram or vbank.
    Use in 3D graphics.
    In particular, if the vertices in the triangle have different 3D depth, you may see some distortion.
    These can be thought of as the window inside image ram (sprite sheet), map ram or another vbank.
    Note that the sprite sheet or map in this case is treated as a single large image, with U and V addressing its pixels directly, rather than by sprite ID.
    So for example the top left corner of sprite #2 would be located at u=16, v=0."""
    ...


def time() -> int:
    """Эта функция возвращает количество миллисекунд, прошедших с начала выполнения картриджа.
    Полезно для отслеживания времени, анимации объектов и запуска событий.

    This function returns the number of milliseconds elapsed since the cartridge began execution.
    Useful for keeping track of time, animating items and triggering events."""
    ...


def trace(message: str, color: int = 15) -> None:
    """Это служебная функция, полезная для отладки вашего кода.
    Она выводит параметр message в консоль указанным (опциональным) цветом.

    Советы:
    - Конкатенатор строк в Lua — это .. (две точки).
    - Используйте команду консоли cls, чтобы очистить вывод trace.

    This is a service function, useful for debugging your code.
    It prints the message parameter to the console in the (optional) color specified.

    Tips:
    - The Lua concatenator for strings is .. (two points).
    - Use console cls command to clear the output from trace."""
    ...


def tri(
    x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, color: int
) -> None:
    """Эта функция рисует треугольник, заполненный цветом, используя заданные вершины.

    This function draws a triangle filled with color, using the supplied vertices."""
    ...


def trib(
    x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, color: int
) -> None:
    """Эта функция рисует контур треугольника цветом, используя заданные вершины.

    This function draws a triangle border with color, using the supplied vertices."""
    ...


def tstamp() -> int:
    """Эта функция возвращает количество секунд, прошедших с 1 января 1970 года.
    Полезно для создания постоянных игр, которые развиваются со временем между запусками.

    This function returns the number of seconds elapsed since January 1st, 1970.
    Useful for creating persistent games which evolve over time between plays."""
    ...


def vbank(bank: int | None = None) -> int:
    """VRAM содержит 2x16K микросхем памяти; используйте vbank(0) или vbank(1), чтобы переключаться между ними.

    VRAM contains 2x16K memory chips, use vbank(0) or vbank(1) to switch between them."""
    ...


def include(path: str) -> None:
  """
  Директива бандлера TIC-80.

  Эта функция **не** выполняется TIC-80 Python во время выполнения.
  Это маркер препроцессора, который ваш бандлер заменяет на
  содержимое другого исходного файла **до** загрузки кода в TIC-80.

  Примеры:
    include("test")        # встраивает ./test.py
    include("util.math")   # встраивает ./util/math.py

  Примечания:
    - `include()` обычно внедряет имена в текущую область модуля,
      похоже на копирование кода.
    - Проверяльщики типов (Pyright/Mypy) не могут вывести, какие имена появляются после
      `include()`. Если нужен IntelliSense для внедряемых имен, добавьте
      импорт только для TYPE_CHECKING рядом с include.

  Рекомендуемый шаблон:
    include("test")

    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
      from test import msg

  TIC-80 bundler directive.

  This function is **not** executed by TIC-80 Python at runtime.
  It is a preprocessor marker that your bundler replaces with the
  contents of another source file **before** the code is loaded into TIC-80.

  Examples:
    include("test")        # inlines ./test.py
    include("util.math")   # inlines ./util/math.py

  Notes:
    - `include()` usually injects names into the current module scope,
      similar to copy-pasting code.
    - Type checkers (Pyright/Mypy) cannot infer which names appear after
      `include()`. If you need IntelliSense for injected names, add a
      TYPE_CHECKING-only import next to the include statement.

  Recommended pattern:
    include("test")

    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
      from test import msg
  """
  ...
