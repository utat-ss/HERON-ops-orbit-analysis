from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from .keplerian_orbit import KeplerianElements
from hermes.constants import GM


def _parse_decimal(s):
    """Parse a floating point with implicit leading dot.

    >>> _parse_decimal('378')
    0.378
    """
    return float("." + s)


def _parse_float(s):
    """Parse a floating point with implicit dot and exponential notation.

    >>> _parse_float(' 12345-3')
    0.00012345
    >>> _parse_float('+12345-3')
    0.00012345
    >>> _parse_float('-12345-3')
    -0.00012345
    """
    return float(s[0] + "." + s[1:6] + "e" + s[6:8])


@dataclass
class TLE:
    """Data class representing a single TLE.

    A two-line element set (TLE) is a data format encoding a list of orbital
    elements of an Earth-orbiting object for a given point in time, the epoch.

    All the attributes parsed from the TLE are expressed in the same units that
    are used in the TLE format.

    :ivar str norad:
        NORAD catalog number (https://en.wikipedia.org/wiki/Satellite_Catalog_Number).
    :ivar str classification:
        'U', 'C', 'S' for unclassified, classified, secret.
    :ivar str int_desig:
        International designator (https://en.wikipedia.org/wiki/International_Designator),
    :ivar int epoch_year:
        Year of the epoch.
    :ivar float epoch_day:
        Day of the year plus fraction of the day.
    :ivar float dn_o2:
        First time derivative of the mean motion divided by 2.
    :ivar float ddn_o6:
        Second time derivative of the mean motion divided by 6.
    :ivar float bstar:
        BSTAR coefficient (https://en.wikipedia.org/wiki/BSTAR).
    :ivar int set_num:
        Element set number.
    :ivar float inc:
        Inclination.
    :ivar float raan:
        Right ascension of the ascending node.
    :ivar float ecc:
        Eccentricity.
    :ivar float argp:
        Argument of perigee.
    :ivar float M:
        Mean anomaly.
    :ivar float n:
        Mean motion.
    :ivar int rev_num:
        Revolution number.
    """

    # NORAD catalog number (https://en.wikipedia.org/wiki/Satellite_Catalog_Number)
    norad: str
    classification: str
    int_desig: str
    epoch_year: int
    epoch_day: float
    dn_o2: float
    ddn_o6: float
    bstar: float
    set_num: int
    inc: float
    raan: float
    ecc: float
    argp: float
    M: float
    n: float
    rev_num: int

    @classmethod
    def from_lines(cls, line1: str, line2: str):
        """Parse a TLE from its constituent lines.

        All the attributes parsed from the TLE are expressed in the same units that
        are used in the TLE format.
        """
        proto_year = int(line1[18:20])
        actual_year = proto_year + 1900 if proto_year >= 57 else proto_year + 2000

        return cls(
            norad=line1[2:7],
            classification=line1[7],
            int_desig=line1[9:17],
            epoch_year=actual_year,
            epoch_day=float(line1[20:32]),
            dn_o2=float(line1[33:43]),
            ddn_o6=_parse_float(line1[44:52]),
            bstar=_parse_float(line1[53:61]),
            set_num=int(line1[64:68]),
            inc=float(line2[8:16]),
            raan=float(line2[17:25]),
            ecc=_parse_decimal(line2[26:33]),
            argp=float(line2[34:42]),
            M=float(line2[43:51]),
            n=float(line2[52:63]),
            rev_num=int(line2[63:68]),
        )

    @property
    def epoch(self) -> np.datetime64:
        """Epoch of the TLE, as an :class:`astropy.time.Time` object."""
        if not hasattr(self, "_epoch"):
            year = np.datetime64(self.epoch_year - 1970, "Y")
            day = np.timedelta64(int((self.epoch_day - 1) * 86400 * 10**6), "us")
            self._epoch = year + day
        return self._epoch

    @property
    def cartesian_state(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Current cartesian state of the satellite,
        in Earth-centered inertial frame, as m and m/s
        """
        # Get missing orbital elements
        a = (GM / (self.n * 2 * np.pi / 86400) ** 2) ** (1 / 3)

        keplerian_elements = KeplerianElements(
            a,
            self.ecc,
            np.deg2rad(self.inc),
            np.rad2deg(self.raan),
            np.deg2rad(self.argp),
            np.deg2rad(self.M),
        )

        return keplerian_elements.inertial_state()

    @property
    def tle_string(self) -> tuple[str, str]:
        epoch_yr = (
            self.epoch_year - 2000
            if self.epoch_year >= 2000
            else self.epoch_year - 1900
        )

        line_1 = f"""1 {self.norad}{self.classification} {self.int_desig} {epoch_yr}{self.epoch_day:012.8f}  .00000000  00000-0  {self.bstar:5.4e} 0    00"""
        line_2 = f"""2 {self.norad} {self.inc:8.4f} {self.raan:8.4f} {self.ecc:7.7f} {self.argp:8.4f} {self.M:8.4f} {self.n:11.8f}{self.rev_num:5d}0"""
        return line_1, line_2

    @classmethod
    def from_cartesian_state(
        cls,
        r_eci: np.ndarray,
        v_eci: np.ndarray,
        dummy_tle: TLE,
        epoch_yr: int,
        epoch_day_frac: float,
    ):
        """
        Create a TLE with the same information as the dummy_tle, but with orbital
        elements corresponding to the cartesian state r_eci, v_eci

        Parameters
        ----------
        r_eci : np.ndarray
            Position vector in ECI frame, in meters
        v_eci : np.ndarray
            Velocity vector in ECI frame, in meters per second
        dummy_tle : TLE
            TLE with the same norad id as the satellite
        epoch_yr : int
            Year of the epoch (last two digits; 57 is 1957, 20 is 2020)
        epoch_day_frac : float
            Day of the year plus fraction of the day
        """
        ke = KeplerianElements.from_cartesian(r_eci, v_eci)

        return cls(
            norad=dummy_tle.norad,
            classification=dummy_tle.classification,
            int_desig=dummy_tle.int_desig,
            epoch_year=epoch_yr,
            epoch_day=epoch_day_frac,
            dn_o2=dummy_tle.dn_o2,
            ddn_o6=dummy_tle.ddn_o6,
            bstar=dummy_tle.bstar,
            set_num=dummy_tle.set_num,
            inc=np.rad2deg(ke.i),
            raan=np.rad2deg(ke.raan),
            ecc=ke.e,
            argp=np.rad2deg(ke.argp),
            M=np.rad2deg(ke.M),
            n=ke.mean_motion,
            rev_num=dummy_tle.rev_num,
        )
