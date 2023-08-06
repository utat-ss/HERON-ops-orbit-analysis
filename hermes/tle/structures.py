from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np
from trajectorize._c_extension import lib
from trajectorize.orbit.conic_kepler import KeplerianElements, KeplerianOrbit

from hermes.constants import GM
from .converters import (
    line_checksum,
    parse_decimal,
    parse_float,
    print_decimal,
    print_float,
)

EARTH = SimpleNamespace(mu=GM)


@dataclass
class TLE:
    """Data class representing a single TLE.

    A two-line element set (TLE) is a data format encoding a list of orbital
    elements of an Earth-orbiting object for a given point in time, the epoch.

    All the attributes parsed from the TLE are expressed in the same units that
    are used in the TLE format.
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
            ddn_o6=parse_float(line1[44:52]),
            bstar=parse_float(line1[53:61]),
            set_num=int(line1[64:68]),
            inc=float(line2[8:16]),
            raan=float(line2[17:25]),
            ecc=parse_decimal(line2[26:33]),
            argp=float(line2[34:42]),
            M=float(line2[43:51]),
            n=float(line2[52:63]),
            rev_num=int(line2[63:68]),
        )

    @property
    def epoch(self) -> np.datetime64:
        """Epoch of the TLE, as a numpy datetime64 object."""
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
        true_anomaly = lib.theta_from_M(np.deg2rad(self.M), self.ecc)

        keplerian_elements = KeplerianElements(
            semi_major_axis=a,
            eccentricity=self.ecc,
            inclination=np.deg2rad(self.inc),
            longitude_of_ascending_node=np.deg2rad(self.raan),
            argument_of_periapsis=np.deg2rad(self.argp),
            true_anomaly=true_anomaly,
            epoch=0,
        )
        orbit = KeplerianOrbit(keplerian_elements, EARTH)

        sv = orbit.state_vector

        return (sv.position, sv.velocity)

    @property
    def tle_string(self) -> tuple[str, str]:
        epoch_yr = (
            self.epoch_year - 2000
            if self.epoch_year >= 2000
            else self.epoch_year - 1900
        )

        line_1 = f"""1 {self.norad}{self.classification} {self.int_desig} {epoch_yr}{self.epoch_day:012.8f}  {f'{self.dn_o2:.8f}'[1:]}  {print_float(self.ddn_o6)}  {print_float(self.bstar)} 0  {self.set_num}"""
        line_2 = f"""2 {self.norad} {self.inc:8.4f} {self.raan:8.4f} {print_decimal(self.ecc)} {self.argp:8.4f} {self.M:8.4f} {self.n:11.8f}{self.rev_num:5d}"""

        # compute checksums
        line_1 += str(line_checksum(line_1))
        line_2 += str(line_checksum(line_2))

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
        orbit = KeplerianOrbit.from_state_vector(r_eci, v_eci, 0, EARTH)
        ke = orbit.ke

        mean_motion = 86400 / orbit.T

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
            inc=np.rad2deg(ke.inclination),
            raan=np.rad2deg(ke.longitude_of_ascending_node),
            ecc=ke.eccentricity,
            argp=np.rad2deg(ke.argument_of_periapsis),
            M=np.rad2deg(lib.M_from_theta(ke.true_anomaly, ke.eccentricity)),
            n=mean_motion,
            rev_num=dummy_tle.rev_num,
        )

    @classmethod
    def null_tle(cls):
        """
        TLE filled with null values, can be used as a dummy TLE
        """
        return cls(
            norad="00000",
            classification="U",
            int_desig="        ",
            epoch_year=0,
            epoch_day=0,
            dn_o2=0,
            ddn_o6=0,
            bstar=0,
            set_num=0,
            inc=0,
            raan=0,
            ecc=0,
            argp=0,
            M=0,
            n=0,
            rev_num=0,
        )
