from __future__ import annotations

from supernova.api import propagate_orbit
from hermes.celest_helpers import ecef_to_eci, jd2000_to_datetime, process_encounters
from celest import units as u
import numpy as np
from hermes.utils import jd_0_from_epoch_ts
from supernova.plotter import plot_from_array, plot_3d_from_array


# MISSION PARAMS
HERON_Y0_ECEF = np.array(
    [+4459305.633, +4513784.109, -2669611.145, +3146.340, +1002.139, +6943.597]
)
EPOCH_TIMESTAMP = "274:06:42:23.371"  # relative to 2023


if __name__ == "__main__":
    days = 50
    jd_0 = jd_0_from_epoch_ts(EPOCH_TIMESTAMP)
    print(f"Using epoch {jd2000_to_datetime(u.Quantity(jd_0, u.jd2000))}")

    t_span = [0, 86400 * days]
    y0 = ecef_to_eci(HERON_Y0_ECEF, jd_0).tolist()

    t, y = propagate_orbit("RK810", "simplified", t_span, y0, 1e-6)

    print(f"Steps taken: {len(t)}")

    process_encounters(t, y, jd_0)

    plot_from_array(t, y)
    plot_3d_from_array(t, y, 3)
