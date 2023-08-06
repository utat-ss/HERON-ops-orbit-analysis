import numpy as np
from celest import units as u
from supernova.api import propagate_orbit

from hermes.celest_helpers import ecef_to_eci, jd2000_to_datetime
from hermes.utils import jd_0_from_epoch_ts, day_frac_from_epoch_ts
from hermes.tle import TLE


def propagate_from_sv_and_timestamp(
    sv_ecef: np.ndarray,
    timestamp: str,
    calendar_year: int,
    days_to_run: float,
) -> tuple[tuple[TLE, TLE], tuple[np.ndarray, np.ndarray]]:
    """Propagate HERON's orbit from a state vector (ECEF, m) and a timestamp.

    Performs the following steps:
    - converts the state vector to ECI
    - parses the timestamp to a Julian date
    - generates initial TLE
    - propagates the orbit using supernova
    - generates final TLE and ECI states

    Parameters
    ----------
    sv_ecef : np.ndarray
        [x, y, z, vx, vy, vz] in ECEF frame, in meters
    timestamp : str
        Timestamp in format "d:hh:mm:ss.sss", relative to some calendar year
    calendar_year : int
        Year of the calendar to use for the timestamp
    days_to_run : float
        Number of days to propagate for

    Returns
    -------
    ((initial_tle, final_tle), (timesteps, states))
    """
    # Calculate initial time information
    jd_0 = jd_0_from_epoch_ts(timestamp, calendar_year)
    epoch_dt = jd2000_to_datetime(u.Quantity(jd_0, u.jd2000))
    day_frac = day_frac_from_epoch_ts(timestamp)

    # Get initial State and TLE
    t_span = [0, 86400 * days_to_run]
    y0 = ecef_to_eci(sv_ecef, jd_0).tolist()

    initial_tle = TLE.from_cartesian_state(
        np.array(y0[:3]), np.array(y0[3:]), TLE.null_tle(), epoch_dt.year, day_frac
    )

    # Propagate
    t, y = propagate_orbit("RK810", "simplified", t_span, y0, 1e-6)

    final_tle = TLE.from_cartesian_state(
        y[-1, :3], y[-1, 3:], TLE.null_tle(), epoch_dt.year, day_frac + days_to_run
    )

    return ((initial_tle, final_tle), (t, y))
