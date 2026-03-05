from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import time


_SEED_TEXT_MAX_LEN = 16
_SEED_TEXT_ALLOWED = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
_FNV_OFFSET_BASIS_U32 = 0x811C9DC5
_FNV_PRIME_U32 = 0x01000193
_DEFAULT_TEXT = "WYRDWAY"


def _lcg_next_u32(seed: int) -> int:
    return ((int(seed) * 1664525) + 1013904223) & 0xFFFFFFFF


def normalize_seed_text(seed_text: str) -> str:
    src = str(seed_text).upper()
    out = ""
    i = 0
    while i < len(src) and len(out) < _SEED_TEXT_MAX_LEN:
        ch = src[i]
        if _seed_char_allowed(ch):
            out += ch
        i += 1
    if out == "":
        return _DEFAULT_TEXT
    return out


def hash_seed_text_u32(seed_text: str) -> int:
    norm = normalize_seed_text(seed_text)
    h = _FNV_OFFSET_BASIS_U32
    i = 0
    while i < len(norm):
        h ^= ord(norm[i]) & 0xFF
        h = (h * _FNV_PRIME_U32) & 0xFFFFFFFF
        i += 1
    if h == 0:
        return 1
    return int(h)


def mix_run_seed(campaign_seed_u32: int, run_index: int) -> int:
    idx = int(run_index)
    if idx < 1:
        idx = 1
    mixed = (
        int(campaign_seed_u32)
        ^ ((idx * 0x9E3779B9) & 0xFFFFFFFF)
    ) & 0xFFFFFFFF
    seed = _lcg_next_u32(mixed)
    if seed == 0:
        seed = 1
    return int(seed)


def generate_seed_text_default() -> str:
    entropy = int(time()) & 0xFFFFFFFF
    if entropy == 0:
        entropy = 0x13579BDF
    seed = _lcg_next_u32(entropy ^ 0xA5A5A5A5)
    out = ""
    i = 0
    n = len(_SEED_TEXT_ALLOWED)
    while i < 8:
        seed = _lcg_next_u32(seed ^ ((i + 1) * 0x85EBCA6B))
        out += _SEED_TEXT_ALLOWED[int(seed % n)]
        i += 1
    return out


def seed_editor_alphabet() -> str:
    return _SEED_TEXT_ALLOWED


def seed_text_max_len() -> int:
    return _SEED_TEXT_MAX_LEN


def seed_cycle_char(ch: str, forward: bool) -> str:
    char = str(ch).upper()
    if len(char) != 1 or not _seed_char_allowed(char):
        char = _SEED_TEXT_ALLOWED[0]
    idx = _SEED_TEXT_ALLOWED.find(char)
    if idx < 0:
        idx = 0
    if forward:
        idx += 1
        if idx >= len(_SEED_TEXT_ALLOWED):
            idx = 0
    else:
        idx -= 1
        if idx < 0:
            idx = len(_SEED_TEXT_ALLOWED) - 1
    return _SEED_TEXT_ALLOWED[idx]


def _seed_char_allowed(ch: str) -> bool:
    return _SEED_TEXT_ALLOWED.find(ch) >= 0
