from hermes.tle import TLE
import pytest
import numpy as np


def test_tle_parsing():
    sample_tle = [
        "1 25544U 98067A   21035.51324206  .00001077  00000-0  27754-4 0  9998",
        "2 25544  51.6455 278.9410 0002184 336.6191  80.6984 15.48940116268036",
    ]

    tle = TLE.from_lines(*sample_tle)

    assert tle.norad == "25544"
    assert tle.epoch == pytest.approx(np.datetime64("2021-02-04T12:19:04.113984", "us"))


def test_tle_end_to_end():
    sample_tle = [
        "1 25544U 98067A   21035.51324206  .00001077  00000-0  27754-4 0  9998",
        "2 25544  51.6455 278.9410 0002184 336.6191  80.6984 15.48940116268036",
    ]

    tle = TLE.from_lines(*sample_tle)

    cart = tle.cartesian_state

    new_tle = TLE.from_cartesian_state(*cart, tle, 2021, 35.51324206)

    assert new_tle.tle_string == tuple(sample_tle)
