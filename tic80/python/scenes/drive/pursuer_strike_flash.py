def pursuer_strike_flash_n(strike_flash: float, strike_flash_seconds: float) -> float:
    if strike_flash <= 0.0:
        return 0.0
    flash_n = 1.0
    if strike_flash_seconds > 0.0001:
        flash_n = strike_flash / strike_flash_seconds
    if flash_n < 0.0:
        return 0.0
    if flash_n > 1.0:
        return 1.0
    return flash_n
