from hermes.spacetrack.get_latest_tle import get_latest_tle

if __name__ == "__main__":
    ISS_ID = 25544

    tle = get_latest_tle(ISS_ID)
    print(tle)
