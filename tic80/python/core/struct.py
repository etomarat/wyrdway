def struct_field(index: int):
    """Создать `property`, читающий/пишущий поле из list-хранилища `_v` по индексу.

    В PocketPy/TIC-80 присваивания вида `obj.x = ...` не вызывают `__setattr__`
    (по результатам проб). Поэтому для перехвата записи и синхронизации с `_v`
    мы используем `property` setter.
    """
    def _get(self):
        return self._v[index]

    def _set(self, value):
        self._v[index] = value

    return property(_get, _set)


class Struct:
    """Упакованная модель данных на list-хранилище + `property` поля.

    Зачем это нужно в TIC-80/PocketPy:
    - `__slots__` не работает как в CPython (инстансы всё равно имеют `__dict__`).
    - `__setattr__` (и даже `__setattr__` в наследниках) по пробам не вызывается
      при `obj.x = ...` — запись идёт прямо в `__dict__`.
    - Поэтому "строгие" модели через `__setattr__` невозможны, а вот `property`
      setter работает и даёт корректную запись в упакованное хранилище `_v`.

    Использование:
    ```python
    class Player(Struct):
        __fields__ = ("x", "y", "hp")
        __defaults__ = (0, 0, 10)

        # Аннотации нужны только для IDE/Pyright:
        x: int
        y: int
        hp: int

    p = Player(x=1, y=2)
    p.hp = 7         # пишет в p._v[2]
    ```

    Ограничения:
    - Нельзя надёжно запретить "левые" поля: `p.typo = 123` создаст запись в
      `p.__dict__` (PocketPy обходит `__setattr__`). Это можно только
      диагностировать постфактум через `extra_attrs()`.
    - Поля создаются лениво (properties ставятся на класс при первом создании
      инстанса/вызове `from_dict`).
    """
    __fields__ = ()
    __defaults__ = ()
    __index__ = None

    @classmethod
    def _ensure_index(cls) -> None:
        if getattr(cls, "__index__", None) is not None:
            return

        fields = getattr(cls, "__fields__", ())
        idx = {}
        i = 0
        for name in fields:
            idx[name] = i
            i += 1
        cls.__index__ = idx

        # PocketPy in TIC-80 appears to bypass __setattr__, so properties are
        # the reliable way to keep writes in sync with `_v`.
        for name, i in idx.items():
            if name not in cls.__dict__:
                setattr(cls, name, struct_field(i))

    @classmethod
    def from_dict(cls, data: dict):
        cls._ensure_index()
        idx = cls.__index__
        if idx is None:
            raise RuntimeError("Struct.__index__ is None after _ensure_index()")

        fields = getattr(cls, "__fields__", ())
        n = len(fields)
        vals = [None] * n

        defaults = getattr(cls, "__defaults__", ())
        if defaults:
            i = 0
            for v in defaults:
                if i >= n:
                    break
                vals[i] = v
                i += 1

        for k in data:
            j = idx.get(k, -1)
            if j == -1:
                raise AttributeError("Unknown field: " + str(k))
            vals[j] = data[k]

        self = cls.__new__(cls)
        self.__dict__["_v"] = vals
        return self

    def __init__(self, *args, **kwargs) -> None:
        cls = type(self)
        cls._ensure_index()
        idx = cls.__index__
        if idx is None:
            raise RuntimeError("Struct.__index__ is None after _ensure_index()")

        fields = getattr(cls, "__fields__", ())
        n = len(fields)
        vals = [None] * n

        defaults = getattr(cls, "__defaults__", ())
        if defaults:
            i = 0
            for v in defaults:
                if i >= n:
                    break
                vals[i] = v
                i += 1

        i = 0
        for v in args:
            if i >= n:
                raise TypeError("Too many positional args")
            vals[i] = v
            i += 1

        for k in kwargs:
            j = idx.get(k, -1)
            if j == -1:
                raise AttributeError("Unknown field: " + str(k))
            vals[j] = kwargs[k]

        self.__dict__["_v"] = vals

    def extra_attrs(self) -> list[str]:
        """Вернуть "лишние" атрибуты из `__dict__`, не относящиеся к `_v`.

        Полезно для отладки опечаток в именах полей, т.к. PocketPy может молча
        создать новый атрибут (например `self.fule = ...`).
        """
        extras: list[str] = []
        for k in self.__dict__:
            if k != "_v":
                extras.append(k)
        return extras

