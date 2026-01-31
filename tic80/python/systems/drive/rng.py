class Rng:
    """RNG = Random Number Generator (генератор псевдо-случайных чисел).

    Зачем свой RNG:
    - в TIC-80/PocketPy нельзя рассчитывать на полноту стандартной библиотеки
      CPython (например, модуль `random` может отсутствовать/быть урезанным);
    - нам нужен детерминизм по seed (одна и та же дорога при одном seed),
      чтобы сравнивать A/B рендеры и настраивать баланс;
    - алгоритм должен быть быстрым, маленьким и без аллокаций.

    Как работает:
    - используется xorshift32 (George Marsaglia): состояние — один 32-битный int;
    - `next_u32()` делает три шага "xor + shift":
        x ^= x << 13
        x ^= x >> 17
        x ^= x << 5
      Числа 13/17/5 — это стандартные параметры xorshift32, подобранные так,
      чтобы давать нормальную статистику при минимальной цене;
    - `0xFFFFFFFF` — маска, чтобы держать значения в диапазоне 32 бит;
    - `4294967296.0` — это 2**32, нужно чтобы получить float в [0..1).

    Важно:
    - нулевое состояние для xorshift даёт нулевой поток, поэтому seed=0
      заменяем на фиксированную константу `0x12345678`.
    """

    def __init__(self, seed: int) -> None:
        s = seed & 0xFFFFFFFF
        if s == 0:
            s = 0x12345678
        self._state = s

    def next_u32(self) -> int:
        x = self._state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        self._state = x & 0xFFFFFFFF
        return self._state

    def rand01(self) -> float:
        return self.next_u32() / 4294967296.0

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.rand01()
