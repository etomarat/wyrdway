LCG_U32_A = 1664525
LCG_U32_C = 1013904223
LCG_U31_A = 1103515245
LCG_U31_C = 12345


def lcg_next_u32(seed: int) -> int:
    """LCG-шаг в 32-битном кольце (mod 2**32)."""
    return ((int(seed) * LCG_U32_A) + LCG_U32_C) & 0xFFFFFFFF


def lcg_next_u31(seed: int) -> int:
    """LCG-шаг в 31-битном кольце (mod 2**31)."""
    return ((int(seed) * LCG_U31_A) + LCG_U31_C) & 0x7FFFFFFF


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

    def randint_inclusive(self, x: int, y: int) -> int:
        """Возвращает целое число в диапазоне [x..y]."""
        if y < x:
            y = x
        span = y - x + 1
        if span <= 1:
            return x
        return x + (self.next_u32() % span)

    def choice_weighted_index(self, weights: list[float]) -> int:
        """Возвращает индекс по весам (0..n-1).

        Важно:
        - веса <= 0 игнорируются
        - если суммарный вес <= 0, возвращаем -1
        - выбор детерминированный по seed
        """
        total = 0.0
        last_pos = -1
        i = 0
        while i < len(weights):
            w = float(weights[i])
            if w > 0.0:
                total += w
                last_pos = i
            i += 1
        if total <= 0.0:
            return -1

        r = self.rand01() * total
        acc = 0.0
        i = 0
        while i < len(weights):
            w = float(weights[i])
            if w > 0.0:
                acc += w
                if r < acc:
                    return i
            i += 1

        # Из-за float округлений можем не попасть ровно в acc==total.
        return last_pos
