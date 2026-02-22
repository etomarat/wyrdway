class PursuerTextBank:
    __slots__ = ()

    _PRIME_WORDS = [
        "void",
        "def",
        "class",
        "struct",
        "typedef",
        "enum",
        "union",
        "static",
        "extern",
        "const",
        "volatile",
        "return",
        "sizeof",
        "NULL",
        "malloc",
        "free",
        "import",
        "lambda",
        "async",
        "await",
        "protocol",
        "module",
        "sentinel",
        "oracle"
    ]
    _ENTITY_WORDS = [
        "0x00",
        "0x1F",
        "0x2A",
        "0x3C",
        "0x7E",
        "0xA0",
        "0xB7",
        "0xFF",
        "jmp",
        "mov",
        "xor",
        "and",
        "or",
        "shl",
        "shr",
        "irq",
        "nmi",
        "ptr",
        "reg",
        "eax",
        "rsp",
        "seg",
        "addr",
        "bus"
    ]
    _ENTITY_ERRORS = [
        "SIGSEGV",
        "SEGFAULT",
        "ILLEGAL OPCODE",
        "STACK SMASH",
        "NULL PTR",
        "BAD ADDR",
        "IRQ LOST",
        "TRAP 0x0D",
        "RING VIOLATION"
    ]
    _PRIME_ERRORS = [
        "ACCESS VIOLATION",
        "UNHANDLED EXCEPTION",
        "HEAP CORRUPTION",
        "STACK OVERFLOW",
        "INTEGRITY FAILURE",
        "FORBIDDEN CALL",
        "STATE CORRUPTED",
        "THREAD DEADLOCK",
        "WATCHDOG TIMEOUT",
        "SYSTEM HALTED",
        "MEMORY POISONED",
        "PANIC: NO RETURN"
    ]

    @staticmethod
    def _pick_text(items: list[str], idx: int) -> str:
        n = len(items)
        if n <= 0:
            return ""
        return items[idx % n]

    def code_shard_text(self, idx: int) -> str:
        return self._pick_text(self._PRIME_WORDS, idx)

    def entity_whisper_text(self, idx: int) -> str:
        return self._pick_text(self._ENTITY_WORDS, idx)

    def entity_error_text(self, idx: int) -> str:
        return self._pick_text(self._ENTITY_ERRORS, idx)

    def prime_error_text(self, idx: int) -> str:
        return self._pick_text(self._PRIME_ERRORS, idx)
