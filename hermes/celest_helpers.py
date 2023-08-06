from __future__ import annotations

from datetime import datetime

import numpy as np
from celest import units as u
from celest.coordinates import GCRS, ITRS, Coordinate, GroundLocation
from celest.encounter import generate_vtws
from celest.satellite import Satellite
from celest.time import Time

from hermes.constants import (
    HERON_NORTH_OCCLUSION_ANGLE,
    HERON_SOUTH_OCCLUSION_ANGLE,
    TORONTO_GS,
)


def jd2000_to_datetime(jd2000: u.Quantity) -> datetime:
    # length-1 quanitity only
    return Time(jd2000.data).datetime()[0]


def ecef_to_eci(y_ecef: np.ndarray, jd: float) -> np.ndarray:
    """
    Convert ECEF coordinates to ECI coordinates using celest,
    in a manner which can be used by supernova.

    Parameters
    ----------
    y_ecef : np.ndarray
        ECEF coordinates in the form [x, y, z, x_dot, y_dot, z_dot]
    jd : float
        Julian date in the JD2000 epoch.

    Returns
    -------
    np.ndarray
        ECI coordinates in the form [x, y, z, x_dot, y_dot, z_dot]
    """
    pos_ecef = Coordinate(
        ITRS(
            np.array([jd]),
            np.array([y_ecef[0]]),
            np.array([y_ecef[1]]),
            np.array([y_ecef[2]]),
            u.m,
        )
    )
    vel_ecef = Coordinate(
        ITRS(
            np.array([jd]),
            np.array([y_ecef[3]]),
            np.array([y_ecef[4]]),
            np.array([y_ecef[5]]),
            u.m / u.s,
        )
    )

    pos_eci = pos_ecef.convert_to(GCRS)
    vel_eci = vel_ecef.convert_to(GCRS)

    state_dirty: list[u.Quantity] = [
        pos_eci.x,
        pos_eci.y,
        pos_eci.z,
        vel_eci.x,
        vel_eci.y,
        vel_eci.z,
    ]

    state_clean: list[float] = [q.data[0] for q in state_dirty]

    return np.array(state_clean)


def process_encounters(
    t: np.ndarray,
    y: np.ndarray,
    jd_0: float,
    cutoff_angles: list[float] = [
        HERON_NORTH_OCCLUSION_ANGLE,
        HERON_SOUTH_OCCLUSION_ANGLE,
    ],
    location: GroundLocation = TORONTO_GS,
) -> None:
    """
    Process the encounters found by supernova, using celest.

    Parameters
    ----------
    t : np.ndarray
        mission elapsed time in seconds, of shape (n,)
    y : np.ndarray
        state vector in the form [x, y, z, x_dot, y_dot, z_dot], of shape (n, 6)
    jd_0 : float
        Julian date in the JD2000 epoch.
    cutoff_angles : list[float]
        List of cutoff angles in degrees, for which to generate VTWS.
    location : GroundLocation
        Ground location to generate VTWS for.
    """
    # Celest stuff
    julian = Time(t / 86400, offset=jd_0)

    position = GCRS(julian.julian.data, y[:, 0], y[:, 1], y[:, 2], u.m)
    velocity = GCRS(julian.julian.data, y[:, 3], y[:, 4], y[:, 5], u.m / u.s)

    # pos_aa = Coordinate(position).convert_to("AzEl", toronto)
    # pos_itrs = Coordinate(position).convert_to(ITRS)

    # plot_from_array(t, pos_itrs.data)

    satellite = Satellite(position=position, velocity=velocity)

    for cutoff_angle in cutoff_angles:
        # Generate ground location windows.
        downlinking_windows = generate_vtws(
            satellite=satellite, location=location, vis_threshold=cutoff_angle
        )

        for idx, window in enumerate(downlinking_windows):
            rise_time = jd2000_to_datetime(window.rise_time)
            set_time = jd2000_to_datetime(window.set_time)

            duration = (set_time - rise_time).total_seconds()

            rise_str = rise_time.strftime("%Y-%m-%d %H:%M:%S")
            set_str = set_time.strftime("%Y-%m-%d %H:%M:%S")

            print(
                f"[{cutoff_angle:.2f} DEG] Encounter {idx}"
                f": {rise_str} to {set_str} ({duration:.2f} sec)"
            )
