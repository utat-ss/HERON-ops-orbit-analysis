from __future__ import annotations

import numpy as np
from supernova.plotter import plot_3d_from_array, plot_from_array

from hermes.celest_helpers import process_encounters
from hermes.copropagation import propagate_from_sv_and_timestamp
from hermes.utils import jd_0_from_epoch_ts

# MISSION PARAMS
HERON_Y0_ECEF = np.array(
    [+4459305.633, +4513784.109, -2669611.145, +3146.340, +1002.139, +6943.597]
)
EPOCH_TIMESTAMP = "274:06:42:23.371"  # relative to 2023


if __name__ == "__main__":
    # Epoch
    days_to_run = 50

    ((initial_tle, final_tle), (t, y)) = propagate_from_sv_and_timestamp(
        HERON_Y0_ECEF, EPOCH_TIMESTAMP, 2023, days_to_run
    )

    print("Initial TLE:", initial_tle.tle_string)
    print(f"Steps taken: {len(t)}")
    print("Final TLE:", final_tle.tle_string)

    # Analysis and plotting
    jd_0 = jd_0_from_epoch_ts(EPOCH_TIMESTAMP, 2023)
    process_encounters(t, y, jd_0)
    plot_from_array(t, y)
    plot_3d_from_array(t, y, 3)
