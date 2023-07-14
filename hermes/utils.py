from datetime import datetime


def jd_0_from_epoch_ts(epoch_ts: str, calendar_year: int = 2023) -> float:
    """
    Get the JD2000 epoch from the timestamp in the HERON epoch.

    Parameters
    ----------
    epoch_ts : str
        Timestamp in the HERON epoch, in the format "day:hour:minute:second.microsecond".
    calendar_year : int, optional
        Calendar year of the HERON epoch, by default 2023

    Returns
    -------
    float
        JD2000 epoch

    Notes
    -----
    May not work for other calendar years (not validated)
    """
    dt = datetime.strptime(epoch_ts, "%j:%H:%M:%S.%f")
    day = (
        dt.toordinal()
        + dt.hour / 24
        + dt.minute / (24 * 60)
        + dt.second / 86400
        + dt.microsecond / 86400e6
    )
    day += 0.5  # 0.5d jd offset

    # calendar year offset
    day += 1766349 - (calendar_year - 2023) * 365

    return day
