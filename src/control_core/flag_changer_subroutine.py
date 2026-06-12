# File Name: flag_changer_subroutine.py
# Location: /src/control_core/
# Subsystem: Autonomous Electro-Mechanical Flag Changer Subroutine

import time
from typing import Dict, Any

class AutomaticFlagChangerSubroutine:
    def __init__(self):
        """
        Initializes the electro-mechanical flag actuator control matrix.
        Allowed Flag States:
            "ENSIGN"     (0x01) -> Standard National / Sovereign Identification
            "COMBAT"     (0x02) -> High-Visibility Battle Ensign (Triggered when weapons wake up)
            "RESTRICTED" (0x03) -> International Code / Restricted Maneuverability Flag Array
        """
        self.current_flag_state = "ENSIGN"
        self.last_transition_time = time.time()
        self.halyard_motor_position_pct = 0.0

    def evaluate_flag_logic_matrix(self, weapon_state: dict, telemetry: dict, transit_targets: dict) -> dict:
        """
        Processes real-time tracking rates, speed barriers, and control authority modes.
        Outputs exact motorized winch and lock commands for the physical flag mast.
        """
        current_time = time.time()
        
        # Ingest variables from high-speed data streams
        az_rate = abs(weapon_state.get('azimuth_rate_rads', 0.0))
        firing_active = weapon_state.get('bus_sync_active', False) or weapon_state.get('engagement_sequence_active', False)
        
        dist_to_bank = telemetry.get('distance_to_bank_meters', 100.0)
        shallow_slowdown = telemetry.get('shallow_water_slowdown_active', False)
        
        # Step 1: Evaluate Posture Gate Criteria
        weapons_are_active = (az_rate > 0.02) or firing_active
        is_maneuverability_restricted = (dist_to_bank < 20.0) or shallow_slowdown

        # Step 2: Resolve Target Flag State
        if weapons_are_active:
            target_state = "COMBAT"
            halyard_target_pct = 100.0  # Hoist Battle Ensign to mainyard apex
            action_description = "WEAPONS ENGAGED: Hoisting High-Visibility Battle Ensign."
        elif is_maneuverability_restricted:
            target_state = "RESTRICTED"
            halyard_target_pct = 50.0   # Position International Code flags at half-mast
            action_description = "RESTRICTED CHANNEL: Deploying international safety signaling codes."
        else:
            target_state = "ENSIGN"
            halyard_target_pct = 0.0    # Maintain nominal cruising ensign configuration
            action_description = "CRUISING PROFILE: Maintaining standard sovereign ensign."

        # Step 3: Handle On-The-Fly Transition Timing
        if self.current_flag_state != target_state:
            self.current_flag_state = target_state
            self.last_transition_time = current_time

        # Simulate electro-mechanical winch motor positioning lag
        error_pct = halyard_target_pct - self.halyard_motor_position_pct
        if abs(error_pct) > 0.1:
            self.halyard_motor_position_pct += error_pct * 0.1  # Servo velocity filter
            motor_moving_relay = 1
        else:
            self.halyard_motor_position_pct = halyard_target_pct
            motor_moving_relay = 0

        return {
            "active_flag_state_string": self.current_flag_state,
            "commanded_halyard_motor_position_pct": round(self.halyard_motor_position_pct, 1),
            "actuator_motor_power_relay": motor_moving_relay,
            "actuator_mechanical_lock_pin": 1 if motor_moving_relay == 0 else 0, # Pin locks when stopped
            "telemetry_flag_log_message": action_description
        }

# Verification and Diagnostic Validation Setup
if __name__ == "__main__":
    changer = AutomaticFlagChangerSubroutine()
    print("TESTING COGNITIVE FLAG CHANGER INTERLOCK LAWS:")
    print("=" * 75)
    
    # Test Scenario A: Cruising quietly in open waters
    mock_weapon_sleep = {'azimuth_rate_rads': 0.0, 'bus_sync_active': False}
    mock_telemetry_open = {'distance_to_bank_meters': 100.0, 'shallow_water_slowdown_active': False}
    out_a = changer.evaluate_flag_logic_matrix(mock_weapon_sleep, mock_telemetry_open, {})
    print(f"Scenario A -> State: {out_a['active_flag_state_string']} | Motor Target: {out_a['commanded_halyard_motor_position_pct']}%")
    
    # Test Scenario B: Weapons system suddenly awakens and tracks target
    mock_weapon_combat = {'azimuth_rate_rads': 0.12, 'bus_sync_active': True}
    out_b = changer.evaluate_flag_logic_matrix(mock_weapon_combat, mock_telemetry_open, {})
    print(f"Scenario B -> State: {out_b['active_flag_state_string']} | Motor Target: {out_b['commanded_halyard_motor_position_pct']}%")
