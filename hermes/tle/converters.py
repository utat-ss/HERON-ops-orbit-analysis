def line_checksum(line: str) -> int:
    """
    Computes a checksum for line based on the following rules
    1. Add all numerical digits in the line together.
    2. Add 1 for each dash ('-') in the line
    3. Ignore all other characters

    Returns mod10 of the sum.
    """
    return (sum(int(c) for c in line if c.isdigit()) + line.count("-")) % 10


def parse_decimal(s: str) -> float:
    """Parse a floating point with implicit leading dot.

    >>> _parse_decimal('378')
    0.378
    """
    return float("." + s)


def print_decimal(f: float) -> str:
    """
    prints a float without leading "0."

    >>> _print_decimal(0.378)
    "378"
    """
    return f"{f:.7f}"[2:]


def parse_float(s: str) -> float:
    """Parse a floating point with implicit dot and exponential notation.

    >>> _parse_float(' 12345-3')
    0.00012345
    >>> _parse_float('+12345-3')
    0.00012345
    >>> _parse_float('-12345-3')
    -0.00012345
    """
    return float(s[0] + "." + s[1:6] + "e" + s[6:8])


def print_float(f: float) -> str:
    """Prints a floating point with implicit dot and exponential notation.

    >>> _print_float(0.00012345)
    "12345-3"

    >>> _print_float(0)
    "00000-0"
    """
    s = f"{f:.4e}"
    numeric_portion = int(s[0] + s[2:6])
    exponent = int(s[7:]) + 1
    if exponent == 1:
        exponent = "-0"
    return f"{numeric_portion:05d}{exponent}"
