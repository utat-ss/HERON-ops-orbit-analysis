from celest import units as u
from celest.coordinates import GroundLocation

TORONTO_GS = toronto = GroundLocation(
    latitude=43.6532,
    longitude=-79.3832,
    height=76,
    angular_unit=u.deg,
    length_unit=u.m,
)

TORONTO_GS_OCCULSION_ANGLE = 45  # deg
GM = 3.986004418e14  # m^3/s^2
