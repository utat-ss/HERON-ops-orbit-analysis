from dataclasses import dataclass
import numpy as np
from hermes.constants import GM


@dataclass
class KeplerianElements:
    # Keplerian elements derived from TLEs, USE RADIANS
    a: float  # semi-major axis
    e: float  # eccentricity
    i: float  # inclination
    raan: float  # right ascension of the ascending node
    argp: float  # argument of perigee
    M: float  # mean anomaly

    @property
    def eccentric_anomaly(self) -> float:
        # rootfind to get eccentric anomaly
        E = self.M + self.e * np.sin(self.M) / (
            1 - np.sin(self.M + self.e) + np.sin(self.M)
        )

        # Halley's method, cubic convergence
        for _ in range(100):
            f = E - self.e * np.sin(E) - self.M
            f_prime = 1 - self.e * np.cos(E)
            f_prime_prime = self.e * np.sin(E)
            delta = -2 * f * f_prime / (2 * f_prime * f_prime - f * f_prime_prime)
            E += delta
            if abs(delta) < 1e-12:
                return E
        raise RuntimeError("Failed to converge on eccentric anomaly")

    @property
    def true_anomaly(self) -> float:
        # true anomaly from eccentric anomaly
        return 2 * np.arctan(
            np.sqrt((1 + self.e) / (1 - self.e)) * np.tan(self.eccentric_anomaly / 2)
        )

    @property
    def rotation_eci_perifocal(self) -> np.ndarray:
        """
        Rotation matrix which rotates vectors from the perifocal frame to the
        ECI frame.
        """
        return self.rotation_perifocal_eci.T

    @property
    def rotation_perifocal_eci(self) -> np.ndarray:
        """
        Rotation matrix which rotates vectors from the ECI frame to the
        perifocal frame.
        """
        return np.array(
            [
                [
                    np.cos(self.raan) * np.cos(self.argp)
                    - np.sin(self.raan) * np.sin(self.argp) * np.cos(self.i),
                    -np.cos(self.raan) * np.sin(self.argp)
                    - np.sin(self.raan) * np.cos(self.argp) * np.cos(self.i),
                    np.sin(self.raan) * np.sin(self.i),
                ],
                [
                    np.sin(self.raan) * np.cos(self.argp)
                    + np.cos(self.raan) * np.sin(self.argp) * np.cos(self.i),
                    -np.sin(self.raan) * np.sin(self.argp)
                    + np.cos(self.raan) * np.cos(self.argp) * np.cos(self.i),
                    -np.cos(self.raan) * np.sin(self.i),
                ],
                [
                    np.sin(self.argp) * np.sin(self.i),
                    np.cos(self.argp) * np.sin(self.i),
                    np.cos(self.i),
                ],
            ]
        )

    def inertial_state(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Gets inertial state of the orbit at the current mean anomaly
        """
        # get position in perifocal frame
        r = self.a * (1 - self.e**2) / (1 + self.e * np.cos(self.true_anomaly))
        h = np.sqrt(GM * self.a * (1 - self.e**2))

        r_perifocal = np.array(
            [
                r * np.cos(self.true_anomaly),
                r * np.sin(self.true_anomaly),
                0,
            ]
        )
        v_x = h * self.e * np.sin(self.true_anomaly) / r
        v_y = h * (1 + self.e * np.cos(self.true_anomaly)) / r

        v_perifocal = np.array([v_x, v_y, 0])

        r_eci = self.rotation_eci_perifocal @ r_perifocal
        v_eci = self.rotation_eci_perifocal @ v_perifocal

        return r_eci, v_eci

    @classmethod
    def from_cartesian(cls, r_eci: np.ndarray, v_eci: np.ndarray):
        h = np.cross(r_eci, v_eci)

        r = np.linalg.norm(r_eci)
        v = np.linalg.norm(v_eci)

        a = 1 / (2 / r - v**2 / GM)

        e_vec = (v**2 - GM / r) * r_eci / GM - np.dot(r_eci, v_eci) * v_eci / GM

        e = np.linalg.norm(e_vec)

        n_vec = np.cross(np.array([0, 0, 1]), h)
        n = np.linalg.norm(n_vec)

        i = np.arccos(h[2] / np.linalg.norm(h))

        raan = np.arccos(n_vec[0] / n)

        if n_vec[1] < 0:
            raan = 2 * np.pi - raan

        argp = np.arccos(np.dot(n_vec, e_vec) / (n * e))
        if e_vec[2] < 0:
            argp = 2 * np.pi - argp

        E = np.arccos((1 - r / a) / e)

        if np.dot(r_eci, v_eci) < 0:
            E = 2 * np.pi - E

        M = E - e * np.sin(E)

        return cls(a, e, i, raan, argp, M)

    @property
    def mean_motion(self) -> float:
        # in revs per day
        # calculate period
        T = 2 * np.pi * np.sqrt(self.a**3 / GM)
        return 86400 / T
