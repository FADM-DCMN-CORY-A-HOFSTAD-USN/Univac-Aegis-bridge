# File Name: univac_features_library.py
# Location: /src/control_core/

import math
import numpy as np

class NAVMOD_Subsystem:
    """Features 1 - 15: Navigation & Geodetic Matrix Modifiers"""
    def __init__(self):
        self.R = 6371000.0 # Earth radius in meters
        self.a = 6378137.0 # WGS-84 semi-major axis
        self.b = 6356752.3 # WGS-84 semi-minor axis
        
    def execute_all(self, targets: dict, telemetry: dict) -> dict:
        speed = telemetry['speed_ms']
        yaw_rate = telemetry['yaw_rate_rads']
        roll = telemetry['roll_angle_rad']
        
        # Feature 14: Turn-Radius Centrifugal Offset
        r_turn = (speed**2) / (9.81 * math.tan(roll)) if abs(roll) > 0.05 else 9999.0
        
        # Feature 13: Crab Angle Correction Factor
        # Simulates environmental sliding angles relative to track
        crab_angle = math.asin(min(1.0, max(-1.0, (speed * 0.05) / max(1.0, speed))))
        
        return {
            "turn_radius_meters": r_turn,
            "crab_angle_rad": crab_angle,
            "heading_filtered_rad": telemetry['yaw_rate_rads'] * 0.95 # Feature 15
        }

class HYDRO_Subsystem:
    """Features 16 - 35: Hydrodynamic & Shallow-Water Constraints"""
    def __init__(self, draft, length, beam):
        self.T = draft
        self.L = length
        self.B = beam
        self.rho = 1025.0
        
    def execute_all(self, telemetry: dict) -> dict:
        h = telemetry['depth']
        V = telemetry['speed_ms']
        clearance = max(0.1, h - self.T)
        clearance_ratio = clearance / self.T
        
        # Feature 16: Squat Maximum Sinkage Estimator (Block Coefficient = 0.7)
        squat = 0.7 * ((V / 10.0) ** 2) * (1.0 + 0.1 * (self.T / clearance))
        
        # Feature 17: Shallow Water Resistance Multiplier
        r_shallow_mult = 1.0 / math.sqrt(max(0.01, 1.0 - (self.T / h)**2)) if h > self.T else 5.0
        
        # Feature 20: Critical Velocity Threshold (Froude Depth Number)
        fr_depth = V / math.sqrt(9.81 * h) if h > 0 else 0
        
        # Feature 26 & 27: Bank Suction & Cushion Estimator Models
        # Calculates lateral force factors if within 25 meters of a bank drop-off
        dist_bank = telemetry.get('distance_to_bank_meters', 50.0)
        y_bank = 0.5 * self.rho * (V**2) * self.L * self.T * (1.0 / max(1.0, dist_bank))
        
        # Feature 33 & 34: Rolling/Pitch Draft Expansion Formulas
        dt_roll = self.B * math.sin(telemetry['roll_angle_rad'])
        
        return {
            "predicted_squat_meters": squat,
            "shallow_resistance_factor": r_shallow_mult,
            "froude_depth_number": fr_depth,
            "bank_suction_force_n": Y_bank if dist_bank < 25.0 else 0.0,
            "dynamic_draft_meters": self.T + squat + abs(dt_roll)
        }

class WAVEMOD_Subsystem:
    """Features 36 - 55: Seakeeping & Autoregressive Wave Predictors"""
    def __init__(self, diameter):
        self.D = diameter
        self.ar_weights = np.array([0.842, -0.441, 0.198, -0.048, 0.009])
        self.elevation_history = [0.0] * 5
        
    def execute_all(self, telemetry: dict) -> dict:
        raw_bow = telemetry['bow_sensor_meters']
        V = telemetry['speed_ms']
        
        # Feature 40: Autoregressive Prediction Filter
        self.elevation_history.pop(0)
        self.elevation_history.append(raw_bow)
        pred_elevation = float(np.dot(self.ar_weights, self.elevation_history))
        
        # Feature 41: Propeller Ventilation Condition (Shaft Line at 3.5m nominal)
        submergence = 3.5 + pred_elevation
        if submergence >= self.D:
            beta_v = 1.0
        elif submergence <= 0:
            beta_v = 0.05
        else:
            beta_v = math.sin((math.pi / 2.0) * (submergence / self.D)) ** 2
            
        # Feature 37: Encounter Frequency Tuning (Wave frequency approx 0.85 rad/s)
        w_wave = 0.85
        k = (w_wave ** 2) / 9.81 # Feature 36: Wave Number
        w_encounter = w_wave + k * V # Assumes head seas profile
        
        # Feature 47: Parametric Rolling Resonance Identifier
        # Alert if wave frequency matches twice the hull's natural roll cycle
        parametric_risk = True if abs(w_encounter - 1.4) < 0.15 else False
        
        return {
            "predicted_stern_elevation": pred_elevation,
            "ventilation_factor_beta": beta_v,
            "encounter_frequency_rads": w_encounter,
            "parametric_roll_risk": parametric_risk
        }

class MIMOMOD_Subsystem:
    """Features 56 - 75: Rudder Roll Stabilization & Structural Interlocking"""
    def __init__(self, inertia_prop, diameter):
        self.J_prop = inertia_prop
        self.D = diameter
        self.rho = 1025.0
        self.K_bend = 0.012
        
    def execute_all(self, targets: dict, telemetry: dict, omega: float) -> dict:
        yaw_rate = telemetry['yaw_rate_rads']
        abs_omega = abs(omega)
        
        # Feature 60: Propeller Asymmetric Bending Moment
        m_bend = self.K_bend * self.rho * (omega**2) * (self.D**5) * yaw_rate
        
        # Feature 61: Gyroscopic Precession Torque
        m_gyro = self.J_prop * omega * yaw_rate
        
        # Feature 62: Safe Maneuvering Envelope Cap Matrix Calculation
        m_total_structural = abs(m_bend) + abs(m_gyro)
        m_allowable = 1500000.0 / 2.5 # 1.5M Nm Yield with 2.5x safety interlock
        
        # Feature 65: Speed-Dependent Rudder Angle Saturation
        max_rudder_allowed = 35.0 * math.exp(-0.015 * abs_omega)
        
        return {
            "structural_moment_total_nm": m_total_structural,
            "structural_yield_percentage": (m_total_structural / m_allowable) * 100.0,
            "clamped_rudder_boundary_deg": max_rudder_allowed
        }
