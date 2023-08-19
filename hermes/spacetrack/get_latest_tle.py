from spacetrack import SpaceTrackClient
from decouple import config


def get_latest_tle(satellite_id: int) -> tuple[str, str]:
    """
    Get the latest TLE for a given satellite ID.
    """

    identity = config("SPACETRACK_EMAIL")
    password = config("SPACETRACK_PASSWORD")

    st = SpaceTrackClient(identity=identity, password=password)

    # Note: this is being deprecated soon, find a workaround later using .gp
    raw_str: str = st.tle_latest(norad_cat_id=satellite_id, ordinal=1, format="tle")
    return raw_str.splitlines()
