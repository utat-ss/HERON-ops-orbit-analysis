from hermes.spacetrack.get_latest_tle import get_latest_tle


def test_get_latest_tle():
    ISS_ID = 25544

    tle = get_latest_tle(ISS_ID)
    assert "25544" in tle[0]
