from celest.coordinates import GroundLocation
from celest import units as u

TORONTO_GS = toronto = GroundLocation(
    latitude=43.6532,
    longitude=-79.3832,
    height=76,
    angular_unit=u.deg,
    length_unit=u.m,
)

HERON_NORTH_OCCLUSION_ANGLE = 5  # deg
HERON_SOUTH_OCCLUSION_ANGLE = 55  # deg
