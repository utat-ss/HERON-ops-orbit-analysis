from .structures import TLE
from supernova.api import propagate_orbit
import numpy as np


def propagate_TLE(tle: TLE, days: float) -> TLE:
    """
    Propagates a TLE by a given number of days
    using Cowell's method.
    """
    y0 = np.concatenate(tle.cartesian_state)

    t_span = [0, 86400 * days]

    t, y = propagate_orbit("RK810", "simplified", t_span, y0, 1e-6)

    year = tle.epoch_year
    day = tle.epoch_day + days
    if day > 365:
        year += 1
        day -= 365

    final_tle = TLE.from_cartesian_state(y[-1, :3], y[-1, 3:], tle, year, day)

    return final_tle
