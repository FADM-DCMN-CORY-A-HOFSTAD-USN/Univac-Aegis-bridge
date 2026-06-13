# File Name: inertial_dead_reckoning.py
# Location: /src/control_core/

import math
from typing import Dict

class InertialDeadReckoning:
    """
    FEATURES 1-15: INERTIAL NAVIGATION & DEAD RECKONING
    Calculates geographic displacement when GPS/GNSS networks are compromised.
    """
    def __init__(self):
        self.R_earth = 6371000.0  # Mean radius of Earth in meters
        self.omega_earth = 7.2921159e-5  # Earth angular velocity (rad/s)

    def feature_10_integrate_dr_position(self, current_lat: float, current_lon: float, 
                                         speed_ms: float, heading_rad: float, dt: float) -> tuple:
        """
        Integrates velocity vectors over the geoid to update the ship's coordinate.
        Assumes spherical Earth approximation for high-frequency (short dt) integration.
        """
        # Calculate displacement in meters (North/East)
        delta_north = speed_ms * math.cos(heading_rad) * dt
        delta_east = speed_ms * math.sin(heading_rad) * dt
        
        # Convert meter displacement to latitude/longitude radians
        delta_lat = delta_north / self.R_earth
        # Longitude scaling depends on the current latitude (lines converge at poles)
        # Prevent ZeroDivisionError singularity at the geographic poles
        cos_lat = max(0.0001, math.cos(current_lat))
        delta_lon = delta_east / (self.R_earth * cos_lat)
        
        new_lat = current_lat + delta_lat
        new_lon = current_lon + delta_lon
        return new_lat, new_lon

    def feature_12_set_and_drift_compensation(self, speed_ms: float, heading_rad: float, 
                                              current_velocity_ms: float, current_direction_rad: float) -> tuple:
        """
        Calculates the Course Made Good (CMG) and Speed Over Ground (SOG) 
        by vector-adding the ocean current (Set and Drift) to the ship's velocity.
        """
        ship_v_x = speed_ms * math.sin(heading_rad)
        ship_v_y = speed_ms * math.cos(heading_rad)
        
        current_v_x = current_velocity_ms * math.sin(current_direction_rad)
        current_v_y = current_velocity_ms * math.cos(current_direction_rad)
        
        sog_x = ship_v_x + current_v_x
        sog_y = ship_v_y + current_v_y
        
        sog = math.sqrt(sog_x**2 + sog_y**2)
        cmg = math.atan2(sog_x, sog_y)
        
        return sog, cmg

    def feature_14_navigational_coriolis_drift(self, speed_ms: float, latitude_rad: float) -> float:
        """
        Calculates the lateral drift force induced by the Earth's rotation.
        Returns the specific counter-rudder angle (in degrees) required to track straight.
        """
        # Coriolis Force = 2 * mass * velocity * omega * sin(lat)
        # We extract the acceleration term to find the necessary rudder offset
        coriolis_accel = 2.0 * speed_ms * self.omega_earth * math.sin(latitude_rad)
        
        # Convert lateral acceleration to a rudder angle offset (simplified hydrodynamic inverse)
        rudder_correction_rad = math.asin(coriolis_accel / 9.81) 
        return math.degrees(rudder_correction_rad)
